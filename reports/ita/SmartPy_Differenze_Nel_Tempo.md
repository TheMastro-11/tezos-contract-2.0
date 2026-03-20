# Differenze fondamentali adottate nel corso degli anni in SmartPy

## Introduzione

Nel corso degli anni SmartPy ha subito una trasformazione significativa. L'evoluzione non ha riguardato solo la sintassi, ma l'intera architettura del framework, passando da una DSL più vicina a Michelson a un approccio moderno, modulare e più integrato con la semantica di Python.

## Visione generale dell'evoluzione

La direzione del cambiamento può essere riassunta così:

- riduzione della verbosità;
- maggiore aderenza alla sintassi Python;
- migliore modularità;
- storage più chiaro;
- tipizzazione più ergonomica;
- minore dipendenza da costrutti DSL specifici.

## 1. Passaggio da DSL Michelson-like a design Python-first

### Prima

Le versioni legacy di SmartPy riflettevano in modo marcato la logica di Michelson. La scrittura dei contratti era più vicina a una DSL dedicata che a Python idiomatico.

Elementi tipici:

- `class Contract(sp.Contract)`
- `self.init(...)`
- `@sp.entry_point`
- `sp.verify(...)`
- `sp.if`, `sp.for`
- tipi espliciti come `sp.TNat`, `sp.TAddress`
- uso frequente di `sp.some`, `sp.none`, `open_some()`

### Oggi

Il framework moderno punta a un'esperienza più naturale per chi scrive Python:

- `@sp.module`
- `self.data.campo`
- `@sp.entrypoint`
- `assert`
- `if`, `for` nativi
- `sp.cast()` per chiarire i tipi

### Impatto

Questo cambiamento ha reso i contratti:

- più leggibili;
- meno verbosi;
- più facili da manutenere;
- più vicini al modello mentale degli sviluppatori Python.

## 2. Evoluzione della gestione dello storage

### Legacy

Lo storage veniva inizializzato con `self.init(...)`:

```python
self.init(admin = admin, balance = sp.mutez(0))
```

### Moderno

Lo storage è rappresentato direttamente tramite `self.data`:

```python
self.data.admin = admin
self.data.balance = sp.mutez(0)
```

### Differenza fondamentale

Il modello moderno è più esplicito, più lineare e semanticamente più vicino a un oggetto Python, pur rimanendo conforme alla logica di compilazione blockchain.

## 3. Evoluzione del flusso di controllo

### Legacy

Il controllo era espresso con costrutti DSL:

```python
sp.if condition:
    ...
```

### Moderno

Si usano strutture di controllo Python native:

```python
if condition:
    ...
```

### Differenza fondamentale

L'abbandono di costrutti DSL dedicati riduce l'attrito cognitivo e migliora la comprensione del codice.

## 4. Evoluzione della tipizzazione

### Legacy

Il vecchio modello richiedeva una dichiarazione molto esplicita dei tipi Michelson:

- `sp.TNat`
- `sp.TAddress`
- `sp.TMap`
- ecc.

Inoltre era frequente la gestione manuale di optional e costrutti affini.

### Moderno

Il sistema moderno riduce la dipendenza da quella verbosità e usa strumenti come `sp.cast()` per chiarire il tipo quando serve.

### Differenza fondamentale

La tipizzazione rimane rigorosa, ma diventa più ergonomica e meno invasiva nel codice.

## 5. Crescita della modularità

### Prima

L'organizzazione dei contratti era più limitata e meno strutturata.

### Oggi

Con `@sp.module`, SmartPy permette di raggruppare in modo più ordinato:

- contratti;
- tipi;
- componenti riusabili;
- logiche comuni.

### Differenza fondamentale

La modularità migliora:

- riuso del codice;
- scalabilità dei progetti;
- chiarezza architetturale;
- separazione delle responsabilità.


## Tabella comparativa sintetica

| Dimensione | SmartPy Legacy | SmartPy Moderno |
|---|---|---|
| Paradigma | DSL vicina a Michelson | Python-first |
| Storage | `self.init()` | `self.data` |
| Controllo | `sp.if`, `sp.for` | `if`, `for` |
| Tipizzazione | Esplicita, molto verbosa | Più ergonomica con `sp.cast()` |
| Modularità | Limitata | Forte sistema a moduli |
| Ergonomia | Più tecnica | Più leggibile e manutenibile |

## Conclusione

Le differenze fondamentali adottate nel tempo mostrano chiaramente che SmartPy si è evoluto da framework fortemente condizionato dalla struttura di Michelson a piattaforma più moderna, modulare e orientata all'esperienza dello sviluppatore. Il cambiamento più importante non è solo sintattico, ma concettuale: oggi SmartPy punta a modellare gli smart contract in modo più naturale, mantenendo però la disciplina richiesta dalla blockchain Tezos.
