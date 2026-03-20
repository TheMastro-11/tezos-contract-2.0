# Report integrato: confronto tra SmartPy (Tezos) e Vyper (Ethereum)

## 1. Inquadramento generale

SmartPy e Vyper condividono una sintassi ispirata a Python, ma sono linguaggi pensati per runtime radicalmente diversi: SmartPy compila verso Michelson e il modello di esecuzione di Tezos, mentre Vyper compila in bytecode EVM per Ethereum. Questa differenza non è solo tecnica: condiziona tipi, chiamate tra contratti, costo computazionale, pattern di sicurezza e perfino il modo corretto di progettare lo storage.

SmartPy si presenta come una soluzione completa per sviluppare, testare e distribuire contratti Tezos, con scenari di test integrati, supporto a metadata e una libreria FA2 molto sviluppata. Vyper, invece, persegue in modo esplicito sicurezza, semplicità e auditabilità, eliminando varie feature considerate opache o rischiose e favorendo un linguaggio piccolo e prevedibile.

## 2. Obiettivi progettuali

| Categoria | SmartPy | Vyper |
|---|---|---|
| Linguaggio di origine | DSL Tezos con sintassi Python-like; compila in Michelson | Linguaggio EVM con sintassi Python-like; compila in bytecode EVM |
| Principi di design | Produttività, modellazione dei contratti Tezos, testing integrato, librerie per standard token | Sicurezza, semplicità, auditabilità, semantica esplicita |
| Ecosistema | Web IDE, CLI locale, scenari di test, explorer, FA2 lib | Compiler Vyper, interfacce ABI, moduli, testing con Titanoboa/Brownie, integrazione nell’ecosistema EVM |

SmartPy include ufficialmente test scenario, compilazione automatica a Michelson, supporto a IPFS e una libreria FA2 modulare con base classes, mixin e transfer policies. Vyper documenta invece testing con Titanoboa e Brownie e punta a riuso tramite moduli e interfacce, non tramite ereditarietà.

## 3. Struttura dei contratti e sintassi

### SmartPy

Nella sintassi attuale, il codice SmartPy è organizzato in moduli; i file `.py` contengono un modulo SmartPy e possono definire classi `sp.Contract`, funzioni e tipi. Un contratto tipico resta una classe che eredita da `sp.Contract`, con storage inizializzato in `__init__` e entrypoint annotati con `@sp.entrypoint`. Inoltre SmartPy distingue chiaramente tra codice contratto e test scenario Python.

### Vyper

In Vyper le funzioni esistono a module scope. La visibilità è espressa tramite decorator come `@external`, `@internal` e `@deploy`; oggi solo `__init__()` può essere marcata `@deploy`. Le funzioni esterne fanno parte dell’interfaccia del contratto e non possono essere richiamate direttamente da altre external dello stesso contratto senza passare da un’interfaccia.

### Sintesi comparativa

| Aspetto | SmartPy | Vyper |
|---|---|---|
| Definizione contratto | Classe `sp.Contract` dentro un modulo/file SmartPy | Contratto/modulo con stato e funzioni a module scope |
| Funzioni pubbliche | `@sp.entrypoint` | `@external` |
| Funzioni interne | Metodi/funzioni ausiliarie SmartPy | `@internal` |
| Constructor | `__init__()` | `@deploy def __init__()` |
| Moduli / riuso | Import di moduli SmartPy e librerie SmartPy | Sistema di moduli con `import`, `initializes`, `uses`, `__interface__` |
| Ereditarietà | Presente lato Python/SmartPy (`sp.Contract`, classi, mixin FA2) | Assente; Vyper favorisce composizione tramite moduli |

## 4. Storage, tipi e semantica dei dati

SmartPy riflette i tipi nativi e i vincoli di Tezos/Michelson: `sp.nat`, `sp.int`, `sp.mutez`, `sp.ticket`, `sp.contract`, option, variant, map, set, list e big-map–style structures. SmartPy supporta type inference, ma resta fortemente vincolato al type system Michelson; il tipo di una variabile non cambia arbitrariamente e in caso di ambiguità si può esplicitare con `sp.cast`. Inoltre alcune strutture “simili a Python” hanno semantica diversa: per esempio le liste SmartPy usano metodi diversi da Python standard, in quanto hanno una struttura *concatenata*.

Vyper riflette invece il modello ABI/EVM: interi signed e unsigned a larghezza definita, `address`, `Bytes`, `String`, `HashMap`/mapping, struct e `DynArray[T, N]` con limite massimo noto. Le conversioni potenzialmente lossy o semanticamente significative richiedono `convert()`. La documentazione ufficiale sottolinea anche che array dinamici e loop devono restare bounded per mantenere prevedibile il gas.

### Tabella sintetica

