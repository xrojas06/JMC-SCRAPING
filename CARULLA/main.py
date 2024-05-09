import json
import pandas as pd
from data_processing import scraping_category


def main():

    with open('categories.json', "r") as file:
        categories = json.load(file)

    with open('template.json', "r") as file:
        base_json = json.load(file)

    with pd.ExcelWriter("carulla.xlsx") as writer:
     for key, value in categories.items():
         if 'precios' in key:
             df = scraping_category(key, categories,base_json)
             if df is not None:
                 df.to_excel(writer, sheet_name=key, index=False)

if __name__ == "__main__":
    main()
    print("Los DataFrames han sido exportados a Excel.")