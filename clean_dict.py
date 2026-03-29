import pandas as pd
import re

# Load Excel file
df = pd.read_excel("ENGLISH-HINDI-DICT.xlsx", header=None)

def split_eng_hin(text):
    words = str(text).split()
    
    eng_words = []
    hin_words = []
    
    for w in words:
        if re.search(r'[\u0900-\u097F]', w):  # Hindi Unicode
            hin_words.append(w)
        else:
            eng_words.append(w)
    
    return eng_words, hin_words

eng_list = []
hin_list = []

for i in range(len(df)):
    text_parts = []
    
    # Take both columns if they exist
    for col in [0, 1]:
        if col in df.columns:
            val = str(df.iloc[i, col])
            if val != "nan":
                text_parts.append(val)
    
    # Combine both columns into one string
    combined_text = " ".join(text_parts)
    
    eng_words, hin_words = split_eng_hin(combined_text)
    
    eng_list.append(" ".join(eng_words))
    hin_list.append(" ".join(hin_words))

# Create DataFrame
clean_df = pd.DataFrame({
    "english": eng_list,
    "hindi": hin_list
})

# Clean Hindi column
clean_df["hindi"] = clean_df["hindi"].str.replace(",", " ")

# Apply join_char
join_char = "_"
clean_df["english"] = clean_df["english"].str.replace(" ", join_char)
clean_df["hindi"] = clean_df["hindi"].str.replace(" ", join_char)

# Remove empty rows (optional but recommended)
clean_df = clean_df[(clean_df["english"] != "") & (clean_df["hindi"] != "")]

# Save TSV
clean_df.to_csv("ENGLISH-HINDI-DICT.tsv", sep="\t", index=False, header=False)

print("Done! Clean TSV created.")