from bigmidia_restapi import *
import math

caminho_1 =r"C:\Users\agata\CBW 2024\relatorios de inscrição eventos sge\clubes\cbi u20.xlsx"

caminho_2 = r"C:\Users\agata\CBW 2024\relatorios de inscrição eventos sge\clubes\cbi u17.xlsx"

caminho_3 = r"C:\Users\agata\CBW 2024\relatorios de inscrição eventos sge\clubes\cbi u15.xlsx"

df1 = pd.read_excel(caminho_1)

df2 = pd.read_excel(caminho_2)

df3 = pd.read_excel(caminho_3)

geral = pd.concat([df1, df2, df3], ignore_index=True)



def merge_cnpj_cbc (df_a_analisar):


  df_estabelecimento = main_estabelecimento()

  cbc_merged = pd.merge(df_a_analisar, df_estabelecimento, how='outer', right_on='descricao', left_on='Clube')

  cbc_merged.to_excel(r"C:\Users\agata\CBW 2024\eventos 2024\CBI INDIVIDUAL DA BASE\cbi_por_equipes_com_cnpj.xlsx")

  # .drop_duplicates(subset=['cnpj'])

  # geral.to_excel(r"C:\Users\agata\CBW 2024\relatorios de inscrição eventos sge\clubes\concat_cbi_da_base.xlsx")

def incluir_cabecas_de_chave(df_inscritos):

    df_inscritos['concat_values'] = df_inscritos.apply(lambda x: str(x['Age Group']) + str(x['Discipline']) + str(x['Weight Category']), axis=1)

    url_lista_peso = f"https://www.cbw.org.br/api/evento-atleta/rank-lista-pesos"

    response_pesos = requests.get(url_lista_peso).json()['items']['2023']['GERAL']

    dfs = []

    estilo_map = {'Estilo Livre - Fem.': 'WW', 'Estilo Livre - Masc.': 'FS', 'Greco-Romano - Masc.': 'GR'}

    idade_map = {'Infantil 11 e 12': 'inf 11-12', 'Sênior': 'seniors', 'Sub-15': 'u15', 'Sub-17': 'u17', 'Sub-20': 'u20',
                 'Veteranos A': 'veterans-a'}

    for estilo, age_groups in response_pesos.items():

        for age_group, weights in age_groups.items():

            df = pd.json_normalize(weights)

            df['estilo'] = estilo

            df['age_group'] = age_group

            df['style'] = df['estilo'].map(estilo_map)

            df['age_group'] = df['age_group'].map(idade_map)

            dfs.append(df)

    result_df = pd.concat(dfs, ignore_index=True)

    result_df['weight'] = [str(values['peso']).replace("kg", "") for index, values in result_df.iterrows()]

    result_df['concat_values'] = result_df['age_group']+result_df['style']+result_df['weight']



    merged = pd.merge(df_inscritos,
                      result_df,
                      how='left',
                      on='concat_values')

    evento_unique_classes_ids = list(merged['id_classe_peso'].unique())

    merged.to_excel(r"C:\Users\agata\CBW 2024\relatorios de inscrição eventos sge\federacoes\join view.xlsx")

    final_df_list = []

    evento_unique_classes_ids = [x for x in evento_unique_classes_ids if not math.isnan(x)]

    print(len(evento_unique_classes_ids))


    for classes in evento_unique_classes_ids:

        def return_rank_for_class_id(classe):

            headers = {}
            headers = []

            try:
                url_rank_category = f"https://www.cbw.org.br/api/evento-atleta/rank-atual?sort=colocacao&ano=2024&grupo=GERAL&id_classe_peso="
                querys =f'{classe}'
                page_count = requests.get(f"{url_rank_category}{querys}").json()["_meta"]["page_count"]
                # response_ranking = requests.get(url_rank_category).json()['items']

                with ThreadPoolExecutor() as executor:

                    dfs = executor.map(lambda page: fetch_data(url_rank_category, querys, headers, page), range(1, page_count + 1))

                final_df = pd.concat(dfs, ignore_index=True)

            except:

                url_rank_category = f"https://www.cbw.org.br/api/evento-atleta/rank-atual?sort=colocacao&ano=2023&grupo=GERAL&id_classe_peso="
                querys = f'{classe}'
                page_count = requests.get(f"{url_rank_category}{querys}").json()["_meta"]["page_count"]
                # response_ranking = requests.get(url_rank_category).json()['items']

                with ThreadPoolExecutor() as executor:

                    dfs = executor.map(lambda page: fetch_data(url_rank_category, querys, headers, page),
                                       range(1, page_count + 1))

                final_df = pd.concat(dfs, ignore_index=True)


            return final_df

        dict_ranking_id = {}

        filtered_merged = merged[merged['id_classe_peso'] == classes]

        dfff = return_rank_for_class_id(classes)

        for index, atleta in dfff.iterrows():

            if atleta['categoria'] != "Sub-15" and "inf" not in atleta['categoria'] and "vete" not in atleta['categoria']:

                id_atleta = atleta['id_atleta']
                rank = int(atleta['colocacao'])

                dict_ranking_id[id_atleta] = rank

                for index, row in filtered_merged.iterrows():


                    if int(row['Custom Id']) == int(id_atleta) and rank <= 4:

                        print('atleta rankeado')

                        filtered_merged.loc[index, 'rank'] = rank

        try:

            filtered_merged['Seed Number'] = filtered_merged['rank'].rank(method='dense')

        except:

            pass

        final_df_list.append(filtered_merged)

    final_df_com_cabecas_de_chave = pd.concat(final_df_list, ignore_index=True)

    final_df_com_cabecas_de_chave.to_excel(r"C:\Users\agata\CBW 2024\relatorios de inscrição eventos sge\federacoes\CIRCUITO NORTE NORDESTE_com_cabeça_de_chave.xlsx")


if __name__ == '__main__':

    df_inscritos = pd.read_excel(r"C:\Users\agata\CBW 2024\relatorios de inscrição eventos sge\federacoes\circuito norte-nordeste.xlsx")

    incluir_cabecas_de_chave(df_inscritos)

    #df_cbc = pd.read_excel(r"C:\Users\agata\CBW 2024\eventos 2024\CBI INDIVIDUAL DA BASE\cbi por equipes.xlsx")

    #merge_cnpj_cbc(df_cbc)