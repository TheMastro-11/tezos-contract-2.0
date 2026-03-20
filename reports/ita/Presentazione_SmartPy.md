# Presentazione SmartPy

## Cos'è SmartPy

SmartPy è un linguaggio e framework di alto livello per sviluppare smart contract su Tezos utilizzando una sintassi ispirata a Python. L'obiettivo è rendere la scrittura dei contratti più leggibile, testabile e sicura, evitando la complessità diretta di Michelson, il linguaggio di basso livello della blockchain Tezos.

In pratica, SmartPy permette di:

- scrivere smart contract con una sintassi familiare a chi conosce Python;
- compilare automaticamente il codice in Michelson;
- simulare e testare il comportamento dei contratti prima del deploy;
- organizzare i contratti in modo modulare e più manutenibile.

## Come funziona

Il flusso logico di utilizzo di SmartPy è questo:

1. si scrive il contratto in SmartPy;
2. si definiscono storage, entrypoint, eventuali views e funzioni ausiliarie;
3. si costruiscono scenari di test in Python;
4. SmartPy compila il contratto in Michelson;
5. il contratto può essere distribuito su Tezos.

Questa impostazione consente di lavorare a un livello più astratto rispetto a Michelson, mantenendo però compatibilità con il modello di esecuzione della blockchain.

## Logica di utilizzo

SmartPy segue una logica "Python-first", ma con vincoli derivati dalla compilazione verso Michelson. Questo significa che il codice somiglia a Python, ma non coincide completamente con Python puro.

L'idea centrale è:

- usare Python come linguaggio di modellazione del contratto;
- mantenere tipizzazione e struttura compatibili con Michelson;
- favorire testabilità e chiarezza;
- ridurre la verbosità della vecchia DSL.

## Struttura di un contratto SmartPy

Un contratto SmartPy moderno è tipicamente definito dentro un modulo tramite `@sp.module` e la classe del contratto eredita da `sp.Contract`.

Elementi principali:

- **Modulo**: contenitore logico per contratti e tipi.
- **Classe contratto**: definisce il comportamento del contratto.
- **Storage**: rappresentato tramite `self.data`.
- **Entrypoint**: funzioni richiamabili dall'esterno, dichiarate con `@sp.entrypoint`.
- **Views**: funzioni di lettura dello stato.
- **Funzioni ausiliarie**: supportano la logica interna del contratto.

## Esempio semplificato

```python
import smartpy as sp

@sp.module
def main():
    class Counter(sp.Contract):
        def __init__(self, initial_value: sp.int):
            self.data.value = initial_value

        @sp.entrypoint
        def add(self, delta: sp.int):
            self.data.value += delta

        @sp.entrypoint
        def sub(self, delta: sp.int):
            self.data.value -= delta
```

Questo esempio mostra la struttura essenziale:

- inizializzazione dello storage in `__init__`;
- uso di `self.data` per i campi persistenti;
- entrypoint per modificare lo stato.

## Peculiarità principali

### 1. Compilazione verso Michelson

SmartPy non esegue direttamente il contratto come Python tradizionale: il codice viene tradotto in Michelson. Questo garantisce integrazione con Tezos ma impone regole più rigide rispetto a Python standard.

### 2. Testing e simulazione

Uno dei punti di forza di SmartPy è la possibilità di creare test in Python. Attraverso `@sp.add_test()` e `sp.test_scenario`, è possibile simulare:

- deploy del contratto;
- chiamate agli entrypoint;
- evoluzione dello storage;
- verifiche tramite assert o controlli di scenario.

### 3. Tipizzazione e casting

SmartPy utilizza tipi compatibili con Michelson, come `nat`, `int`, `mutez`, `address`, `timestamp`, `map`, `set`, `list`, `record`, `variant` e altri. In molti casi il tipo può essere chiarito esplicitamente con `sp.cast()`.

### 4. Modularità

L'evoluzione più importante del framework è il passaggio a un'architettura basata su moduli. Questo migliora:

- organizzazione del codice;
- riuso dei componenti;
- leggibilità;
- manutenzione di contratti complessi.

### 5. Librerie integrate

SmartPy include librerie pensate per casi d'uso tipici su Tezos, come FA2 per token fungibili e non fungibili, con approccio modulare e facilmente estendibile.

## Differenze rispetto a Python puro

Anche se SmartPy ricorda Python, esistono limitazioni importanti:

- non si possono importare liberamente moduli Python esterni nei moduli SmartPy;
- non sono ammessi alcuni costrutti come `try/except`;
- l'uso dei loop è più limitato;
- non è consentito usare `break` come in Python;
- il pattern matching è limitato a strutture come `variant` e `option`;
- il comportamento di liste e set non coincide sempre con quello Python.

Queste differenze derivano dal fatto che SmartPy deve rispettare le regole del modello blockchain e della compilazione Michelson.

## Vantaggi

- sintassi familiare per sviluppatori Python;
- maggiore leggibilità rispetto a Michelson;
- forte supporto al testing;
- buon livello di sicurezza grazie alla tipizzazione;
- modularità crescente nelle versioni moderne;
- strumenti utili per token e casi d'uso Tezos.

## Limiti

- non è Python puro;
- alcune restrizioni sintattiche possono risultare scomode;
- l'ecosistema è più ristretto rispetto a Solidity/Ethereum;
- la logica deve comunque adattarsi ai vincoli della blockchain.

## Conclusione

SmartPy è uno strumento pensato per rendere lo sviluppo di smart contract su Tezos più accessibile, leggibile e testabile. Il suo valore principale sta nella combinazione tra sintassi simile a Python, compilazione verso Michelson, testing integrato e progressiva modularizzazione dell'architettura. È particolarmente adatto a chi cerca un approccio ad alto livello senza rinunciare al controllo richiesto dall'ambiente blockchain.
