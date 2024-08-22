import json
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog, ttk, StringVar
import requests
import re
from main import *
from bs4 import BeautifulSoup
from bigmidia_restapi import *
from fuzzywuzzy import process


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
        requests.request("PATCH", url=url, headers=headers)

def clear_fights_for_age_group():

    headers = get_headers()

    weight_categories = get_weights_categories()
    categoria = simpledialog.askstring("age group","qual categoria mane")

    for id, shortName in weight_categories.items():

        if categoria in shortName:

            url = f"http://localhost:8080/api/json/weight-category/get/{id}/fights/clear"
            requests.request("PATCH", url=url, headers=headers)


def save_arena_credentials():

    api_key = entries[0].get()
    client_id = entries[1].get()
    client_secret = entries[2].get()
    ip = entries[3].get()
    event_id = entries[4].get()
    directory = entries[5].get()
    user_name = entries[6].get()
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

    print(response)

    for i in range(len(response)):

        f_result = response[i]['result']
        tc_points = response[i]['technicalPoints']
        winner_fighter_id = response[i]['winnerFighter']
        try:
            atleta = get_endpoint_response(headers, endpoint=f"fighter/get/{winner_fighter_id}")['fighter']
            atleta_vencedor = atleta['fullName']
            f1_pid = response[i]["fighter1PersonId"]
            f1_id = get_custom_id(headers, person_id=f1_pid)
            f2_pid = response[i]["fighter2PersonId"]
            f2_id = get_custom_id(headers, person_id=f2_pid)

        except():

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

        print(tc_points)

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
        except():

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
    file = f"D://Users//Ágata Aja//CBW//RESULTADOS ARENA 2023-AGOSTO//{user_name}.xlsx"
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

    # df['jubs points'] = df['rank'].apply(assign_points)

    print(df)

    # df.to_excel(f"jubs2023.xlsx", sheet_name=f"{user_name}", index=False)

    grouped = df.groupby('teamName')

    # Now, you can perform operations on each group. For example, calculate the sum of 'A' in each group:
    grouped_sum = grouped['teamRankingPoint'].sum()

    # Display the sum for each group
    print(grouped_sum)


def browse_directory():

    directory = filedialog.askdirectory()
    entries[5].delete(0, tk.END)
    entries[5].insert(0, directory)


def save_credentials_stored():

    file_saving_path = filedialog.asksaveasfilename(confirmoverwrite=True)

    if file_saving_path:
        with open("credentials.json", 'r') as creds:

            data = json.load(creds)

            df = pd.json_normalize(data)

            df.to_excel(excel_writer=f"{file_saving_path}.xlsx")

            messagebox.showinfo("Sucesso", "arquivo salvo com sucesso")

    else:
        messagebox.showerror("Erro", "uepa, ratinho!")


