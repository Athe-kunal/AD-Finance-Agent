import json

if __name__=="__main__":
    file_in = "artifacts/Youtube_API_Transcripts/transcripts_undergrad.json"
    file_out = 'src/data/transcript_files/undergrad_transcript_file.txt'

    with open(file_in,"r") as f:
        data = json.load(f)
    
    s = ""
    for t_list in data.values():
        for d in t_list:
            s = s+d['text']+" "
        s = s+"\n"
    
    with open(file_out,"w") as f:
        f.write(s)
    