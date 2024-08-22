
def get_fights_from():

    sportEventId = get_event_id()

    headers = get_headers()

    fights_response = get_endpoint_response(headers, f'fight/{sportEventId}')['fights']

    lista_de_vencedores_rs = []



    for luta in fights_response:


        victory_type = luta['rankingPoint']['victoryTypeId']
        winner_id = luta['winnerFighter']
        winner_team = luta['winnerTeamAlternateName']
        round_name = luta['roundFriendlyName']
        estilo = luta['sportName']
        audience = luta['audienceName']
        peso = luta['weightCategoryName']

        if victory_type != "VFO" and victory_type != '2DSQ' and victory_type != '2VFO':

            lista_de_vencedores_rs.append({winner_id, winner_team, estilo, peso, audience})



        f1_nome = luta["fighter1FullName"]
        f1_draw_number = luta['fighter1DrawRank']
        f2_nome = luta["fighter2FullName"]
        f2_draw_number = luta['fighter2DrawRank']
        f1_cp = luta["fighter1RankingPoint"]
        f2_cp = luta["fighter2RankingPoint"]
        team_1 = luta['team1Name']
        team_2 = luta['team2Name']
        team1 = luta['team1AlternateName']
        team2 = luta['team2AlternateName']
        check_rank = luta['rankingCheck']
        tech_check = luta['technicalCheck']
        weight_category_id = luta["sportEventWeightCategoryId"]
        is_round_robin = luta['isRobinGroupFight']

        print(round_name, "pontos atleta 1:", f1_cp, "pontos atleta 2:", f2_cp)

        if f1_cp != 1 and f1_cp != 0:

            print("atleta 1 ganhou, linha adicionada")

            dict_lutas_vencidas['id_evento'] = sportEventId
            dict_lutas_vencidas['id'] = ''
            dict_lutas_vencidas['id_evento_arena'] = ''
            dict_lutas_vencidas['countFighters'] = ''
            dict_lutas_vencidas['countFights'] = ''
            dict_lutas_vencidas['weightCategoryFullName'] = ''
            dict_lutas_vencidas["customId"] = ''
            dict_lutas_vencidas['fullName'] = f1_nome
            dict_lutas_vencidas["rank"] = ''
            dict_lutas_vencidas['sportName'] = estilo
            dict_lutas_vencidas['name'] = peso
            dict_lutas_vencidas['audienceName'] = audience
            dict_lutas_vencidas['id_estabelecimento'] = team1

            json_payload = json.dumps(dict_lutas_vencidas)
            print(dict_lutas_vencidas)

        elif f2_cp != 1 and f2_cp != 0:

            dict_lutas_vencidas = {}

            print("atleta 2 ganhou, linha adicionada")

            dict_lutas_vencidas['id_evento'] = sportEventId
            dict_lutas_vencidas['id'] = f2_nome
            dict_lutas_vencidas['id_evento_arena'] = ''
            dict_lutas_vencidas['countFighters'] = ''
            dict_lutas_vencidas['countFights'] = ''
            dict_lutas_vencidas['weightCategoryFullName'] = ''
            dict_lutas_vencidas["customId"] = ''
            dict_lutas_vencidas['fullName'] = ''
            dict_lutas_vencidas["rank"] = ''
            dict_lutas_vencidas['sportName'] = estilo
            dict_lutas_vencidas['name'] = peso
            dict_lutas_vencidas['audienceName'] = audience
            dict_lutas_vencidas['id_estabelecimento'] = team2

            json_payload = json.dumps(dict_lutas_vencidas)

            print(dict_lutas_vencidas)

        breakpoint()