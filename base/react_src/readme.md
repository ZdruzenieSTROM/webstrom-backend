# React na stránke

React sa na našej stránke používa iba na vytváranie vlastných elementov, ktoré sú aspoň čiastočne interaktívne, menia svoj stav alebo načítavajú dáta zo stránky. Samozrejme, ak React používať nechcem, môžem celý priečinok `base/react_src` s reaktom úplne odignorovať a nič sa nestane :)

## Ako používať React

Ak je už vytvorený nejaký custom element v Reacte, môžem ho používať bez ohľadu na to, či viem ako vznikol. Príkladom je element `example-element` ktorý sa dá používať jednoducho pomocou `div` elementu ktorému nastavím `class` s rovnakým menom:

```html
  <div class="example-element"></div>
```
React potom zariadí aby sa tento element naplnil kódom definovaným v React priečinku.

## Definovanie vlastného elementu

Na vytvorenie nového elementu je potrebných len pár krokov, ale hlavne znalosť Reactu

- Vytvoriť `.js` súbor s React componentom. Napríklad `ExampleElement.js` v React priečinku na stránke.
- Nahradiť kód v custom elemente v html kóde týmto React componentom. Koniec `ExampleElement.js` súboru.
- Importnúť tento custom element do `index.js` v React priečinku `base/react_src`.
- Transpilenúť kód do JavaScriptu čitateľného všetkými priehliadačmi. Je na to pripravený prikaz:
```sh
  base/react_src>  npm run dev
```
Tento príkaz vytvorí v `base/static/js` súbor `main.js` ktorý obsahuje všetko potrebné na to, aby tieto custom elementy fungovali.


## Inštalácia potrebných balíkov

V prvom rade je potrebné mať nainštalovaný [Node.js](https://nodejs.org/) pomocou ktorého nainštalujeme všetky potrebné balíky.

Najskôr sa musíme dostať do React priačinka:

```sh
  cd base/react_src
```

V tomto priečinku je už rpedpripravený `package.json` súbor, ktorý obsahuje všetky potrebné balíky. Nainšatujeme ich pomocou:

```sh
  npm install
```
alebo
```sh
  npm i
```

