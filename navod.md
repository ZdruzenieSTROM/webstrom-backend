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

**Ak si prostredie pre python vytváraš v priečinku so stránkou, nezabudni pridať priečinok s prostredím do `.gitignore`**

Nainštaluj potrebné balíky:

```shell
pip install -r requirements.txt
```

**Package `pdf2image` používa externé programy, zariaď, aby si ich mal nainštalované ([dokumentácia](https://pypi.org/project/pdf2image/))**

Vytvor a naplň databázu:

```shell
python manage.py restoredb
```

Spusti lokálny vývojový server:

```shell
python manage.py runserver
```

# Nastavenia linteru a formátovaču

## Linter

VSCode python extension podporuje viacero linterov, medzi nimi aj `pylint`. Aby si ho mohol používať, potrebuješ mať **vo vnútri virtual environmentu** nainštalovaný package `pylint` a `pylint-django`. Ďalej treba VSCodu povedať, aby pri spustení linteru načítal djangový plugin, teda do workspace settings (`${workspaceFolder}/.vscode/settings.json`) treba pridať

```json
"python.linting.pylintArgs": [
    "--load-plugins",
    "pylint_django"
]
```

Teraz ak nemáš nejak veľmi zle nastavený globálny config, mal by ťa linter začať šikanovať tým, že ti bude podfarbovať kusy kódu a pridávať položky do panelu `PROBLEMS`.

## Formátovač

Nainštaluj si (opäť, vo vnútri svojho virtual environmentu) package `autopep8`. Okrem toho potrebuješ zapnúť `editor.formatOnSave` (defaultne je vypnuté), buď v globálnom configu alebo len lokálne vo projekte (odporúčam globálne).
