from bs4 import BeautifulSoup
import requests
import pandas as pd


def load_whatsmart_table(ano):

    data = requests.get(f"https://whatsmat.uww.org/daten.php?pid=&suchart=nation&fland=6875342BCEB04CC48166C21C53A21C13&fvon={ano}&fbis=&fwkart=&fstil=&fakl=&fsort=0")

    soup = BeautifulSoup(data.text, 'html.parser')
    data = soup.find('table', {'class': 'normal'})

    df = pd.read_html(str(data))[0]

    return df


