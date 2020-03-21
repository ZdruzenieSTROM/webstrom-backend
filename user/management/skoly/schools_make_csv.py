import pandas as pd
import re
import unidecode
import wget
import math



kraje = 'kraje.xlsx'
okresy = 'okresy.xlsx'
files = ['SOS_Z.XLS','zs_z.xls','GYM_Z.XLS']

def remove_vowels(s):
    return re.sub('[aeiouy]','',s)

def download_files():
    #TODO: Stiahnut zo stranok ministerstva správne súbory
    pass

def get_number(address):
    f = re.findall(r'\d+', address)
    if len(f)==0:
        print(address)
        return '',0
    elif int(f[-1])>999:
        return '',0
    else:
        return f[-1],int(math.log10(int(f[-1])))+1

def create_abbreviation(nazov_skoly,ulica,mesto,okres):
    pure_ulica = re.sub(r'\W+', '', unidecode.unidecode(ulica))
    pure_mesto = remove_vowels(re.sub(r'\W+', '', unidecode.unidecode(mesto)))
    number, l = get_number(ulica)
    return nazov_skoly[0]+pure_ulica[0:5-l]+str(number)+okres 

def nacitaj_kraje(file):
    df_kraje = pd.read_excel(file,header=0)
    print(f'Zo súboru {file} bolo načítaných {df_kraje.shape[0]} krajov')
    df_kraje.to_csv('kraje.csv')
    print('Kraje boli exportované do kraje.csv')

def nacitaj_okresy(file):
    df_okresy = pd.read_excel(file,header=0)
    df_okresy['kraj'] = list(map(lambda x: x//100, list(df_okresy['kod'])))
    df_okresy = df_okresy.set_index('kod')
    print(f'Zo súboru {file} bolo načítaných {df_okresy.shape[0]} okresov')

    #Export do csv
    df_okresy.to_csv('okresy.csv')
    print('Okresy boli exportované do okresy.csv')

    return df_okresy

def load_schools():
    celkove_duplicity = 0
    df_okresy = nacitaj_okresy(okresy)
    df_all=pd.DataFrame()
    for file in files:
        df = pd.read_excel(file, usecols="A,C,G,H,I,J,L")

        #Vymaz odveci riadky
        i=0
        while pd.isna(df.iloc[0][1]):
            print(f'{file}: Vynechaný riadok {i}')
            df = df.drop(df.index[0])
            i+=1
        
        # Prvý nevymazany riadok je hlavicka
        df.columns = df.iloc[0]
        df = df.drop(df.index[0])

        #Upravit typy a pripravit na join
        df = df.astype({'okres':'int64'})
        df_okresy = df_okresy.rename(columns={'nazov':'nazov_okresu'})

        df = df.join(df_okresy, on='okres')
        #df['skratka'] = list(map(create_abbreviation_x ,list(df['nazov']),list(df['ulica']),list(df['skratka_okresu'])))
        df['skratka'] = list(map(create_abbreviation ,list(df['nazov']),list(df['ulica']),list(df['miesto']),list(df['skratka_okresu'])))
        
        skratky = set([])
        dupl = 0
        for a in df['skratka']:
            if a in skratky:
                print(f'Duplicitná skratka: {a}')
                dupl+=1
            else:
                skratky.add(a)
        print(f'Bolo nájdených {dupl} duplictít')

        #Nakumulovat do jedného framu
        if df_all.empty:
            df_all=df
        else:
            df_all = pd.concat([df_all, df])

        print(f'Zo súboru {file} bolo načítaných {df.shape[0]} škôl')
        celkove_duplicity += dupl

    #Ukladanie skol
    rename_dict = {
        'kodsko': 'code',
        'okres': 'district',
        'nazov': 'name',
        'ulica': 'street',
        'miesto': 'city',
        'psc': 'zip_code',
        'skratka':'abbreviation'
    }


    df_all = df_all.rename(columns=rename_dict)
    columns_to_save = ['code','district','name','street','city','zip_code','email','abbreviation']
    df_all.to_csv('skoly.csv', columns=columns_to_save,index=False)
    print(f'Do súboru skoly.csv bolo vyexportovaných {df_all.shape[0]} škôl')
    print(f'Dokopy identifikovaných {celkove_duplicity} duplicít')

nacitaj_kraje(kraje)
load_schools()