def load_user_names():
    try:
        with open("credentials.json", "r") as f:
            credentials_data = json.load(f)
            # user_names = []
        # for n in range(len(credentials_data)):

            # user_names.append(n)
        user_names = [machines["user_name"] for cred_data, machines in credentials_data.items()]
        # user_names = [credentials[next(iter(credentials))]["user_name"] for credentials in credentials_data]
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

    lista_de_perdedores = {}

    for i in range(len(response)):

        round_name = response[i]['roundFriendlyName']

        print(round_name)

        if round_name == "1/4 Final" or round_name == "1/8 Final" or round_name == "Qualif.":

            winner_fighter_id = response[i]['winnerFighter']

            #try:

                #atleta = get_endpoint_response(headers, endpoint=f"fighter/get/{winner_fighter_id}")['fighter']
                #atleta_vencedor = atleta['fullName']
                #f1_pid = response[i]["fighter1PersonId"]
                #f1_id = get_custom_id(headers, person_id=f1_pid)
                #f2_pid = response[i]["fighter2PersonId"]
                #f2_id = get_custom_id(headers, person_id=f2_pid)

            #except():

                #f1_id = "undefined"
                #f2_id = "undefined"
                #atleta_vencedor = "undefined"

            f1_nome = response[i]["fighter1FullName"]
            f1_draw_number = response[i]['fighter1DrawRank']
            f2_nome = response[i]["fighter2FullName"]
            f2_draw_number = response[i]['fighter2DrawRank']
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
            print(round_name, "pontos atleta 2:", f2_cp, "pontos atleta 1:", f1_cp)

            if round_name == "1/8 Final":

                if f1_cp == 1 or f1_cp == 0:
                    eighters_list.append(
                        [team_1, team1, "", "", f1_nome, "", "", audience, estilo, peso, "", "", "", f1_draw_number])
                    print("atleta 1 perdeu, linha adicionada")

                elif f2_cp == 1 or f2_cp == 0:
                    eighters_list.append(
                        [team_2, team2, "", "", f2_nome, "", "", audience, estilo, peso, "", "", "", f2_draw_number])
                    print("atleta 2 perdeu, linha adicionada")

            elif round_name == 'Qualif.':

                if f1_cp == 1 or f1_cp == 0:
                    eighters_list.append(
                        [team_1, team1, "", "", f1_nome, "", "", audience, estilo, peso, "", "", "", f1_draw_number])
                    print("atleta 1 perdeu, linha adicionada")

                    lista_de_perdedores[f1_nome] = weight_category_id

                elif f2_cp == 1 or f2_cp == 0:
                    eighters_list.append(
                        [team_2, team2, "", "", f2_nome, "", "", audience, estilo, peso, "", "", "", f2_draw_number])
                    print("atleta 2 perdeu, linha adicionada")

                    lista_de_perdedores[f2_nome] = weight_category_id

            elif round_name == "1/4 Final":

                if f1_cp == 1 or f1_cp == 0:

                    quarters_list.append(
                        [team_1, team1, "", "", f1_nome, "", "", audience, estilo, peso, "", "",
                         "", f1_draw_number * 3])
                    quarters_list.append(
                        ["null", "null", "", "", f"null.{f1_nome}", "", "", audience, estilo, peso, "", "",
                         "", int(f1_draw_number * 3) + 1])

                    print("atleta 1 perdeu, linha adicionada")

                elif f2_cp == 1 or f2_cp == 0:

                    quarters_list.append(
                        [team_2, team2, "", "", f2_nome, "", "", audience, estilo, peso, "", "",
                         "", f2_draw_number*3])
                    quarters_list.append(
                        ["null", "null", "", "", f"null.{f2_nome}", "", "", audience, estilo, peso, "", "",
                         "", f2_draw_number*3+1])

                    print("atleta 2 perdeu, linha adicionada")

    catgoridict = get_weights_categories()

    for id in catgoridict.keys():

        response = get_endpoint_response(headers, f"weight-category/get/{id}")

        number_of_fighters = response['weightCategory']['fightersIsReady'][0][
            'weightCategoryCountReadyFighters']

        if number_of_fighters < 16:

            contagem_de_perdedores = list(lista_de_perdedores.values()).count(id)

            atletas_fantasmas = 8 - contagem_de_perdedores

            for i in range(atletas_fantasmas):

                eighters_list.append(
                    ["", "", "", "", f"null", "", "", response['weightCategory']['audienceName'], response['weightCategory']['sportId'], re.findall(r'\d+', str(response['weightCategory']['alternateName'])), "", "",
                     "", ""])

            # contador_de_categoria = 16 - number_of_fighters

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
    # df.to_excel(r"C:\Users\agata\CBW 2024\JEBS\SUB 18\SERIE BRONZE.xlsx", sheet_name="Oitavas", index=False)

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
    df2.to_excel(r"C:\Users\agata\CBW 2024\JEBS\SUB 18\SERIE PRATA.xlsx", sheet_name="Quartas", index=False)


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
        entries[0].delete(0, tk.END)
        entries[0].insert(0, api_key)
        entries[1].delete(0, tk.END)
        entries[1].insert(0, client_id)
        entries[2].delete(0, tk.END)
        entries[2].insert(0, client_secret)
        entries[3].delete(0, tk.END)
        entries[3].insert(0, ip)
        entries[4].delete(0, tk.END)
        entries[4].insert(0, event_id)
        entries[5].delete(0, tk.END)
        entries[5].insert(0, directory)
        entries[6].delete(0, tk.END)
        entries[6].insert(0, user_name)


def clear_single_fight(fight_id, headers):

    url = f"http://localhost:8080/api/json/fight/get/{fight_id}/clear-result"
    tryi = requests.request("POST", url=url, headers=headers)
    print(tryi.status_code)


def get_completed_fights_ids(id_evento, headers):

    response = get_endpoint_response(headers=headers, endpoint=f"fight/{id_evento}/completed")['fights']

    fights_id_list = []
    fights_dict = {}

    for i in range(len(response)):

        fight_id = response[i]['id']
        estilo = response[i]['sportName']
        audience = response[i]['audienceName']
        peso = response[i]['weightCategoryName']
        fight_number = response[i]['fightNumber']

        fights_id_list.append([fight_id, estilo, audience, peso, fight_number])
        fights_dict[fight_id] = [estilo, audience, peso, fight_number]

    return fights_dict


