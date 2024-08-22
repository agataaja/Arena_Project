import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
from main import *

def get_headers():

    user_name = user_name_combobox.get()
    file_path = "credentials.json"

    with open(file_path, "r") as f:
        credentials_data = json.load(f)

    api_key = credentials_data[user_name]["api_key"]
    client_id = credentials_data[user_name]["client_id"]
    client_secret = credentials_data[user_name]["client_secret"]
    ip = credentials_data[user_name]["ip"]

    headers = {'Authorization': 'Bearer ' + get_token(api_key, client_id, client_secret, ip)}

    return headers


def get_event_id():

    user_name = user_name_combobox.get()
    file_path = "credentials.json"

    with open(file_path, "r") as f:
        credentials_data = json.load(f)

    event_id = credentials_data[user_name]["event_id"]

    return event_id


def clear_fights():


    headers = get_headers()

    event_id = get_event_id()

    weight_categories = get_endpoint_response(headers, f"weight-category/{event_id}")['weightCategories']

    for category in weight_categories:


        id = category['id']

        url = f"http://localhost:8080/api/json/weight-category/get/{id}/fights/clear"
        requests.request("PATCH",url=url, headers=headers)


def save_arena_credentials():

    api_key = api_key_entry.get()
    client_id = client_id_entry.get()
    client_secret = client_secret_entry.get()
    ip = ip_entry.get()
    event_id = event_id_entry.get()
    directory = directory_entry.get()
    user_name = user_name_entry.get()
    credentials = {
        "api_key": api_key,
        "client_id": client_id,
        "client_secret": client_secret,
        "ip": ip,
        "event_id": event_id,
        "directory": directory,
        "user_name": user_name
    }

    try:
        with open("credentials.json", "r") as f:
            existing_credentials = json.load(f)
    except FileNotFoundError:
        existing_credentials = {}

    existing_credentials[user_name] = credentials

    with open("credentials.json", "w") as f:
        json.dump(existing_credentials, f)

    user_names = load_user_names()
    user_name_combobox['values'] = user_names
    user_name_combobox.set("")


    messagebox.showinfo("Credentials Saved", "Arena credentials have been saved!")


def run_main_program():

    user_name = user_name_combobox.get()
    file_path = "credentials.json"

    with open(file_path, "r") as f:
        credentials_data = json.load(f)

    api_key = credentials_data[user_name]["api_key"]
    client_id = credentials_data[user_name]["client_id"]
    client_secret = credentials_data[user_name]["client_secret"]
    ip = credentials_data[user_name]["ip"]
    event_id = credentials_data[user_name]["event_id"]
    directory = credentials_data[user_name]["directory"]

    headers = {'Authorization': 'Bearer ' + get_token(api_key, client_id, client_secret, ip)}

    if not api_key or not client_id or not client_secret or not ip or not event_id or not directory:
        messagebox.showerror("Error", f"Invalid credentials for user '{user_name}'.")
        return



    df = get_all_ranking(api_key, client_id, client_secret, ip, event_id)

    df.to_excel(f"{directory}/{user_name}.xlsx", sheet_name=f"{user_name}", index=False)

    messagebox.showinfo("Main Program Executed", "The main program has been executed!")


