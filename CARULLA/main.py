import base64
import json
import pandas as pd
import http.client
from data_processing import scraping_category


def main():

    with open('categories.json', "r") as file:
        categories = json.load(file)

    with open('template.json', "r") as file:
        base_json = json.load(file)

    with pd.ExcelWriter("carulla.xlsx") as writer:
        for key, value in categories.items():
            if "vinos" in value:
             df = scraping_category(value, base_json)
             if df is not None:
                 df.to_excel(writer, sheet_name=key, index=False)

if __name__ == "__main__":
    main()
    print("Los DataFrames han sido exportados a Excel.")