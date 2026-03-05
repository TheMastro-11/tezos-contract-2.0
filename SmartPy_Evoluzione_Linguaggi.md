# L'Evoluzione di SmartPy

## Trasformazione Architetturale a Livello di Linguaggio e il Suo Impatto sulla Progettazione degli Smart Contract su Tezos

------------------------------------------------------------------------

## Abstract

Questo report analizza l'evoluzione del linguaggio
e framework SmartPy negli ultimi anni, concentrandosi sulla transizione
architetturale dal modello legacy orientato a DSL al moderno design
basato su moduli.

Piuttosto che focalizzarsi esclusivamente su singoli refactoring di
contratti, questo lavoro esamina come i cambiamenti sistemici in SmartPy
abbiano influenzato la struttura degli smart contract, i modelli di
tipizzazione, la gestione dello storage, il flusso di controllo e i
pattern di governance.

------------------------------------------------------------------------

# 1. Introduzione

SmartPy è un linguaggio e framework di alto livello per scrivere smart
contract su Tezos utilizzando Python. Nel tempo, SmartPy ha subito
cambiamenti strutturali significativi finalizzati a:

-   Ridurre la verbosità della DSL
-   Allinearsi maggiormente alla semantica di Python
-   Migliorare la modularità
-   Semplificare la compilazione in Michelson
-   Migliorare la leggibilità e l'ergonomia per gli sviluppatori

Secondo la documentazione ufficiale di SmartPy:

> "SmartPy è una libreria Python per scrivere smart contract su Tezos."

La documentazione più recente introduce l'architettura modulare:

> "I moduli consentono di raggruppare contratti e tipi in modo
> strutturato."

L'evoluzione riflette un passaggio da una DSL che rispecchiava Michelson
a un paradigma di modellazione dei contratti integrato in Python.

------------------------------------------------------------------------

# 2. Panoramica Storica dell'Architettura di SmartPy

## 2.1 SmartPy Legacy (Era Pre-Moduli)

Caratteristiche principali:

-   `class Contract(sp.Contract)`
-   Storage definito tramite `self.init(...)`
-   `@sp.entry_point`
-   `sp.verify(...)`
-   Flusso di controllo in stile DSL (`sp.if`, `sp.for`)
-   Tipi Michelson espliciti (`sp.TAddress`, `sp.TNat`, ecc.)
-   Gestione esplicita degli opzionali (`sp.some`, `sp.none`,
    `open_some()`)

La filosofia progettuale rispecchiava fortemente Michelson.

------------------------------------------------------------------------

## 2.2 SmartPy Moderno (Architettura Basata su Moduli)

Caratteristiche moderne:

-   `@sp.module`
-   Storage definito tramite `self.data.field`
-   `@sp.entrypoint`
-   `assert` nativo di Python
-   Strutture di controllo native di Python
-   `sp.cast()` per l'enforcement dei tipi
-   Riduzione delle dichiarazioni esplicite di tipi Michelson

Il framework si è evoluto verso un design Python‑first.

------------------------------------------------------------------------

# 3. Principali Trasformazioni a Livello di Linguaggio

## 3.1 Cambiamento di Paradigma nella Definizione dello Storage

Legacy:

    self.init(admin = admin, balance = sp.mutez(0))

Moderno:

    self.data.admin = admin
    self.data.balance = sp.mutez(0)

La documentazione afferma:

> "Lo storage è rappresentato da self.data nel contratto."

------------------------------------------------------------------------

## 3.2 Semplificazione del Flusso di Controllo

Legacy:

    sp.if condition:
        ...

Moderno:

    if condition:
        ...

------------------------------------------------------------------------

## 3.3 Evoluzione del Modello di Tipizzazione

Legacy:

-   Uso esplicito di `sp.TNat`, `sp.TAddress`
-   Ampio utilizzo di tipi opzionali

Moderno:

-   `sp.cast()` per la validazione dei tipi
-   Riduzione della dipendenza da opzionali

------------------------------------------------------------------------

## 3.4 Modernizzazione della Dichiarazione degli Entrypoint

Legacy:

    @sp.entry_point

Moderno:

    @sp.entrypoint

------------------------------------------------------------------------

# 4. Sintesi Comparativa

  | Dimensione            | SmartPy Legacy         | SmartPy Moderno
  | - | - | - |
  | Tipizzazione          | Ricalco di Michelson   | Integrata con Python
  | Flusso di controllo   | DSL specifica          | Python nativo
  | Storage               | `self.init()`          | `self.data`
  | Gestione opzionali    | Esplicita              | Ridotta
  | Modularità            | Limitata               | Forte sistema a moduli

------------------------------------------------------------------------

# 5. Conclusione

L'evoluzione di SmartPy rappresenta un passaggio da un'astrazione
Michelson fortemente basata su DSL a un framework modulare nativo
Python.

Questa trasformazione influisce su:

-   Ergonomia per gli sviluppatori
-   Manutenibilità dei contratti
-   Chiarezza semantica
-   Modularità e componibilità

I contratti analizzati fungono da esempi illustrativi di questa più
ampia transizione architetturale.

------------------------------------------------------------------------

# Riferimenti

1.  SmartPy Documentation -- Introduction\
    https://smartpy.io/docs/

2.  SmartPy Documentation -- Contracts and Storage\
    https://smartpy.io/docs/manual/syntax/contracts

3.  SmartPy Documentation -- Modules\
    https://smartpy.io/docs/manual/syntax/modules

4.  SmartPy Documentation -- Types\
    https://smartpy.io/docs/manual/syntax/types
