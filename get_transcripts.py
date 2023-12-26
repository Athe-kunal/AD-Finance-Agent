import torch
from transformers import pipeline
import transformers
import os
from config import *
from tqdm import tqdm
import json
import wandb
import re 

assert int(torch.__version__[0])>=2, "Please ensure that the torch version is above 2 to use better transformers"


def generate_transcripts(output_folder:str,idx:int=0):
    wandb.login(key=WANDB_API_KEY)
    run = wandb.init(project=WANDB_PROJECT,config={"source":"YouTube Video","data":output_folder},entity=WANDB_ENTITY,group=output_folder)

    pipe = pipeline("automatic-speech-recognition",
                "openai/whisper-large-v3",
                torch_dtype=torch.bfloat16,
                device="cuda:0")
    artifact = wandb.Artifact(name=output_folder+"_data", type="dataset")
    json_folder_name = output_folder+"_TRANSCRIPTS"
    os.makedirs(json_folder_name,exist_ok=True)
    for audio_files in tqdm(os.listdir(output_folder)[idx:]):
        print(f"Generating transcripts for {audio_files}")
        title = audio_files.split(".mp3")[0]
        relative_audio_path_mp3 = os.path.join(output_folder,audio_files)
        outputs = pipe(relative_audio_path_mp3,
                chunk_length_s=WHISPHER_CHUNK_LENGTH,
                batch_size=WHISPHER_BATCH_SIZE,
                return_timestamps=True)
        relative_audio_path_json = json_folder_name + "/" + title + ".json"
        with open(relative_audio_path_json, 'w') as fp:
            json.dump(outputs, fp)
        artifact.add_file(local_path=relative_audio_path_json,name=f"{title}_transcript.json")
        artifact.add_file(local_path=relative_audio_path_mp3)
        # artifact.add_file(local_path=relative_audio_path_mp3)
        # run.
        run.log_artifact(artifact)

    del pipe
    torch.cuda.empty_cache()
        