def run_selecionar_categorias():

    headers = get_headers()
    id_evento = get_event_id()

    selection_window = tk.Toplevel(root, bg="#2f2f2f")
    selection_window.title("Selecione as Categorias/Pesos")
    selection_window.iconbitmap('icon 1.ico')

    items = get_completed_fights_ids(id_evento, headers)

    # Create a list to store the Checkbutton variables
    check_vars = []

    for valor in items.values():
        var = tk.StringVar()
        check_vars.append(var)
        checkbutton = tk.Checkbutton(selection_window, text=f"Luta: {valor[3]}", variable=var)
        checkbutton.pack()

    def limpar_lutas_selecionadas():

        selected_items = [chave
                          for var, chave in zip(check_vars, items.keys())
                          if var.get() == "1"]
        for chave in selected_items:
            print("Selected:", chave)
            clear_single_fight(chave, headers)
            print(f"Luta: {chave} apagada")

    select_button = tk.Button(selection_window, text="Show Selected Items", command=limpar_lutas_selecionadas)
    select_button.pack()


def try_cleaning():

    headers = get_headers()
    var = input("digite o id da luta")
    clear_single_fight(var, headers)

    print("cleaned")


def get_sge_event():

    selection_window = tk.Toplevel(root, bg="#2f2f2f")
    selection_window.title("Selecione o Evento ")
    selection_window.iconbitmap('icon 1.ico')
    selection_window.configure(background="#2f2f2f", bg="#2f2f2f", highlightbackground="black", highlightcolor="black")

    with open("eventos sge 2024.json", "rb") as campeonatos_sge:
        campeonatos_data = json.load(campeonatos_sge)

    selected_event_var = tk.StringVar()
    button_style = {"bg": "#2f2f2f", "fg": "white", "font": ("Roboto", 9)}
    event_combobox = ttk.Combobox(selection_window, values=list(campeonatos_data.keys()), width=50)
    event_combobox.set("Selecione o evento do SGE")
    event_combobox.grid(row=0, column=0, padx=10, pady=10)

    # Function to set the selected event and close the window
    def set_selected_event():

        global evento_sge
        evento_sge = event_combobox.get()
        selection_window.destroy()

        return evento_sge

    # Button to confirm the selection
    confirm_button = tk.Button(selection_window, text="Confirm", command=set_selected_event, **button_style, width=10, relief='groove', borderwidth=2)
    confirm_button.grid(row=1, column=0, padx=10, pady=10)

    selection_window.wait_window(event_combobox)

    return evento_sge, campeonatos_data


def post_results_sge():

    headers = get_headers()
    event_id = get_event_id()

    all_data = []
    var_dict = {}

    evento_sge, campeonatos_data = get_sge_event()

    weight_categories = get_endpoint_response(headers, f"weight-category/{event_id}")['weightCategories']

    for category in weight_categories:


        id_categoria = category['id']
        id_evento_sge = campeonatos_data[evento_sge]['id_sge']
        categoria_sge = campeonatos_data[evento_sge]['age']

        ranking_categoria = get_endpoint_response(headers, endpoint=f"weight-category/get/{id_categoria}/ranking?=")[
            'ranking']

        print(ranking_categoria)

        try:
            for chave, valor in ranking_categoria.items():

                weight_category_string = str(valor['fighter']['weightCategoryFullName'])
                categoria_arena = weight_category_string.split(' - ')[1]

                print('It is OK untill now')

                if (categoria_sge == categoria_arena or categoria_sge == "") and valor['fighter']['isNotRanked'] is False: #and valor['fighter']['weightCategoryFullName'] == "Women's wrestling - U15 - 39 kg":

                    person_id = valor['fighter']['personId']
                    try:
                        custom_id = get_custom_id(headers, person_id)
                    except():
                        custom_id = ""

                    var_dict['id_evento'] = id_evento_sge
                    var_dict['id'] = ""
                    var_dict['id_evento_arena'] = str(valor['fighter']['sportEventId'])
                    var_dict['countFighters'] = str(valor['fighter']['weightCategoryCountReadyFighters'])
                    var_dict['countFights'] = str(valor['fighter']['weightCategoryCountFights'])
                    var_dict['weightCategoryFullName'] = str(valor['fighter']['weightCategoryFullName'])
                    var_dict["customId"] = str(custom_id)
                    var_dict['fullName'] = str(valor['fighter']['fullName'])
                    var_dict["rank"] = str(valor['fighter']['rank'])
                    if weight_category_string.split(' - ')[0] == "Freestyle":
                        var_dict['sportAlternateName'] = "FS"
                    elif weight_category_string.split(' - ')[0] == "Greco-Roman":
                        var_dict['sportAlternateName'] = "GR"
                    else:
                        var_dict['sportAlternateName'] = "WW"
                    var_dict['sportName'] = weight_category_string.split(' - ')[0]
                    var_dict['name'] = weight_category_string.split(' - ')[2]
                    var_dict['audienceName'] = categoria_arena

                    url_api = "https://restcbw.bigmidia.com/cbw/api/resultado-rank-arena"

                    json_payload = json.dumps(var_dict)

                    headers2 = {"Content-Type": "application/json"}

                    response = requests.post(url_api, data=json_payload, headers=headers2)

                    print(json_payload)
                    print(response.status_code)


        except AttributeError:

            for valor in range(len(ranking_categoria)):

                person_id = valor['fighter']['personId']
                custom_id = get_custom_id(headers, person_id)
                valor['fighter']['customId'] = custom_id
                all_data.append(valor['fighter'])

        except():
            pass
    messagebox.showinfo("Finished", "finish baby agatinha!")


