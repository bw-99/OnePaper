import scipdf
import pandas as pd
from const import *
import requests
import json
import tqdm


def download_pdf(url, title):
    tmp_path = f"{PARSED_PATH}/{title}.pdf"
    try:
        response = requests.get(url)
        response.raise_for_status()
        with open(tmp_path, 'wb') as file:
            file.write(response.content)
    except Exception as e:
        print(f'Error during download: {e}')
    return tmp_path


def parse_pdf(pdf_path, title):
    output_path = f"{PARSED_PATH}/{title}.json"
    try:
        article_dict = scipdf.parse_pdf_to_dict(pdf_path)
        with open(output_path, "wb") as f:
            json.dump(article_dict, f)
        os.remove(pdf_path)
    except Exception as e:
        print(f'Error during download: {e}')
        

if __name__=="__main__":
    df = pd.read_csv(CSV_PATH)
    df = df.iloc[df.notna()["PDF Link"].values]
    
    for idx, row in tqdm.tqdm(df.iterrows(), total=df.shape[0]):
        title, url = row["Title"], row["PDF Link"]
        if os.path.exists(f"{PARSED_PATH}/{title}.json"):
            continue
        pdf_path = download_pdf(url=url, title=title)
        parse_pdf(pdf_path=pdf_path, title=title)
        