| Aspetto | SmartPy | Vyper |
|---|---|---|
| Tipizzazione | Forte, con inferenza e `sp.cast` dove utile | Forte, esplicita, con `convert()` per conversioni non banali |
| Tipi distintivi | `sp.nat`, `sp.mutez`, `sp.ticket`, `sp.contract`, `variant` | `uintN`, `intN`, `address`, `Bytes`, `String`, `DynArray`, `HashMap` |
| Decimali | Nessun tipo nativo equivalente; uso di `mutez` o fixed-point library | `decimal` fixed-point base 10, da abilitare esplicitamente |
| Overflow | Vincolato alle semantiche Michelson e ai costrutti SmartPy | Controlli di overflow/underflow sempre attivi |

## 5. Flow control, loop, pattern matching, eccezioni

SmartPy non supporta `try/except`, non supporta `elif` e non consente `break` nei loop. Il pattern matching tramite `match` è valido solo per `option` e `variant`, non per interi o stringhe. Questo conferma che SmartPy non è Python vero, ma una DSL con limiti voluti per poter compilare in Michelson.

Vyper non supporta ricorsione e richiede che i loop abbiano un upper bound noto a compile time. Questa scelta esiste per rendere il consumo di gas staticamente analizzabile. Anche Vyper evita una gestione eccezioni complessa: la semantica degli errori ruota attorno ad `assert` e al revert.

| Aspetto | SmartPy | Vyper |
|---|---|---|
| `try/except` | Non supportato | Non supportato |
| `break` | Non supportato | I loop sono bounded, ma non c’è il modello Python pieno |
| Ricorsione | Possibile solo entro i limiti del modello Michelson, ma poco naturale e sconsigliata in pratica | Vietata |
| Pattern matching | Solo su `option` e `variant` | Non presente come feature nativa equivalente |

## 6. Chiamate tra contratti ed esecuzione

In SmartPy, quando un entrypoint crea un’operazione — ad esempio `sp.transfer`, `sp.send`, `sp.emit`, `sp.create_contract` — l’operazione non viene eseguita subito: viene aggiunta alla lista delle operazioni e parte solo al termine dell’entrypoint. L’ordine è FIFO con effetto pratico di execution tree depth-first; se avviene un errore, le operazioni vengono annullate e rollbackate. Questo cambia radicalmente il modo di ragionare sulle “chiamate esterne”.

In Vyper, invece, le interazioni esterne avvengono tramite interfacce ABI e chiamate esplicite `extcall` o `staticcall`, che devono combaciare con la mutabilità della funzione chiamata. La documentazione insiste proprio sull’esplicitazione della natura della call, per distinguere meglio i casi che possono modificare stato da quelli di sola lettura.

Questa differenza ha conseguenze dirette anche sulla sicurezza: Ethereum/Vyper è molto segnato dal problema classico della reentrancy durante external calls; Tezos/SmartPy, pur non “eliminando magicamente” tutti i rischi di composizione, ha un modello operativo diverso che riduce l’analogia diretta con il pattern EVM classico.

## 7. Sicurezza e controllo degli errori

Vyper rende la sicurezza un obiettivo di design esplicito: niente inline assembly, niente overloading, niente ereditarietà, niente ricorsione, loop limitati, conversioni esplicite, e `@nonreentrant` come lock globale sulle funzioni protette. Dalla 0.4.0 in poi, la documentazione chiarisce che la non-reentrancy è globale e non più per-key come nelle versioni vecchie.

SmartPy punta più a una sicurezza “per aderenza al modello Tezos”. Gli errori si gestiscono con `assert`, `sp.failwith` e verifiche esplicite; inoltre la compilazione e il testing integrato aiutano a validare scenari complessi. Sul lato token, la libreria FA2 fornisce anche politiche di trasferimento e componenti standardizzati.

| Aspetto | SmartPy | Vyper |
|---|---|---|
| Filosofia di sicurezza | Aderenza al modello Tezos + test integrati + librerie standard | Sicurezza per sottrazione di feature + semantica esplicita |
| Error handling | `assert`, `sp.failwith`, verifiche esplicite | `assert`, revert, conversioni esplicite |
| Reentrancy | Non c’è un equivalente diretto a `@nonreentrant`; il modello operativo Tezos è diverso | `@nonreentrant` con lock globale |
| Auditabilità | Buona, ma dentro una toolchain più ricca | Estremamente centrale nel design del linguaggio |


## 8. Confronto sintetico integrato per categoria

Il seguente confronto mette in luce le principali differenze tra SmartPy e Vyper, organizzate per categoria. Si noti che i due linguaggi operano su blockchain diverse, quindi alcune caratteristiche derivano dall’architettura della rete stessa.

### Obiettivi progettuali

| Categoria | SmartPy | Vyper |
|---|---|---|
| **Linguaggio di origine** | Linguaggio specifico per Tezos basato su sintassi Python; compila in Michelson. | Linguaggio per EVM con sintassi simile a Python; compila in bytecode EVM. |
| **Principi di design** | Facilità d’uso e modellazione di smart contract con sintassi familiare; strumenti di testing e libreria per standard token. | Sicurezza, semplicità e auditabilità; eliminazione di funzionalità pericolose e codice prevedibile. |
| **Ecosistema** | Concentrato su Tezos; include IDE online, librerie FA2 e scenari di test. | Integrato con strumenti Ethereum come Remix, Titanoboa, Brownie, Moccasin e altri tool EVM. |