def delete_ids_sge_range():

    x = simpledialog.askinteger("range inicial", "id")
    y = simpledialog.askinteger("range final", "id")
    a = x


    for items in range(x, y):

        url_api = f"https://restcbw.bigmidia.com/cbw/api/resultado-rank-arena/{a}"

        payload = {}
        headers2 = {}

        response = requests.delete(url_api, data=payload, headers=headers2)

        a += 1

        print(response.status_code)
    messagebox.showinfo("Finished", f"Cleanded Id Range {x}:{y}")


def delete_ids_sge():

    a = simpledialog.askstring("id a ser excluido", "informe o id")




    url_api = f"https://restcbw.bigmidia.com/cbw/api/resultado-rank-arena/{a}"

    payload = {}
    headers2 = {}

    response = requests.delete(url_api, data=payload, headers=headers2)


    print(response.status_code)

    messagebox.showinfo("Finished", f"Cleanded Id e {a}")


def update_sge():

    resultados_window = tk.Toplevel(root, bg="#2f2f2f")
    resultados_window.title("Manipulação de Resultados ")
    resultados_window.iconbitmap('icon 1.ico')
    resultados_window.configure(background="#2f2f2f", bg="#2f2f2f", highlightbackground="black", highlightcolor="black")

    estilos = ["Freestyle", "Greco-Roman", "Female wrestling"]

    estilo_combobox = ttk.Combobox(resultados_window, values=estilos, width=50)
    estilo_combobox.set("Estilo")
    estilo_combobox.grid(row=0, column=0, padx=10, pady=10)

    rotulos = ["Id SGE:", "Novo Rank:"]
    entradas = [tk.Entry(resultados_window, relief='groove', borderwidth=2),
               tk.Entry(resultados_window, relief='groove', borderwidth=2)]

    for i, label_text in enumerate(rotulos):
        tk.Label(resultados_window, text=label_text, anchor='w', **label_style).grid(row=i + 2, column=0, padx=10, pady=5,
                                                                        sticky='w')
        entradas[i].grid(row=i + 2, column=1, pady=5)
        entradas[i].config(**entry_style)


    # a = simpledialog.askstring("ID", "Qual ID?")
    # r = simpledialog.askstring("Rank", "Qual o novo rank?")
    # estilo = simpledialog.askstring("Estilo", "Qual o novo estilo?")



    def send_new_results():

        id_resultado = entradas[0].get()
        novo_resultado = entradas[1].get()

        print("id_do_resultado enviado",id_resultado)

        estilo = estilo_combobox.get()

        print("estilo novo", estilo)

        url_api = f"https://restcbw.bigmidia.com/cbw/api/resultado-rank-arena/{id_resultado}"

        headers = {"Content-Type": "application/json"}

        resultado_payload = requests.get(url_api).json()

        resultado_payload['rank'] = f'{novo_resultado}'

        if estilo == 'Freestyle':

            resultado_payload['sportAlternateName'] = 'FS'

        elif estilo == 'Greco-Roman':

            resultado_payload['sportAlternateName'] = 'GR'

        else:
            resultado_payload['sportAlternateName'] = 'WW'

        resultado_payload['weightCategoryFullName'] = (resultado_payload['weightCategoryFullName']

                                                       .replace(str(resultado_payload['sportName']), estilo))

        resultado_payload['sportName'] = f'{estilo}'

        resultado_payload['id_classe_peso'] = ''

        final_json_payload = json.dumps(resultado_payload)

        print(final_json_payload)

        requests.delete(url_api)

        url_post = 'https://restcbw.bigmidia.com/cbw/api/resultado-rank-arena'

        post = requests.post(url_post, data=final_json_payload, headers=headers)

        print(final_json_payload, post.status_code)

    button = tk.Button(resultados_window, text="Enviar", command=send_new_results, **button_style)
    button.grid(row=3, column=2, padx=5)


