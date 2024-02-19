import os
import json
from tqdm import tqdm


def median(lst):

    lst.sort()
    return lst[len(lst)//2]

def get_book_data():
    books_folder = r"artifacts\book_hi_res"
    book_data = []
    for book_name in tqdm(os.listdir(books_folder)):
        # print(book_name)
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
            num_words = len(jd['text'].split(" "))
            x_coord = jd['coordinates'][0][0]
            page_num = jd['page_num']
            if start_page == 1 and end_page == None:
                pass
            elif start_page>page_num:
                continue
            elif end_page is not None and end_page<page_num:
                continue
            if x_median-10<=x_coord <= x_median+10 and num_words>50:
                book_data.append(
                    {
                        "text": jd['text']+"\n\n",
                    }
                )
                page_coordinates = jd['coordinates'].copy()
                page_coordinates.insert(0,{"page_num":page_num})
                book_data[-1]["page_num_coordinates"] = [page_coordinates]
                book_data[-1]['book_source'] = metadata_book_name
            else:
                prev_idx = book_data[-1]
                prev_idx['text'] = prev_idx['text'][:-2] + jd['text'] + "\n\n"
                page_coordinates = jd['coordinates'].copy()
                page_coordinates.insert(0,{"page_num":page_num})
                prev_idx["page_num_coordinates"].append(page_coordinates)
    return book_data