### Struttura dei contratti e sintassi

| Aspetto | SmartPy | Vyper |
|---|---|---|
| **Definizione di contratto** | Classe Python che eredita da `sp.Contract`, normalmente definita in un modulo SmartPy. Gli entrypoint sono funzioni con decoratore `@sp.entrypoint`. | Contratto definito come modulo con variabili globali e funzioni annotate con `@external`, `@internal`, `@deploy`, ecc. |
| **Tipo di variabili e storage** | Storage accessibile tramite `self.data`; tipi derivati da Michelson (`nat`, `int`, `string`, `bytes`, `mutez`, `list`, `set`, `map`, `variant`). Le variabili di storage sono inizializzate in `__init__()`. | Variabili di stato dichiarate globalmente e tipizzate esplicitamente; gli array dinamici richiedono un limite massimo (`DynArray[T, N]`). |
| **Entry point / funzioni pubbliche** | Funzioni con `@sp.entrypoint`; `self` permette accesso allo storage e `sp` fornisce le primitive Tezos. | Funzioni annotate con `@external` (pubbliche) o `@internal` (interne). Il decoratore `@payable` consente l’invio di ether. |
| **Constructor** | Metodo `__init__` all’interno della classe; eseguito al deploy. | Funzione annotata `@deploy` (tipicamente `__init__`). |
| **Sistemi di eredità/moduli** | Usa ereditarietà Python per derivare da `sp.Contract`; non consente import arbitrari di moduli Python nei contratti, ma supporta moduli SmartPy. | Non supporta ereditarietà; utilizza un sistema di moduli introdotto nelle versioni recenti, con composizione e inizializzazione esplicita. |
| **Handling delle eccezioni** | Niente `try/except`; per errori si usano `sp.failwith` o `assert`. | Niente gestione eccezioni complessa; gli errori avvengono tramite `assert` e revert. |

### Typing e semantica

| Aspetto | SmartPy | Vyper |
|---|---|---|
| **Tipizzazione** | Forte; inferenza di tipo disponibile, con possibilità di esplicitare usando `sp.cast`. Il tipo non cambia dopo la dichiarazione. | Forte; tutti i parametri e le variabili hanno tipo dichiarato. Le conversioni potenzialmente lossy richiedono `convert()`. |
| **Numeri decimali** | Nessun tipo decimale nativo equivalente; uso di `sp.mutez` o librerie fixed-point. | Supporta `decimal`, tipo a punto fisso base 10, da abilitare nelle versioni recenti. |
| **Overflow e controlli** | La sicurezza numerica dipende da Michelson e dai costrutti SmartPy, con verifiche esplicite dove necessario. | Overflow e underflow controllati sempre dal compilatore/runtime semantico del linguaggio. |
| **Loop e ricorsione** | Supporta loop con limitazioni; niente `break`; ricorsione poco naturale e sconsigliata. | I cicli devono avere un limite massimo noto; la ricorsione è vietata. |
| **Pattern matching** | Supportato solo per `variant` e `option`. | Non presente come feature nativa. |

### Librerie e ecosistema

| Aspetto | SmartPy | Vyper |
|---|---|---|
| **Token standard** | Libreria **FA2** per token fungibili, non fungibili e multi‑asset conformi agli standard Tezos. | Nessuna libreria standard integrata equivalente; per ERC‑20/721/1155 si usano librerie o esempi esterni. |
| **IDE e strumenti** | IDE web (smartpy.io), editor offline e CLI. | Supporto in tool EVM come Remix, Titanoboa, Brownie, Moccasin e plugin vari. |
| **Testing** | `sp.test_scenario` integrato, simulazione della blockchain, verifiche di stato e generazione di Michelson. | Testing con Titanoboa, Brownie e altri framework; attenzione a gas e bounded loops. |

### Sicurezza e controllo degli errori

| Aspetto | SmartPy | Vyper |
|---|---|---|
| **Re-entrancy** | Da gestire tramite pattern sicuri Tezos e progettazione dello storage; il modello operativo è diverso da EVM. | `@nonreentrant` impedisce automaticamente la re-entrancy all’interno del contratto. |
| **Controllo dei parametri** | `assert` e verifiche esplicite su input e stato. | `assert`, conversioni esplicite, ABI deterministico e controlli severi del compilatore. |

## 9. Conclusione finale

SmartPy e Vyper condividono la scelta di una sintassi ispirata a Python, ma hanno obiettivi differenti, fortemente condizionati dalle rispettive blockchain.

SmartPy privilegia la facilità di sviluppo e fornisce un ambiente completo per Tezos, con librerie token e test integrati. Le restrizioni imposte dalla compilazione verso Michelson limitano però la libertà tipica di Python e impediscono di trattare i contratti come normali programmi Python.

Vyper punta invece a massimizzare la sicurezza sacrificando la flessibilità. Le restrizioni severe — assenza di ereditarietà, loop limitati, niente assembly, niente overloading, ricorsione vietata — riducono la superficie d’attacco ma possono rendere l’implementazione più verbosa.