def post_bra_senior():

    file_path = "credentials.json"

    with open(file_path, "r") as f:
        credentials_data = json.load(f)

    file = f"C://Users//agata//CBW disco C//RESULTADOS ARENA 2023-AGOSTO//resultados individuais/BRA SR.xlsx"
    df = pd.read_excel(file)

    evento_sge, campeonatos_data = get_sge_event()

    id_evento_sge = campeonatos_data[evento_sge]['id_sge']
    categoria_sge = campeonatos_data[evento_sge]['age']



    var_dict = {}

    print('It is OK untill now')
    for index, linha in df.iterrows():

        weight_category_string = linha['weightCategoryFullName']
        categoria_arena = weight_category_string.split(' - ')[1]

        if (categoria_sge == categoria_arena or categoria_sge == "") and linha['isNotRanked'] is False:

            var_dict['id_evento'] = id_evento_sge
            var_dict['id'] = ""
            var_dict['id_evento_arena'] = str(linha['sportEventId'])
            var_dict['countFighters'] = str(linha['weightCategoryCountReadyFighters'])
            var_dict['countFights'] = str(linha['weightCategoryCountFights'])
            var_dict['weightCategoryFullName'] = str(linha['weightCategoryFullName'])
            var_dict["customId"] = str(linha['customId'])
            var_dict['fullName'] = str(linha['fullName'])
            var_dict["rank"] = str(linha['rank'])
            if weight_category_string.split(' - ')[0] == "Freestyle":
                var_dict['sportAlternateName'] = "FS"
            elif weight_category_string.split(' - ')[0] == "Greco-Roman":
                var_dict['sportAlternateName'] = "GR"
            else:
                var_dict['sportAlternateName'] = "WW"
            var_dict['sportName'] = weight_category_string.split(' - ')[0]
            var_dict['name'] = weight_category_string.split(' - ')[2]
            var_dict['audienceName'] = categoria_arena

            url_api = "https://restcbw.bigmidia.com/cbw/api/resultado-rank-arena"

            json_payload = json.dumps(var_dict)

            headers2 = {"Content-Type": "application/json"}

            response = requests.post(url_api, data=json_payload, headers=headers2)

            print(json_payload)
            print(response.status_code)


def get_fighters():

    categorias = get_weights_categories()

    for id, value in categorias.items():

        data = get_endpoint_response(get_headers(), f"fighter/list?fsportEventWeightCategoryId={id}")['fighters']

        data2 = pd.json_normalize(data)

        print(data2)


def get_weights_categories():

    weight_categories = get_endpoint_response(get_headers(), f"weight-category/{get_event_id()}")['weightCategories']
    categorias = {}

    for category in weight_categories:
        id_categoria = category['id']
        nome = category['shortName']
        categorias[id_categoria] = nome
    print(categorias)
    return categorias


def post_generate_automatic_draw():

    categorias = get_weights_categories()

    data = {"drawType": "block"}

    for id in categorias.keys():

        post_endpoint(get_headers(), f"weight-category/get/{id}/draw/auto", data)

    print("done")


def reset_all_draw():

    categorias = get_weights_categories()

    data = {}

    for id in categorias.keys():

        patch_endpoint(get_headers(), f"weight-category/get/{id}/draw/clear", data)

    print("done")


def delete_all_categorias():
    categorias = get_weights_categories()

    data = {}

    for id in categorias.keys():
        delete_endpoint(get_headers(), f"weight-category/get/{id}", data)

    print("done")


def get_brackets_pdf():

    h = get_headers()
    h['Content-Type'] = 'application/pdf'

    print(h)

    data = {}

    categorias = get_weights_categories()

    for id, value in categorias.items():
        params = {
            'print': 1,
            'showNumber': 1
        }

        pdf = requests.get(f"http://localhost:8080/api/json/weight-category/bracket/print?sportEventWeightCategoryId={id}", data=data, headers=h, params=params)

        #print(f"Content-Type: {pdf.headers.get('Content-Type')}")

        # pdf = requests.get(f"http://localhost:8080/bracket/weight-category/show/{id}/bracket/print?live=1")

        # print(pdf.text)

        with open(f'output_folder/{value}.pdf', 'wb') as file:

            file.write(pdf.content)

    print("done")


def load_whatsmart_table(ano):

    data = requests.get(f"https://whatsmat.uww.org/daten.php?pid=&suchart=nation&fland=6875342BCEB04CC48166C21C53A21C13&fvon={ano}&fbis=&fwkart=&fstil=&fakl=&fsort=0")

    soup = BeautifulSoup(data.text, 'html.parser')
    data = soup.find('table', {'class': 'normal'})

    df = pd.read_html(str(data), header=0)[0]

    def normalize_names(df):
        def normalize_name(name):
            parts = name.split(", ")
            last_name = parts[0]
            first_name = parts[1]
            new_name = f"{first_name} {last_name}"
            return new_name.upper()

        df['Name'] = df['Name'].apply(normalize_name)

        return df

    df = normalize_names(df)

    return df


