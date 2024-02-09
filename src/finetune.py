import json
import re
import os
from datasets import Dataset
import torch
from transformers import get_linear_schedule_with_warmup
from torch.utils.data import (
    Dataset,
    DataLoader,
    random_split,
    RandomSampler,
    SequentialSampler,
)
from torch.optim import AdamW
from transformers import PhiForCausalLM, AutoTokenizer
import random
import numpy as np
import datetime
import time
import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd

os.chdir("..")

def preprocessing_func(path):
    with open(path) as f:
        d = json.load(f)
        text = d["text"]
    sentence_list = text.split(". ")
    preprocessed_sentence_list = []
    for idx, sent in enumerate(sentence_list):
        if idx < len(sentence_list) - 1:
            if sent == sentence_list[idx + 1]:
                continue
        num_words = len(sent.split(" "))
        if num_words <= 5:
            continue
        sent = re.sub(r"[^\x00-\x7F]+", "", sent)
        sent = sent.strip()
        preprocessed_sentence_list.append(sent)
    return preprocessed_sentence_list


def get_data():
    path = "artifacts"

    all_texts_list = []
    for data in os.listdir(path):
        curr_path = os.path.join(path, data)
        curr_path = os.path.join(curr_path, "TRANSCRIPTS")
        for transcripts_json_file in os.listdir(curr_path):
            json_file_path = os.path.join(curr_path, transcripts_json_file)
            preprocessed_sent = preprocessing_func(json_file_path)
            all_texts_list.extend(preprocessed_sent)

    return all_texts_list



