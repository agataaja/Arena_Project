import json

import pandas as pd
import requests
from concurrent.futures import ThreadPoolExecutor


with open('token.json', 'r') as token:

    sge_token = json.load(token)['token']

def fetch_data(base_url, querys, headers, page):

    response = requests.get(f"{base_url}{querys}&page={page}", headers=headers).json()['items']
    return pd.json_normalize(response)



def main_atletas():

    token = sge_token
    expands = ["atletaDocumentos"]
    base_url = "https://restcbw.bigmidia.com/gestao/api/atleta"
    headers = {"Content-Type": "application/json"}
    querys = f"?expand={','.join(map(str, expands))}&flag_del=0&access-token={token}"
    page_count = requests.get(f"{base_url}{querys}", headers=headers).json()["_meta"]["pageCount"]

    with ThreadPoolExecutor() as executor:

        dfs = executor.map(lambda page: fetch_data(base_url, querys, headers, page), range(1, page_count+1))

    final_df = pd.concat(dfs, ignore_index=True)


    return final_df

def main_estabelecimento():

    token = sge_token
    expands = [""]
    base_url = " https://restcbw.bigmidia.com/gestao/api/estabelecimento"
    headers = {"Content-Type": "application/json"}
    querys = f"?expand={','.join(map(str, expands))}&flag_del=0&access-token={token}"
    page_count = requests.get(f"{base_url}{querys}", headers=headers).json()["_meta"]["pageCount"]

    with ThreadPoolExecutor() as executor:
        dfs = executor.map(lambda page: fetch_data(base_url, querys, headers, page), range(1, page_count+1))

    final_df = pd.concat(dfs, ignore_index=True)

    filtered_df = final_df[~final_df['id_estabelecimento_tipo'].isin([1, 2])]

    return filtered_df


def get_ids_ano_eventos(anos):

    headers = {"Content-Type": "application/json"}
    base_url = "https://restcbw.bigmidia.com/gestao/api/evento"
    querys = f"?flag_del=0"

    page_count = requests.get(f"{base_url}{querys}", headers=headers).json()["_meta"]["pageCount"]


    dfs = []
    with ThreadPoolExecutor() as executor:
        for ano in anos:
            filtered_dfs = executor.map(lambda page: fetch_data(base_url, querys, headers, page), range(1, page_count+1))
            final_df = pd.concat(filtered_dfs, ignore_index=True)
            filtered_df = final_df[final_df['data_fim'].str.contains(f"{ano}")]
            dfs.append(filtered_df)

    final_df = pd.concat(dfs, ignore_index=True)


    return final_df


if __name__ == '__main__':

    df_estabelecimento = main_estabelecimento()

    df_atletas = main_atletas()

    # df_estabelecimento.to_excel('estabelecimentos sge.xlsx')



