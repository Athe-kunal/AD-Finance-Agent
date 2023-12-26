from typing import List
from unstructured.partition.pdf import partition_pdf

def get_slides_data(filename,pages_NOT_to_include:List[str]=[1]):
    pages_NOT_to_include_str = [str(pg) for pg in pages_NOT_to_include]

    elements = partition_pdf(filename,infer_table_structure=False,include_page_breaks=True)
    num_pages = int(elements[-2].text)
    slides_data = ""
    # first_encounter_to_NOT_include_page = 0
    ignore_page = False
    
    for el in elements:
        elem_text = el.text
        elem_metadata_type = el.to_dict()['type']
        if elem_text in pages_NOT_to_include_str and elem_metadata_type=='UncategorizedText':
            ignore_page=True
        if ignore_page and elem_metadata_type=='PageBreak': 
            ignore_page=False
            continue
        
        if not ignore_page:
            try:
                page_num = int(elem_text)
                continue
            except ValueError:
                pass
            if elem_text == 'Aswath Damodaran': continue
            if elem_metadata_type=='PageBreak':
                slides_data+="\n\n"
            else:
                slides_data+=elem_text
    return slides_data


slides_data = get_slides_data("SLIDES\Valuation_Intro.pdf",[1,4,19])