import json
import os

parent_directory = os.path.dirname(os.path.abspath(__file__))
parent_directory = parent_directory.replace('src', '')
src_folder = parent_directory + 'src'
artifacts_folder = parent_directory + 'artifacts/YouTube_API_Transcripts/'

# Specify the file paths
file_path1 = f'{artifacts_folder}transcripts_MBA.json'
file_path2 = f'{artifacts_folder}transcripts_undergrad.json'
file_path3 = f'{artifacts_folder}misc_transcripts.json'

# Read JSON data from the files
with open(file_path1, 'r') as file:
    mba_json = json.load(file)

with open(file_path2, 'r') as file:
    undergrad_json = json.load(file)
    
with open(file_path3, 'r') as file:
    misc_json = json.load(file)

def chunk_transcripts(json_data, chunk_size):
    all_chunks = {}

    for key, data in json_data.items():
        transcript_chunks = []
        current_chunk_text = ""
        current_chunk_start_time = None
        word_count = 0

        for item in data:
            text = item['text']
            start_time = item['start']

            words = text.split()

            if word_count + len(words) <= chunk_size:
                current_chunk_text += " " + text
                word_count += len(words)
                if current_chunk_start_time is None:
                    current_chunk_start_time = start_time
            else:
                transcript_chunks.append({'text': current_chunk_text.strip(), 'start_time': current_chunk_start_time})
                current_chunk_text = text
                current_chunk_start_time = start_time
                word_count = len(words)

        if current_chunk_text:
            transcript_chunks.append({'text': current_chunk_text, 'start_time': current_chunk_start_time})

        all_chunks[key] = transcript_chunks

    return all_chunks

final_json_undergrad = chunk_transcripts(undergrad_json, 512)
final_json_mba = chunk_transcripts(mba_json, 512)
final_json_misc = chunk_transcripts(misc_json, 512)

# Write the chunked transcripts to JSON files

with open(f"{artifacts_folder}/chunked_transcripts_mba.json", 'w') as file:
    json.dump(final_json_mba, file, indent=4)

with open(f"{artifacts_folder}/chunked_transcripts_undergrad.json", 'w') as file:
    json.dump(final_json_undergrad, file, indent=4)

with open(f"{artifacts_folder}/chunked_misc_transcripts.json", 'w') as file:
    json.dump(final_json_misc, file, indent=4)