def run_fights_info():

    user_name = user_name_combobox.get()
    file_path = "credentials.json"

    with open(file_path, "r") as f:
        credentials_data = json.load(f)

    api_key = credentials_data[user_name]["api_key"]
    client_id = credentials_data[user_name]["client_id"]
    client_secret = credentials_data[user_name]["client_secret"]
    ip = credentials_data[user_name]["ip"]
    event_id = credentials_data[user_name]["event_id"]
    directory = credentials_data[user_name]["directory"]

    headers = {'Authorization': 'Bearer ' + get_token(api_key, client_id, client_secret, ip)}

    if not api_key or not client_id or not client_secret or not ip or not event_id or not directory:
        messagebox.showerror("Error", f"Invalid credentials for user '{user_name}'.")
        return

    fight_list = []

    data_list = []

    response = get_endpoint_response(headers, endpoint=f"fight/{event_id}")['fights']


    for i in range(len(response)):

        f_result = response[i]['result']
        tc_points = response[i]['technicalPoints']
        winner_fighter_id = response[i]['winnerFighter']
        try:
            atleta = get_endpoint_response(headers, endpoint=f"fighter/get/{winner_fighter_id}")['fighter']
            atleta_vencedor = atleta['fullName']
            f1_pid = response[i]["fighter1PersonId"]
            f1_id = get_customId(headers, person_id=f1_pid)
            f2_pid = response[i]["fighter2PersonId"]
            f2_id = get_customId(headers, person_id=f2_pid)

        except:

            f1_id = "undefined"
            f2_id = "undefined"
            atleta_vencedor = "undefined"

        f1_nome = response[i]["fighter1FullName"]
        f2_nome = response[i]["fighter2FullName"]
        tipo_de_vitoria = response[i]["victoryType"]
        f1_cp = response[i]["fighter1RankingPoint"]
        f2_cp = response[i]["fighter2RankingPoint"]
        nome_evento = response[i]["sportEventName"]
        categoria = response[i]["weightCategoryFullName"]
        team1 = response[i]['team1AlternateName']
        team2 = response[i]['team2AlternateName']
        check_rank = response[i]['rankingCheck']
        tech_check = response[i]['technicalCheck']
        rk_nice_name = response[i]['rankingPointNiceName']
        fight_number = response[i]['fightNumber']
        fight_id = response[i]['id']
        weight_category_id = response[i]["sportEventWeightCategoryId"]
        is_round_robin = response[i]['isRobinGroupFight']

        try:
            for item in tc_points.keys():

                atleta = tc_points[item]['fullName']

                total_de_pontos_tecnicos = tc_points[item]['total']

                if item == winner_fighter_id:

                    is_fight_winner = 1
                else:
                    is_fight_winner = 0


                print(f"{atleta} marcou o total de: {total_de_pontos_tecnicos}")

                rounds = tc_points[item]['rounds']

                for z in rounds.keys():

                    round_numer = rounds[z]['number']
                    total_de_pontos_do_round = rounds[z]['total']
                    points = rounds[z]['points']

                    print(f"Total de: {total_de_pontos_do_round} maracados no {round_numer} round")

                    for pontos in points.keys():

                        ponto_marcado = points[pontos]['points']
                        segundo = points[pontos]['second']
                        print(ponto_marcado, segundo)

                        linhas_minimas = [atleta,
                                          is_fight_winner,
                                          total_de_pontos_tecnicos,
                                          total_de_pontos_do_round,
                                          round_numer,
                                          ponto_marcado,
                                          segundo,
                                          fight_number,
                                          fight_id,
                                          event_id]

                        fight_list.append(linhas_minimas)
        except:

            linhas_minimas = [0,
                              0,
                              0,
                              0,
                              0,
                              0,
                              0,
                              fight_number,
                              fight_id,
                              event_id]

            fight_list.append(linhas_minimas)

        all_data = [f_result,
                    winner_fighter_id,
                    atleta_vencedor,
                    f1_nome,
                    f1_id,
                    f2_nome,
                    f2_id,
                    tipo_de_vitoria,
                    f1_cp,
                    f2_cp,
                    event_id,
                    nome_evento,
                    categoria,
                    team1,
                    team2,
                    check_rank,
                    tech_check,
                    rk_nice_name,
                    fight_number,
                    fight_id,
                    weight_category_id]

        print(all_data)

        data_list.append(all_data)

        df1 = pd.DataFrame(data_list, columns=[
                    'f_result',
                    'winner_fighter_id',
                    'atleta_vencedor',
                    'f1_nome',
                    'f1_id',
                    'f2_nome',
                    'f2_id',
                    'tipo_de_vitoria',
                    'f1_cp',
                    'f2_cp',
                    'id do evento',
                    'nome do evento',
                    'categoria',
                    'team1',
                    'team2',
                    'check_rank',
                    'tech_check',
                    'rk_nice_name',
                    'fight_number',
                    'fight_id',
                    'weight_category_id'])

        df2 = pd.DataFrame(fight_list, columns=["atleta",
                                                 "is_fight_winner",
                                                 "total_de_pontos_tecnicos",
                                                 "total_de_pontos_do_round",
                                                 "round_numer",
                                                 "ponto_marcado",
                                                 "segundo",
                                                 "fight_number",
                                                 "fight_id",
                                                 "id do evento"])

        df2.to_excel(f"{user_name}_rounds_results.xlsx", index=False)

        df1.to_excel(f"{user_name}_fight_results.xlsx", index=False)

    messagebox.showinfo("fights loaded", "The fights results has been loaded to the files!")


