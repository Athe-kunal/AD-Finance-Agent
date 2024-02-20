import json
import os

parent_directory = os.path.dirname(os.path.abspath(__file__))
src_folder = os.path.join(parent_directory, 'src')
artifacts_folder = os.path.join(parent_directory, 'artifacts', 'YouTube_API_Transcripts')

# Specify the file path
file_path1 = f'{artifacts_folder}/transcripts_MBA.json'
file_path2 = f'{artifacts_folder}/transcripts_undergrad.json'

# Read JSON data from the file
with open(file_path1, 'r') as file:
    mba_json = json.load(file)

with open(file_path2, 'r') as file:
    undergrad_json = json.load(file)
    
def chunking(json_data,chunk_size):
  all_chunks = {}
  current_chunk_text = ""  
  current_chunk_start_time = None  
  keys = json_data.keys()
  for k in keys:
    transcript_chunks = [] 
    for item in json_data[k]:

        text = item['text']
        start_time = item['start']
      

        # Check if adding the current text will exceed 512 characters
        if len(current_chunk_text) + len(text) <= chunk_size:
            current_chunk_text += " "+text
            if current_chunk_start_time is None:
                current_chunk_start_time = start_time
        else:
            transcript_chunks.append({'text': current_chunk_text.strip(), 'start_time': current_chunk_start_time})
            current_chunk_text = text
            current_chunk_start_time = start_time

    if current_chunk_text:
        transcript_chunks.append({'text': current_chunk_text, 'start_time': current_chunk_start_time})
    all_chunks[k] = transcript_chunks
  
  return all_chunks

final_json_undergrad = chunking(undergrad_json,512)
final_json_mba = chunking(mba_json,512)

with open(f"{artifacts_folder}/chunked_transcripts_mba.json", 'w') as file:
    json.dump(final_json_mba,file,indent=4)
    
with open(f"{artifacts_folder}/chunked_transcripts_undergrad.json", 'w') as file:
    json.dump(final_json_undergrad,file,indent=4)
