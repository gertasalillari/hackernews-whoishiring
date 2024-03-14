import json
import os
import time

import pandas as pd
import requests
from tqdm import tqdm

tqdm.pandas(leave=False)

# LOAD DATA
DATA_DIR = os.getenv("DATA_DIR")
APOLLO_KEY = os.getenv("APOLLO_KEY")
filename = os.path.join(DATA_DIR, "output.csv")
df = pd.read_csv(filename, na_values="")
df.fillna("", inplace=True)


test_url_index = df[df["company_url"] != ""]["company_url"][:50].index
urls = df.loc[test_url_index, "company_url"]

key_names = [
    "name",
    "website_url",
    "linkedin_url",
    "twitter_url",
    "facebook_url",
    "founded_year",
    "crunchbase_url",
    "keywords",
    "estimated_num_employees",
    "industries",
    "city",
    "state",
    "annual_revenue",
    "total_funding",
    "total_funding_printed",
    "latest_funding_round_date",
    "latest_funding_stage",
    "departmental_head_count",
]


querystring = {"api_key": APOLLO_KEY, "domain": "apollo.io"}

headers = {"Cache-Control": "no-cache", "Content-Type": "application/json"}

apollo_url = "https://api.apollo.io/v1/organizations/enrich"

url_data = []
for url in tqdm(urls):
    querystring["domain"] = url
    response = requests.request("GET", apollo_url, headers=headers, params=querystring)

    if response.text:
        output = json.loads(response.text)
        if "organization" in output:
            url_data.append([output["organization"].get(key) for key in key_names])
        else:
            url_data.append([])
    time.sleep(1)


df.loc[test_url_index, key_names] = pd.DataFrame(url_data, columns=key_names)
output_example = df[(df.index.isin(test_url_index)) & (~pd.isna(df["name"]))]

output_filename = os.path.join(DATA_DIR, "outputs/apollo_example.csv")
output_example.to_csv(output_filename, index=False)