def get_teams_ranking():

    user_name = user_name_combobox.get()
    file_path = "credentials.json"

    with open(file_path, "r") as f:
        credentials_data = json.load(f)

    directory = credentials_data[user_name]["directory"]
    file = f"D://Users//Ágata Aja//CBW//RESULTADOS ARENA 2023-AGOSTO//resultados individuais//{user_name}.xlsx"
    df = pd.read_excel(file)

    # Define a function to assign values based on the 'rank' column
    def assign_points(rank):
        if rank == 1:
            return 5
        elif rank == 2:
            return 3
        elif rank == 3:
            return 2
        elif rank == 4:
            return 2
        elif rank == 5:
            return 1
        else:
            return 0.5  # You can specify a default value if needed


    df['jubs points'] = df['rank'].apply(assign_points)

    
    print(df)

    df.to_excel(f"jubs2023.xlsx", sheet_name=f"{user_name}", index=False)

    grouped = df.groupby('teamAlternateName')

    # Now, you can perform operations on each group. For example, calculate the sum of 'A' in each group:
    grouped_sum = grouped['jubs points'].sum()

    # Display the sum for each group
    print(grouped_sum)


def browse_directory():
    directory = filedialog.askdirectory()
    directory_entry.delete(0, tk.END)
    directory_entry.insert(0, directory)


def load_user_names():
    try:
        with open("credentials.json", "r") as f:
            credentials_data = json.load(f)
            #user_names = []
        #for n in range(len(credentials_data)):

            #user_names.append(n)
        user_names = [machines["user_name"] for cred_data, machines in credentials_data.items()]
        #user_names = [credentials[next(iter(credentials))]["user_name"] for credentials in credentials_data]
        return user_names
    except FileNotFoundError:
        return []


def get_sport_events_info():

    get_endpoint_response(get_headers(), endpoint="/sport-event")                                           


def get_eight_quarter_losers():

    headers = get_headers()
    id_evento = get_event_id()

    response = get_endpoint_response(headers=headers, endpoint=f"fight/{id_evento}/completed")['fights']
    eighters_list = []
    quarters_list = []
    print(response)

    for i in range(len(response)):

        round_name = response[i]['roundFriendlyName']

        if round_name == "1/8 Final" or round_name == "1/4 Final":
            winner_fighter_id = response[i]['winnerFighter']
            try:
                atleta = get_endpoint_response(headers, endpoint=f"fighter/get/{winner_fighter_id}")['fighter']
                atleta_vencedor = atleta['fullName']
                f1_pid = response[i]["fighter1PersonId"]
                f1_id = get_customId(headers, person_id=f1_pid)
                f2_pid = response[i]["fighter2PersonId"]
                f2_id = get_customId(headers, person_id=f2_pid)

            except:

                f1_id = "undefined"
                f2_id = "undefined"
                atleta_vencedor = "undefined"

            f1_nome = response[i]["fighter1FullName"]
            f2_nome = response[i]["fighter2FullName"]
            f1_cp = response[i]["fighter1RankingPoint"]
            f2_cp = response[i]["fighter2RankingPoint"]
            team_1 = response[i]['team1Name']
            team_2 = response[i]['team2Name']
            team1 = response[i]['team1AlternateName']
            team2 = response[i]['team2AlternateName']
            check_rank = response[i]['rankingCheck']
            tech_check = response[i]['technicalCheck']
            weight_category_id = response[i]["sportEventWeightCategoryId"]
            is_round_robin = response[i]['isRobinGroupFight']
            round_name = response[i]['roundFriendlyName']
            estilo = response[i]['sportName']
            audience = response[i]['audienceName']
            peso = response[i]['weightCategoryName']
            print(round_name, "pontos atleta 2:", f2_cp, "pontos atleta 1:",f1_cp)
            if round_name == "1/8 Final":

                if f1_cp == 1 or f1_cp == 0:
                    eighters_list.append([team_1, team1, "", "", f1_nome, "", "", audience, estilo, peso, "", "", f1_id, ""])
                    print("atleta 1 perdeu, linha adicionada")

                elif f2_cp == 1 or f2_cp == 0:
                    eighters_list.append([team_2, team2, "", "", f2_nome, "", "", audience, estilo, peso, "", "", f2_id, ""])
                    print("atleta 2 perdeu, linha adicionada")

            elif round_name == "1/4 Final":

                if f1_cp == 1 or f1_cp == 0:
                    quarters_list.append([team_1, team1, "", "", f1_nome, "", "", audience, estilo, peso, "", "", f1_id, ""])
                    print("atleta 1 perdeu, linha adicionada")

                elif f2_cp == 1 or f2_cp == 0:
                    quarters_list.append([team_2, team2, "", "", f2_nome, "", "", audience, estilo, peso, "", "", f2_id, ""])
                    print("atleta 2 perdeu, linha adicionada")

    df = pd.DataFrame(eighters_list, columns=[
        "Code",
        "Code Alt(max 10 chars)",
        "Last Name",
        "First Name",
        "Full Name",
        "Short Name",
        "Athena Print ID",
        "Age Group",
        "Discipline",
        "Weight category",
        "Previous Federation",
        "Seed Number",
        "Custom ID",
        "DrawNumber"])
    print(df)
    df.to_excel("perdedores das oitavas.xlsx", sheet_name="teste", index=False
                )

    df2 = pd.DataFrame(quarters_list, columns=[
        "Code",
        "Code Alt(max 10 chars)",
        "Last Name",
        "First Name",
        "Full Name",
        "Short Name",
        "Athena Print ID",
        "Age Group",
        "Discipline",
        "Weight category",
        "Previous Federation",
        "Seed Number",
        "Custom ID",
        "DrawNumber"])
    print(df2)
    df2.to_excel("perdedores das quartas.xlsx", sheet_name="teste", index=False)