def compare_events_box():



    df2 = main_atletas()



    data = load_whatsmart_table(2024)



    selection_window = tk.Toplevel(root, bg="#2f2f2f")
    selection_window.title("Selecione o Evento ")
    selection_window.iconbitmap('icon 1.ico')
    selection_window.configure(background="#2f2f2f", bg="#2f2f2f", highlightbackground="black", highlightcolor="black")

    with open("eventos sge 2024.json", "rb") as campeonatos_sge:
        campeonatos_data = json.load(campeonatos_sge)

    from bigmidia_restapi import get_ids_ano_eventos

    eventos_2024 = get_ids_ano_eventos([2024])

    # event_combobox = ttk.Combobox(selection_window, values=list(campeonatos_data.keys()), width=50)
    event_combobox = ttk.Combobox(selection_window, values=list(eventos_2024['descricao']), width=50)
    event_combobox.set("Selecione o evento do SGE")
    event_combobox.grid(row=0, column=0, padx=10, pady=10)

    international_event_combobox = ttk.Combobox(selection_window, values=list((data['Competition']+" - "+data['Place']).unique().tolist()), width=50)
    international_event_combobox.set("Selecione Evento Internacional")
    international_event_combobox.grid(row=0, column=1, padx=10, pady=10)

    def set_selected_events():

        global evento_sge
        evento_sge = event_combobox.get()

        global evento_uww
        evento_uww = international_event_combobox.get()

        selection_window.destroy()

        return evento_sge, evento_uww

    confirm_button = tk.Button(selection_window, text="Confirm", command=set_selected_events, **button_style,
                               width=10, relief='groove', borderwidth=2)
    confirm_button.grid(row=1, column=0, padx=10, pady=10)

    selection_window.wait_window(event_combobox)

    evento_selecionado_id = eventos_2024['id'][eventos_2024['descricao'] == evento_sge].iloc[0]

    def international_results_send(df, nome_sge, nome_uww, id_atleta, id_evento):

        data_load = {}

        data_load['id_evento'] = str(id_evento)
        data_load['id'] = ""
        data_load['id_evento_arena'] = ""
        data_load['countFighters'] = ""
        data_load['countFights'] = ""
        data_load["customId"] = str(id_atleta)
        data_load['fullName'] = nome_sge
        data_load["rank"] = str(int(df.loc[(df['Name'] == nome_uww), 'Rank'].values[0]))
        if df.loc[(df['Name'] == nome_uww), 'Style'].values[0] == "Freestyle":
            data_load['sportAlternateName'] = "FS"
        elif df.loc[(df['Name'] == nome_uww), 'Style'].values[0] == "Greco-Roman":
            data_load['sportAlternateName'] = "GR"
        else:
            data_load['sportAlternateName'] = "WW"
        data_load['sportName'] = df.loc[(df['Name'] == nome_uww), 'Style'].values[0]
        data_load['name'] = str(int(float(df.loc[(df['Name'] == nome_uww), 'Weight'].values[0]))) + " kg"
        data_load['audienceName'] = df.loc[(df['Name'] == nome_uww), 'Age Group'].values[0]

        data_load['weightCategoryFullName'] = (
                df.loc[(df['Name'] == nome_uww), 'Style'].values[0] + " - " +
                df.loc[(df['Name'] == nome_uww), 'Age Group'].values[0] + " - " +
                str(int(float(df.loc[(df['Name'] == nome_uww), 'Weight'].values[0]))) + " kg"
        )

        url_api = "https://restcbw.bigmidia.com/cbw/api/resultado-rank-arena"

        json_payload = json.dumps(data_load)

        headers2 = {"Content-Type": "application/json"}

        print(data_load)
        response = requests.post(url_api, data=json_payload, headers=headers2)

        print(response.status_code)



    def compare_athletes_uww_sge(df, df2):

        selection_window = tk.Toplevel(root, bg="#2f2f2f")
        selection_window.title("Match Athletes")
        selection_window.iconbitmap('icon 1.ico')
        selection_window.configure(background="#2f2f2f", bg="#2f2f2f", highlightbackground="black", highlightcolor="black")

        #uww_names_list = load_whatsmart_table(2024)['Name'].unique().tolist()

        #sge_names_list = main_atletas()['nome_completo'].unique().tolist()

        def get_id_by_name(df, name):

            filtered_df = df[df['nome_completo'] == name]

            if not filtered_df.empty:
                return filtered_df.iloc[0]['id']
            else:
                return None

        def find_similar_names(row, df2, threshold=90):
            similar_names = process.extract(row['Name'], df2['nome_completo'], limit=None)
            print(similar_names)
            result = []
            for name_score_tuple in similar_names:
                if name_score_tuple[1] >= threshold:
                    name_id_tuple = (name_score_tuple[0], get_id_by_name(df2, name_score_tuple[0]))
                    result.append(name_id_tuple)
            return result


        similar_names_dict = {row['Name']: find_similar_names(row, df2) for _, row in df.iterrows()}

        print(similar_names_dict)

        def normalize_names(lista):

            new_list = []

            for name in lista:

                try:

                    parts = name.split(", ")
                    last_name = parts[0]
                    first_name = parts[1]
                    new_name = f"{first_name} {last_name}"
                    new_list.append(new_name.upper())

                except:
                    new_list.append(name)

            return new_list

        #def update_names_list(*args):

            #search_string = entrada_var.get()
            #filtered_names = [name for name in sge_names_list if name.lower().startswith(search_string.lower())]
            #sge_name_combobox['values'] = filtered_names

        #uww_name_combobox = ttk.Combobox(selection_window, values=normalize_names(uww_names_list), width=50)
        #uww_name_combobox.set("Atleta a ser")
        #uww_name_combobox.grid(row=0, column=0, padx=10, pady=10)

        def on_select_change(event, row, labels):
            selection = event.widget.get()
            row_name = labels[row]['text']
            if selection != "":
                selected_name, selected_id = selection.split(':')
                similar_names_dict[row_name] = [(selected_name.strip(), int(selected_id.strip()))]
            else:
                similar_names_dict[row_name] = []

            return

        labels = []

        for idx, (_, row) in enumerate(df.iterrows()):
            label = tk.Label(selection_window, text=row['Name'], **label_style)
            label.grid(row=idx, column=0, padx=5, pady=5, sticky=tk.W)
            labels.append(label)

            values = [f"{name}: {id_}" for name, id_ in similar_names_dict[row['Name']]]
            values.insert(0, "")
            selection = ttk.Combobox(selection_window, values=values, width=25)
            selection.grid(row=idx, column=1, padx=5, pady=5)
            selection.bind("<<ComboboxSelected>>",
                           lambda event, row=idx, labels=labels: on_select_change(event, row, labels))
            selection.current(0)

            def send_results(selection, row, df, evento_selecionado_id):
                selection_value = selection.get()
                if selection_value:
                    name_id = selection_value.split(':')
                    if len(name_id) >= 2:
                        name = name_id[0].strip()
                        id_ = int(name_id[1].strip())
                        international_results_send(df, name, row["Name"], id_, evento_selecionado_id)
                    else:
                        print("Selection value is not in the expected format")
                else:
                    print("Selection value is empty")

            send_button = tk.Button(selection_window, text="Enviar", command=lambda s=selection, r=row: send_results(s, r, df, evento_selecionado_id), **button_style)
            send_button.grid(row=idx, column=2, padx=5, pady=5)


        #sge_names_list = main_atletas()['nome_completo'].unique().tolist()

        #entrada_var = StringVar()
        #sge_name_combobox = ttk.Combobox(selection_window, textvariable=entrada_var, values=sge_names_list, width=50)
        #sge_name_combobox.set("Atleta Sge")
        #sge_name_combobox.grid(row=0, column=1, padx=10, pady=10)
        #sge_name_combobox.bind("<KeyRelease>", update_names_list)

    compare_athletes_uww_sge(data[(data['Competition']+" - "+data['Place']) == evento_uww], df2)


