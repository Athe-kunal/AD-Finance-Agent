from transformers import AutoModelForCausalLM,AutoTokenizer,TrainingArguments,Trainer
from datasets import load_dataset
from transformers import DataCollatorForLanguageModeling
from ruamel.yaml import YAML
import torch

def preprocess_text(example,tokenizer):
    return tokenizer(example['text'])



def chunk_data(examples,block_size):
    #print(type(examples['input_ids']))
    
    concatenated_examples = {k: sum(examples[k], []) for k in examples.keys()}
    
    total_length = len(concatenated_examples['input_ids'])
    
    if total_length >= block_size:
        total_length = (total_length // block_size) * block_size
   
    result = {
        k: [t[i : i + block_size] for i in range(0, total_length, block_size)]
        for k,t in concatenated_examples.items()
    }
    result['labels'] = result['input_ids'].copy()
   
    return result


if __name__=="__main__":
    # block_size=512
    yaml = YAML(typ='rt')
    with open('config/finetuning_config.yaml',"r") as f:
         config = yaml.load(f)
    
    
    tokenizer = AutoTokenizer.from_pretrained(config['model_name'])
    tokenizer.pad_token = tokenizer.eos_token
    data = load_dataset("text",data_files={"train":"src/data/transcript_files/book_*.txt","test":["src/data/transcript_files/mba_transcript_file.txt",
                                                                        "src/data/transcript_files/undergrad_transcript_file.txt"]})
    
    tokenized_data = data.map(preprocess_text,
                              fn_kwargs={'tokenizer':tokenizer},
                              remove_columns=data['train'].column_names)
    lm_dataset = tokenized_data.map(chunk_data,batched=True,
                                    fn_kwargs={'block_size':512},
                                    remove_columns=tokenized_data['train'].column_names)
    
    # data_collator = DataCollatorForLanguageModeling(tokenizer=tokenizer, mlm=False)

    # model = AutoModelForCausalLM.from_pretrained(config["model_name"])

    # if torch.cuda.is_available():
    #     model.cuda()
    
    # training_args = TrainingArguments(**config["train_args"])

    # trainer = Trainer(
    #     model=model,
    #     args=training_args,
    #     train_dataset=lm_dataset["train"],
    #     data_collator=data_collator,
    #     tokenizer=tokenizer
        
    # )

    # trainer.train()

    # ### Inference ###
    # prompt = 'How I think you can value a company like tesla'
    # input_dict = tokenizer(prompt,return_tensors='pt')
    # inputs = input_dict.input_ids
    # attn = input_dict.attention_mask
    # op = model.generate(inputs.cuda(),max_new_tokens=100, do_sample=True, top_k=10, top_p=0.95,attention_mask=attn.cuda())
    # tokenizer.batch_decode(op, skip_special_tokens=True)