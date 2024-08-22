
from main import *

def get_fights_data():

    headers = {'Authorization': 'Bearer ' + get_token(api_key, client_id, client_secret, ip)}
    data = get_endpoint_response(headers, f"fight/{event_id}")['fights']
    df_r = pd.json_normalize(data)


    return df_r


def get_team_data():

    headers = {'Authorization': 'Bearer ' + get_token(api_key, client_id, client_secret, ip)}
    weight_categories = get_endpoint_response(headers, f"weight-category/{event_id}")['weightCategories']
    all_data = []
    for category in weight_categories:
        id_categoria = category['id']
        data = get_endpoint_response(headers, f"weight-category/get/{id_categoria}/team-rankings")["teamsRankings"]
        all_data.append(data)

    df = pd.json_normalize(all_data)
    return df

with open("build/exe.win-amd64-3.10/lib/credentials.json", "r") as f:
    credentials = json.load(f)

api_key = credentials["api_key"]
client_id = credentials["client_id"]
client_secret = credentials["client_secret"]
ip = credentials["ip"]
event_id = credentials["event_id"]
directory = credentials["directory"]
user_name = credentials["user_name"]

#get_fights_data().to_excel("teste.xlsx", index=False)

print(get_team_data().to_excel("testeteams.xlsx", index=False))


