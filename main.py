import requests
import pandas as pd


def get_token(api_key, client_id, client_secret, ip):
    url = f'http://{ip}:8080/oauth/v2/token'
    params = {
        'grant_type': 'https://arena.uww.io/grants/api_key',
        'client_id': client_id,
        'client_secret': client_secret,
        'api_key': api_key
    }
    response = requests.post(url, params=params)
    return response.json()["access_token"]


def get_endpoint_response(headers, endpoint):
    url = f"http://localhost:8080/api/json/{endpoint}"
    response = requests.get(url, headers=headers)
    return response.json()

def post_endpoint(headers, endpoint, data):

    url = f"http://localhost:8080/api/json/{endpoint}"
    response = requests.post(url, headers=headers, json=data)

    return print(response.status_code)

def patch_endpoint(headers, endpoint, data):

    url = f"http://localhost:8080/api/json/{endpoint}"
    response = requests.put(url, headers=headers, json=data)

    return print(response.status_code)

def delete_endpoint(headers, endpoint, data):

    url = f"http://localhost:8080/api/json/{endpoint}"
    response = requests.delete(url, headers=headers, json=data)

    return print(response.status_code)

def get_custom_id(headers, person_id):

    custom = get_endpoint_response(headers, f"person/get/{person_id}")
    return custom['person']['customId']


def get_all_ranking(api_key, client_id, client_secret, ip, event_id):

    # Get the access token
    headers = {'Authorization': 'Bearer ' + get_token(api_key, client_id, client_secret, ip)}

    # Get all weight categories in a single API call
    weight_categories = get_endpoint_response(headers, f"weight-category/{event_id}")['weightCategories']
    print(weight_categories)

    all_data = []
    for category in weight_categories:
        id_categoria = category['id']
        ranking_categoria = get_endpoint_response(headers, endpoint=f"weight-category/get/{id_categoria}/ranking?=")['ranking']
        print(ranking_categoria)
        try:
            for chave, valor in ranking_categoria.items():
                person_id = valor['fighter']['personId']
                custom_id = get_custom_id(headers, person_id)
                valor['fighter']['customId'] = custom_id
                all_data.append(valor['fighter'])

        except AttributeError:
            for valor in range(len(ranking_categoria)):

                person_id = valor['fighter']['personId']
                custom_id = get_custom_id(headers, person_id)
                valor['fighter']['customId'] = custom_id
                all_data.append(valor['fighter'])
        except():
            pass

    df = pd.json_normalize(all_data)
    return df


def try_print(event_id, headers, user_name):

    url = f"http://localhost:8080/api/json/team/{event_id}/print/entry-list/table"

    weight_categories = get_endpoint_response(headers, f"weight-category/{event_id}")['weightCategories']
    response = requests.request(method="GET", url=url, headers=headers)

    pdf_path = response.json()
    print(pdf_path)
    if response.status_code == 200:
        with open(f'{user_name}.pdf', 'wb') as file:
            file.write(response.content)
        print('File downloaded successfully.')
    else:
        print(f'Error print: {response.status_code}')

    all_data = []
    for category in weight_categories:
        id_categoria = category['id']

        # ranking_categoria = get_endpoint_response(headers, endpoint=f"weight-category/get/{id_categoria}/ranking?=")['ranking']
        categoria_nome = category['fullName']
        url = f"http://localhost:8080/api/xml/weight-category/get/{id_categoria}/bracket/live?print=1&showNumber=1"
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            path_load = response.json()
            print(path_load)
            with open(f'{categoria_nome}.pdf', 'wb') as file:
                file.write(response.content)
            print('File downloaded successfully.')
        else:
            print(f'Error: {response.status_code}')


def get_ranking_rank(api_key, client_id, client_secret, ip, event_id):
    # Get the access token
    headers = {'Authorization': 'Bearer ' + get_token(api_key, client_id, client_secret, ip)}

    # Get all weight categories in a single API call
    weight_categories = get_endpoint_response(headers, f"weight-category/{event_id}")['weightCategories']
    print(weight_categories)
    
    all_data = []
    for category in weight_categories:
        id_categoria = category['id']
        ranking_categoria = get_endpoint_response(headers, endpoint=f"weight-category/get/{id_categoria}/ranking?=")[
            'ranking']
        print(ranking_categoria)
        try:
            for chave, valor in ranking_categoria.items():
                person_id = valor['fighter']['personId']
                custom_id = get_custom_id(headers, person_id)
                valor['fighter']['customId'] = custom_id
                all_data.append(valor['fighter'])

        except AttributeError:
            for valor in range(len(ranking_categoria)):

                person_id = valor['fighter']['personId']
                custom_id = get_custom_id(headers, person_id)
                valor['fighter']['customId'] = custom_id
                all_data.append(valor['fighter'])
        except():
            pass

    df = pd.json_normalize(all_data)
    return df


# if __name__ == "__main__":

    # user_name = "sul-sudeste"

    # with open("credentials.json", "r") as f:
    # credentials_data = json.load(f)

    # credentials = next(
    # cred_data for cred_data in credentials_data if cred_data[next(iter(cred_data))]["user_name"] == user_name)

    # api_key = credentials_data[user_name]["api_key"]
    # client_id = credentials_data[user_name]["client_id"]
    # client_secret = credentials_data[user_name]["client_secret"]
    # ip = credentials_data[user_name]["ip"]
    # event_id = credentials_data[user_name]["event_id"]
    # directory = credentials_data[user_name]["directory"]

    # headers = {'Authorization': 'Bearer ' + get_token(api_key, client_id, client_secret, ip)}

    # weight_categories = get_endpoint_response(headers, f"weight-category/{event_id}")['weightCategories']
    # clear_fights(headers=headers)

    # for category in weight_categories:

    # id_categoria = category['id']

    # print(get_endpoint_response(headers, endpoint=f"weight-category/get/{id_categoria}/ranking?=")['ranking'])

    # df = get_all_ranking(api_key, client_id, client_secret, ip, event_id)

    # df.to_excel(f"{directory}/{user_name}.xlsx", sheet_name=f"{user_name}", index=False)
