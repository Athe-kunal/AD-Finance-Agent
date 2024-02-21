import os
import json
from tqdm import tqdm
import re

def median(lst):

    lst.sort()
    return lst[len(lst)//2]

def get_book_data(num_para_words:int=50):
    books_folder = r"artifacts/book_hi_res"
    book_data = []
    for book_name in tqdm(os.listdir(books_folder)):
        # print(book_name)
        if book_name.startswith("Corporate_Finance"):continue
        curr_json_path = os.path.join(books_folder, book_name)
        if book_name.startswith("Narrative"):
            start_page = 1
            end_page = 266
        elif book_name.startswith("Little"):
            start_page = 17
            end_page = None
        elif book_name.startswith("Investment_Philosophies"):
            start_page = 1
            end_page = 486
        elif book_name.startswith("Dark"):
            start_page = 1
            end_page = 794
        elif book_name.startswith("Damodaran"):
            start_page = 1
            end_page = 1237
        else:
            start_page = 1
            end_page = None
        
        #Load the data
        with open(curr_json_path, "r") as f:
            json_data = json.load(f)
        x_start = []
        for jd in json_data:
            x_start.append(jd['coordinates'][0][0])
        x_median = median(x_start)
        metadata_book_name = book_name.split(".")[0]
        for jd in json_data:
            text_split_list = jd['text'].split(" ")
            num_words = len(text_split_list)
            x_coord = jd['coordinates'][0][0]
            page_num = jd['page_num']
            txt = jd['text']
            # txt = re.sub("\. ",".\n",txt)
            if start_page == 1 and end_page == None:
                pass
            elif start_page>page_num:
                continue
            elif end_page is not None and end_page<page_num:
                continue
            if x_median-10<=x_coord <= x_median+10 and text_split_list[0].istitle() and num_words>num_para_words:
                book_data.append(
                    {
                        "text": txt+"\n\n",
                    }
                )
                page_coordinates = jd['coordinates'].copy()
                page_coordinates.insert(0,{"page_num":page_num})
                book_data[-1]["page_num_coordinates"] = [page_coordinates]
                book_data[-1]['book_source'] = metadata_book_name
            else:
                prev_idx = book_data[-1]
                if "text" in prev_idx:
                    prev_idx['text'] = prev_idx['text'][:-2] + txt + "\n\n"
                else:
                    prev_idx['text'] = txt + "\n\n"
                page_coordinates = jd['coordinates'].copy()
                page_coordinates.insert(0,{"page_num":page_num})
                if "page_num_coordinates" not in prev_idx:
                    prev_idx["page_num_coordinates"] = [page_coordinates]
                else:
                    prev_idx["page_num_coordinates"].append(page_coordinates)
                if "book_source" not in prev_idx:
                    prev_idx['book_source'] = metadata_book_name
        book_data.append({})
    return book_data

def higher_preproc(book_data):
    s_dict = {}
    
    for element in book_data:
        if element['book_source'] not in s_dict.keys():
            s_dict[element['book_source']] = ''
        s_dict[element['book_source']]+=element["text"]+" "
    
    return s_dict

if __name__=="__main__":
    book_data = get_book_data()
    book_dict = higher_preproc(book_data)
    for k in book_dict.keys():
        with open(f"src/data/transcript_files/book_{k}.txt","w") as f:
            f.write(book_dict[k])
    
            