def show_credentials_infos(user_name):

    user_name = user_name_combobox.get()
    file_path = "credentials.json"

    with open(file_path, "r") as f:
        credentials_data = json.load(f)

    api_key = credentials_data[user_name]["api_key"]
    client_id = credentials_data[user_name]["client_id"]
    client_secret = credentials_data[user_name]["client_secret"]
    ip = credentials_data[user_name]["ip"]
    event_id = credentials_data[user_name]["event_id"]
    directory = credentials_data[user_name]["directory"]

    if user_name in credentials_data:
        api_key_entry.delete(0, tk.END)
        api_key_entry.insert(0, api_key)
        client_id_entry.delete(0, tk.END)
        client_id_entry.insert(0, client_id)
        client_secret_entry.delete(0,tk.END)
        client_secret_entry.insert(0,client_secret)
        ip_entry.delete(0,tk.END)
        ip_entry.insert(0,ip)
        event_id_entry.delete(0,tk.END)
        event_id_entry.insert(0,event_id)
        directory_entry.delete(0,tk.END)
        directory_entry.insert(0,directory)


root = tk.Tk()
root.configure(background="yellow", height=100, width=1000)

root.title("Arena Credentials")


# Create labels and entry widgets for each credential
tk.Label(root, text="API Key:").grid(row=0, column=0)
api_key_entry = tk.Entry(root)
api_key_entry.grid(row=0, column=1)

tk.Label(root, text="Client ID:").grid(row=1, column=0)
client_id_entry = tk.Entry(root)
client_id_entry.grid(row=1, column=1)

tk.Label(root, text="Client Secret:").grid(row=2, column=0)
client_secret_entry = tk.Entry(root, show="*")
client_secret_entry.grid(row=2, column=1)

tk.Label(root, text="IP:").grid(row=3, column=0)
ip_entry = tk.Entry(root)
ip_entry.grid(row=3, column=1)

tk.Label(root, text="Event ID:").grid(row=4, column=0)
event_id_entry = tk.Entry(root)
event_id_entry.grid(row=4, column=1)

tk.Label(root, text="Directory:").grid(row=5, column=0)
directory_entry = tk.Entry(root)
directory_entry.grid(row=5, column=1)


tk.Label(root, text="Machine Name:").grid(row=6, column=0)
user_name_entry = tk.Entry(root)
user_name_entry.grid(row=6, column=1)


user_name_combobox = ttk.Combobox(root, values=load_user_names())
user_name_combobox.grid(row=8, column=0, columnspan=4, pady=10)
user_name_combobox.bind('<<ComboboxSelected>>', show_credentials_infos)


browse_button = tk.Button(root, text="Selecionar", command=browse_directory)
browse_button.grid(row=5, column=2, padx=10 )

save_button = tk.Button(root, text="Save Credentials", command=save_arena_credentials)
save_button.grid(row=7, column=0, columnspan=2, pady=10)

run_main_button = tk.Button(root, text="Dados de Lutas", command=run_main_program)
run_main_button.grid(row=9, column=0)

team_ranking_button = tk.Button(root, text="Resultado Geral de Times", command=get_teams_ranking)
team_ranking_button.grid(row=10, column=0, padx=10)

fight_infos_button = tk.Button(root, text="Resultados por Luta", command=run_fights_info)
fight_infos_button.grid(row=9, column=1, padx=10)

clear_fights_button = tk.Button(root, text="Limpar Sessão", command=clear_fights)
clear_fights_button.grid(row=10, column=1, pady=10)

rodar_oitavas_quartas_botao = tk.Button(root, text="Gerar Planilha com Perdedores das Oitava/Quartas", command=get_eight_quarter_losers)
rodar_oitavas_quartas_botao.grid(row=11, column=1, pady=10)

root.mainloop()