def situacao():

    data = {'sessionType': '1day'}

    patch_endpoint(get_headers(), "sport-event/get/1ef06f5f-83af-6bb6-9093-7b50a7a7b5dc", data)



def print_events():

    print(get_endpoint_response(get_headers(), "sport-event/get/1ef06f5f-83af-6bb6-9093-7b50a7a7b5dc"))







root = tk.Tk()
root.title("Arena Integrated Aplication GUI")

# Configure the window background and dimensions
root.configure(background="#2f2f2f", bg="#2f2f2f", highlightbackground="black", highlightcolor="black", width= 100)


root.iconbitmap('icon 1.ico')

# Create labels and entry widgets for each credential
label_style = {"bg": "#2f2f2f", "fg": "white", "font": ("Roboto", 9)}
entry_style = {"bg": "#585858", "fg": "white", "font": ("Roboto", 9), "width": 35}


labels = ["API Key:", "Client ID:", "Client Secret:", "IP:", "Event ID:", "Directory:", "Machine Name:"]
entries = [tk.Entry(root, relief='groove', borderwidth=2),
           tk.Entry(root, relief='groove', borderwidth=2),
           tk.Entry(root, show="*", relief='groove', borderwidth=2),
           tk.Entry(root, relief='groove', borderwidth=2),
           tk.Entry(root, relief='groove', borderwidth=2),
           tk.Entry(root, relief='groove', borderwidth=2),
           tk.Entry(root, relief='groove', borderwidth=2)]

for i, label_text in enumerate(labels):
    tk.Label(root, text=label_text, anchor='w', **label_style).grid(row=i+2, column=0, padx=10, pady=5, sticky='w')
    entries[i].grid(row=i+2, column=1, pady=5)
    entries[i].config(**entry_style)

# Set additional configurations for Combobox and Buttons
user_name_combobox_label = (tk.Label(root, text="Maquina/Evento", **label_style))
user_name_combobox_label.grid(row=0, column=0)

user_name_combobox = ttk.Combobox(root, values=load_user_names(), width=38)
user_name_combobox.grid(row=0, column=1, pady=5)
user_name_combobox.bind('<<ComboboxSelected>>', show_credentials_infos)

