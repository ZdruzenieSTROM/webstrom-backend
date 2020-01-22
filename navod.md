# Návod na spustenie

Naklonuj si projekt z GitHubu:

```shell
git clone https://github.com/zdruzeniestrom/webstrom
cd webstrom
```

Vytvor a aktivuj prostredie pre python:

Linux:

```shell
python3 -m venv <názov prostredia>
source <názov prostredia>/bin/activate
```

Windows:

```batch
py -m venv <názov prostredia>
call <názov prostredia>\Scripts\activate.bat
```

*Ak si prostredie pre python vytváraš v priečinku so stránkou, nezabudni pridať priečinok s prostredím do `.gitignore`*

Nainštaluj potrebné balíky:

```shell
pip install -r requirements.txt
```

Vytvor migračné modely a databázu:

```shell
python manage.py makemigrations
python manage.py migrate
```

Vytvor superusera:

```shell
python manage.py createsuperuser
```

Spusti lokálny vývojový server:

```shell
python manage.py runserver
```