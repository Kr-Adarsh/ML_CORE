import pandas as pd
import fitz

with fitz.open("./The_Alchemist.pdf") as pdf:
    text = ""
    for page in pdf:
        text += page.get_text()
        
# removeing the extra new lines and spaces
text = text.replace("\n", " ").replace("  ", " ")
# print(text[0:1000])

# with open("./The_Alchemist.txt", "r+") as file:
#     content = file.readlines()
# print(content[0:100])

def truncate_txt(text, frm_where: str, end_where:str = None):
    idx = text.find(frm_where)
    print(idx)
    if end_where:
        end_idx = text.find(end_where)
        return text[idx:end_idx]
    return text[idx:]

text = truncate_txt(text, "PART ONE")
fl = "theAlchemist.txt"
with open(fl, "w") as file:
    for i in text: 
        file.write(i)
print(len(fl))