button_style = {"bg": "#2f2f2f", "fg": "white", "font": ("Roboto", 9)}

browse_button = tk.Button(root, text="Selecionar", command=browse_directory, **button_style,
                          width=10, relief='groove', borderwidth=2)
browse_button.grid(row=7, column=2, padx=5)
save_button = tk.Button(root, text="Salvar", command=save_arena_credentials, **button_style,
                        width=10, relief='groove', borderwidth=2)
save_button.grid(row=8, column=2)


buttons = [

    ("Save Credentials", save_arena_credentials),
    ("Dados de Lutas", run_main_program),
    ("Resultado Geral de Times", get_teams_ranking),
    ("Resultados por Luta", run_fights_info),
    ("Limpar Sessão", clear_fights),
    ("Gerar Planilha com Perdedores das Oitava/Quartas", get_eight_quarter_losers)
]

# for i, (text, command) in enumerate(buttons):

# tk.Button(root, text=text, command=command, **button_style).grid(row=9 + i, column=0, padx=10)

menu_bar = tk.Menu(root, cursor='cross', borderwidth="10px")


relatorios_menu = tk.Menu(menu_bar, tearoff=0, cursor='hand1')

menu_bar.add_cascade(label="Relatórios e Resultados", menu=relatorios_menu)

relatorios_menu.add_command(label="Rodar resultados individuais", command=run_main_program)
relatorios_menu.add_command(label="resultados de luta a luta", command=run_fights_info)
relatorios_menu.add_command(label="Rodar Oitavas/Quartas", command=get_eight_quarter_losers)
relatorios_menu.add_command(label="Gerar Pontuações", command=get_teams_ranking)
relatorios_menu.add_command(label="Lista nova de inscritos", command=get_fighters)


implementacoes_menu = tk.Menu(menu_bar, tearoff=0, cursor='hand1')
menu_bar.add_cascade(label="Implementações no Arena", menu=implementacoes_menu)
implementacoes_menu.add_command(label="Ver Categorias", command=run_selecionar_categorias)
implementacoes_menu.add_command(label="Clear Fights", command=clear_fights)
implementacoes_menu.add_command(label="Limpar Luta X", command=try_cleaning)
implementacoes_menu.add_command(label="Generate Auto Draw", command=post_generate_automatic_draw)
implementacoes_menu.add_command(label="Clear All Draw", command=reset_all_draw)
implementacoes_menu.add_command(label="print brackets", command=get_brackets_pdf)
implementacoes_menu.add_command(label="Delete All WCategories", command=delete_all_categorias)
implementacoes_menu.add_command(label="Get test info", command=situacao)
implementacoes_menu.add_command(label="clear age group", command=clear_fights_for_age_group)


help_menu = tk.Menu(menu_bar, tearoff=0)
menu_bar.add_cascade(label="Downloads", menu=help_menu)
help_menu.add_command(label="Biaxar Credenciais", command=save_credentials_stored)

def get_fights_from():

    sportEventId = get_event_id()

    headers = get_headers()

    fights_response = get_endpoint_response(headers, f'fight/{sportEventId}')['fights']

    lista_de_vencedores_rs = {}

    for luta in fights_response:

        victory_type = luta['rankingPoint']['victoryTypeId']
        winner_id = luta['winnerFighter']
        winner_team = luta['winnerTeamAlternateName']
        round_name = luta['roundFriendlyName']
        estilo = luta['sportName']
        audience = luta['audienceName']
        peso = luta['weightCategoryName']

        if victory_type != "VFO" and victory_type != '2DSQ' and victory_type != '2VFO':

            if winner_id not in lista_de_vencedores_rs:
                lista_de_vencedores_rs[winner_id] = []

            lista_de_vencedores_rs[winner_id].append({'id_estabelecimento': winner_team,
                                                      'sportName': estilo,
                                                      'name': peso,
                                                      'audienceName': audience,
                                                      'victory_type': victory_type})



    print(json.dumps(lista_de_vencedores_rs))

api_menu = tk.Menu(menu_bar, tearoff=0)
menu_bar.add_cascade(label="Integração API", menu=api_menu)
api_menu.add_command(label="Post SGE Events Results", command=post_results_sge)
api_menu.add_command(label="Excluir Resultados por ID", command=delete_ids_sge)
api_menu.add_command(label="Uppar Bra senior", command=post_bra_senior)
api_menu.add_command(label="Atualizar Resultados por ID", command=update_sge)
api_menu.add_command(label="Excluir Resultados por ID RANGE", command=delete_ids_sge_range)
api_menu.add_command(label="Match Resultados Internacionais", command=compare_events_box)
api_menu.add_command(label="test_por_equipes", command=get_fights_from)

root.config(menu=menu_bar)

root.mainloop()