if __name__ == "__main__":
    all_texts_list = get_data()
    batch_size = 4
    epochs = 10
    learning_rate = 5e-4
    warmup_steps = 1e2
    epsilon = 1e-8

    # this produces sample output every 100 steps
    sample_every = 100

    class CausalLMDataset(Dataset):
        def __init__(self, txt_list, tokenizer, max_length=768):
            self.tokenizer = tokenizer
            self.input_ids = []
            self.attn_masks = []

            for txt in txt_list:
                encodings_dict = tokenizer(
                    txt,
                    truncation=True,
                    max_length=max_length,
                    padding="max_length",
                )

                self.input_ids.append(torch.tensor(encodings_dict["input_ids"]))
                self.attn_masks.append(torch.tensor(encodings_dict["attention_mask"]))

        def __len__(self):
            return len(self.input_ids)

        def __getitem__(self, idx):
            return self.input_ids[idx], self.attn_masks[idx]

    # define the model and tokenizer and push the model and tokens to the GPU.
    model = PhiForCausalLM.from_pretrained(
        "microsoft/phi-1_5",
        torch_dtype=torch.float16,
        # attn_implementation="flash_attention_2",
        # bos_token="<|startoftext|>",
        # eos_token="<|endoftext|>",
        # pad_token="<|pad|>",
    )
    tokenizer = AutoTokenizer.from_pretrained("microsoft/phi-1_5")
    tokenizer.add_special_tokens({'pad_token': '[PAD]'})
    model.resize_token_embeddings(len(tokenizer))
    model.to("cuda")
    dataset = CausalLMDataset(all_texts_list, tokenizer, max_length=768)

    # Split into training and validation sets
    train_size = int(0.9 * len(dataset))
    val_size = len(dataset) - train_size

    train_dataset, val_dataset = random_split(dataset, [train_size, val_size])
    # Create the DataLoaders for our training and validation datasets.
    # We'll take training samples in random order.
    train_dataloader = DataLoader(
        train_dataset,  # The training samples.
        sampler=RandomSampler(train_dataset),  # Select batches randomly
        batch_size=batch_size,  # Trains with this batch size.
    )

    # For validation the order doesn't matter, so we'll just read them sequentially.
    validation_dataloader = DataLoader(
        val_dataset,  # The validation samples.
        sampler=SequentialSampler(val_dataset),  # Pull out batches sequentially.
        batch_size=batch_size,  # Evaluate with this batch size.
    )

    seed_val = 42

    random.seed(seed_val)
    np.random.seed(seed_val)
    torch.manual_seed(seed_val)
    torch.cuda.manual_seed_all(seed_val)

    optimizer = AdamW(model.parameters(), lr=learning_rate, eps=epsilon)
    # Total number of training steps is [number of batches] x [number of epochs].
    # (Note that this is not the same as the number of training samples).
    total_steps = len(train_dataloader) * epochs

    # Create the learning rate scheduler.
    # This changes the learning rate as the training loop progresses
    scheduler = get_linear_schedule_with_warmup(
        optimizer, num_warmup_steps=warmup_steps, num_training_steps=total_steps
    )

    def format_time(elapsed):
        return str(datetime.timedelta(seconds=int(round((elapsed)))))

    total_t0 = time.time()
    device = "cuda"
    training_stats = []

    for epoch_i in range(0, epochs):
        # ========================================
        #               Training
        # ========================================

        print("")
        print("======== Epoch {:} / {:} ========".format(epoch_i + 1, epochs))
        print("Training...")

        t0 = time.time()

        total_train_loss = 0

        model.train()

        for step, batch in enumerate(train_dataloader):
            b_input_ids = batch[0].to(device)
            b_labels = batch[0].to(device)
            b_masks = batch[1].to(device)

            model.zero_grad()

            outputs = model(
                b_input_ids,
                labels=b_labels,
                attention_mask=b_masks,
                # token_type_ids=None,
            )

            loss = outputs[0]

            batch_loss = loss.item()
            total_train_loss += batch_loss

            # Get sample every x batches.
            if step % sample_every == 0 and not step == 0:
                elapsed = format_time(time.time() - t0)
                print(
                    "  Batch {:>5,}  of  {:>5,}. Loss: {:>5,}.   Elapsed: {:}.".format(
                        step, len(train_dataloader), batch_loss, elapsed
                    )
                )

                model.eval()

                sample_outputs = model.generate(
                    bos_token_id=random.randint(1, 30000),
                    do_sample=True,
                    top_k=50,
                    max_length=200,
                    top_p=0.95,
                    num_return_sequences=1,
                )
                for i, sample_output in enumerate(sample_outputs):
                    print(
                        "{}: {}".format(
                            i, tokenizer.decode(sample_output, skip_special_tokens=True)
                        )
                    )

                model.train()

            loss.backward()

            optimizer.step()

            scheduler.step()

        # Calculate the average loss over all of the batches.
        avg_train_loss = total_train_loss / len(train_dataloader)

        # Measure how long this epoch took.
        training_time = format_time(time.time() - t0)

        print("")
        print("  Average training loss: {0:.2f}".format(avg_train_loss))
        print("  Training epoch took: {:}".format(training_time))

        # ========================================
        #               Validation
        # ========================================

        print("")
        print("Running Validation...")

        t0 = time.time()

        model.eval()

        total_eval_loss = 0
        nb_eval_steps = 0

        # Evaluate data for one epoch
        for batch in validation_dataloader:
            b_input_ids = batch[0].to(device)
            b_labels = batch[0].to(device)
            b_masks = batch[1].to(device)

            with torch.no_grad():
                outputs = model(
                    b_input_ids,
                    #                            token_type_ids=None,
                    attention_mask=b_masks,
                    labels=b_labels,
                )

                loss = outputs[0]

            batch_loss = loss.item()
            total_eval_loss += batch_loss

        avg_val_loss = total_eval_loss / len(validation_dataloader)

        validation_time = format_time(time.time() - t0)

        print("  Validation Loss: {0:.2f}".format(avg_val_loss))
        print("  Validation took: {:}".format(validation_time))

        # Record all statistics from this epoch.
        training_stats.append(
            {
                "epoch": epoch_i + 1,
                "Training Loss": avg_train_loss,
                "Valid. Loss": avg_val_loss,
                "Training Time": training_time,
                "Validation Time": validation_time,
            }
        )

    print("")
    print("Training complete!")
    print(
        "Total training took {:} (h:mm:ss)".format(format_time(time.time() - total_t0))
    )

    # Create a DataFrame from our training statistics.
    df_stats = pd.DataFrame(data=training_stats)

    # Use the 'epoch' as the row index.
    df_stats = df_stats.set_index("epoch")
    # Use plot styling from seaborn.
    sns.set(style="darkgrid")

    # Increase the plot size and font size.
    sns.set(font_scale=1.5)
    plt.rcParams["figure.figsize"] = (12, 6)

    # Plot the learning curve.
    plt.plot(df_stats["Training Loss"], "b-o", label="Training")
    plt.plot(df_stats["Valid. Loss"], "g-o", label="Validation")

    # Label the plot.
    plt.title("Training & Validation Loss")
    plt.xlabel("Epoch")
    plt.ylabel("Loss")
    plt.legend()
    plt.xticks([1, 2, 3, 4])

    plt.show()

    model.eval()

    prompt = "First steps on valuing a company "

    generated = torch.tensor(tokenizer.encode(prompt)).unsqueeze(0)
    generated = generated.to(device)

    print(generated)

    sample_outputs = model.generate(
        generated,
        # bos_token_id=random.randint(1,30000),
        do_sample=True,
        top_k=10,
        max_length=100,
        top_p=0.95,
        num_return_sequences=3,
        # repetition_penalty = 0.9,
        # num_beams = 10
    )

    for i, sample_output in enumerate(sample_outputs):
        print(
            "{}: {}\n\n".format(
                i, tokenizer.decode(sample_output, skip_special_tokens=True)
            )
        )
