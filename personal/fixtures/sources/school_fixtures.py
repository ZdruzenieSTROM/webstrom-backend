#!/usr/bin/env python3

import json
import math
import re

import pandas as pd
import unidecode
import wget

kraje = 'kraje.xlsx'
okresy = 'okresy.xlsx'
files = ['SOS_Z.XLS', 'zs_z.xls', 'GYM_Z.XLS', '']
output_format = 'json'


def remove_vowels(s):
    return re.sub('[aeiouy]', '', s)


def download_files():
    # TODO: Stiahnut zo stranok ministerstva správne súbory
    pass


def get_number(address):
    f = re.findall(r'\d+', address)
    if len(f) == 0:
        print(address)
        return '', 0
    elif int(f[-1]) > 999:
        return '', 0
    else:
        return f[-1], int(math.log10(int(f[-1])))+1


def create_abbreviation(nazov_skoly, ulica, mesto, okres):
    pure_ulica = re.sub(r'\W+', '', unidecode.unidecode(ulica))
    pure_mesto = remove_vowels(re.sub(r'\W+', '', unidecode.unidecode(mesto)))
    number, l = get_number(ulica)
    return nazov_skoly[0]+pure_ulica[0:5-l]+str(number)+okres


def nacitaj_kraje(file):
    df_kraje = pd.read_excel(file, header=0)
    print(f'Zo súboru {file} bolo načítaných {df_kraje.shape[0]} krajov')
    if output_format == 'csv':
        df_kraje.to_csv('kraje.csv')
    elif output_format == 'json':
        df_kraje.to_json('kraje.json', orient='records', force_ascii=False)
    print(f'Kraje boli exportované do kraje.{output_format}')


def nacitaj_okresy(file):
    df_okresy = pd.read_excel(file, header=0)
    df_okresy['county'] = list(map(lambda x: x//100, list(df_okresy['code'])))

    print(f'Zo súboru {file} bolo načítaných {df_okresy.shape[0]} okresov')

    # Export do csv
    if output_format == 'csv':
        df_okresy = df_okresy.set_index('code')
        df_okresy.to_csv('okresy.csv')
    elif output_format == 'json':
        df_okresy.to_json('okresy.json', orient='records', force_ascii=False)
    print(f'Okresy boli exportované do okresy.{output_format}')
    df_okresy = df_okresy.set_index('code')
    return df_okresy


def load_schools():
    celkove_duplicity = 0
    df_okresy = nacitaj_okresy(okresy)
    df_all = pd.DataFrame()
    for file in files:
        df = pd.read_excel(file, usecols="A,C,G,H,I,J,L")

        # Vymaz odveci riadky
        i = 0
        while pd.isna(df.iloc[0][1]):
            print(f'{file}: Vynechaný riadok {i}')
            df = df.drop(df.index[0])
            i += 1

        # Prvý nevymazany riadok je hlavicka
        df.columns = df.iloc[0]
        df = df.drop(df.index[0])

        # Upravit typy a pripravit na join
        df = df.astype({'okres': 'int64'})
        df_okresy = df_okresy.rename(columns={'name': 'nazov_okresu'})
        df_okresy = df_okresy.rename(
            columns={'abbreviation': 'dist_abbreviation'})
        df = df.join(df_okresy, on='okres')

        # df['skratka'] = list(map(create_abbreviation_x ,list(df['nazov']),list(df['ulica']),list(df['skratka_okresu'])))
        df['skratka'] = list(map(create_abbreviation, list(df['nazov']), list(
            df['ulica']), list(df['miesto']), list(df['dist_abbreviation'])))

        skratky = set([])
        dupl = 0
        for a in df['skratka']:
            if a in skratky:
                print(f'Duplicitná skratka: {a}')
                dupl += 1
            else:
                skratky.add(a)
        print(f'Bolo nájdených {dupl} duplictít')

        # Nakumulovat do jedného framu
        if df_all.empty:
            df_all = df
        else:
            df_all = pd.concat([df_all, df])

        print(f'Zo súboru {file} bolo načítaných {df.shape[0]} škôl')
        celkove_duplicity += dupl

    # Ukladanie skol
    rename_dict = {
        'kodsko': 'code',
        'okres': 'district',
        'nazov': 'name',
        'ulica': 'street',
        'miesto': 'city',
        'psc': 'zip_code',
        'skratka': 'abbreviation'
    }

    df_all = df_all.rename(columns=rename_dict)
    columns_to_save = ['code', 'district', 'name', 'street',
                       'city', 'zip_code', 'email', 'abbreviation']

    if output_format == 'csv':
        df_all.to_csv('skoly.csv', columns=columns_to_save, index=False)
    elif output_format == 'json':
        df_all = df_all[columns_to_save]
        df_all.to_json('skoly.json', orient='records', force_ascii=False)
    print(f'Do súboru skoly.csv bolo vyexportovaných {df_all.shape[0]} škôl')
    print(f'Dokopy identifikovaných {celkove_duplicity} duplicít')


def transform_json_to_django_format(file_names, primary_keys, model_names, output_file):
    data = []
    for file_name, primary_key, model_name in zip(file_names, primary_keys, model_names):
        with open(file_name) as json_file:
            content = json.load(json_file)
            for item in content:
                pk = item[primary_key]
                del item[primary_key]
                json_obj = {
                    "model": model_name,
                    "pk": pk,
                    "fields": item}
                data.append(json_obj)

    with open(output_file, 'w') as outfile:
        json.dump(data, outfile, indent=4)


if __name__ == "__main__":
    # nacitaj_kraje(kraje)
    # load_schools()
    # transform_json_to_django_format(['kraje.json'], ['code'], [
    #                                 'user.County'], 'counties.json')
    # transform_json_to_django_format(['okresy.json'], ['code'], [
    #                                 'user.District'], 'districts.json')
    # transform_json_to_django_format(['skoly.json'], ['code'], [
    #                                 'user.School'], 'schools.json')
    with open('../schools.json', 'r') as f:
        schools = json.load(f)
    code_to_email = {school['pk']: school['fields'].get('email')
                     for school in schools}
    with open('../districts.json', 'r') as f:
        districts = json.load(f)
    district_to_shortcut = {
        district['pk']: district['fields']['abbreviation'] for district in districts}
    print(district_to_shortcut)
    df = pd.read_excel('SOS_Z.xls', header=1)
    df = df.rename({
        'kodsko': 'code',
        'okres': 'district_id',
        'nazov': 'name',
        'ulica': 'street',
        'psc': 'zip_code',
        'miesto': 'city',

    }, axis=1)
    print(df)
    df['email'] = df['code'].apply(lambda code: code_to_email.get(code))
    df['abbreviation'] = df.apply(lambda row: create_abbreviation(
        row['name'], row['street'], row['city'], district_to_shortcut[row['district_id']]), axis=1)
    df = df.drop(['rok', 'zriadz', 'eduid', 'kraj', 'druh',
                  'jazyk', 'adrwww',  'ziaci'], axis=1)
    df = df.reindex(['code', 'name', 'abbreviation', 'street',
                    'city', 'zip_code', 'email', 'district_id'], axis=1)
    df.to_csv('school_sos.csv', index=False)
