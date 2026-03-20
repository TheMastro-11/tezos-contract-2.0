# Integrated Report: Comparison Between SmartPy (Tezos) and Vyper (Ethereum)

## 1. General Framing

SmartPy and Vyper share a Python-inspired syntax, but they are languages designed for radically different runtimes: SmartPy compiles to Michelson and the Tezos execution model, while Vyper compiles to EVM bytecode for Ethereum. This difference is not only technical: it affects types, contract-to-contract calls, computational cost, security patterns, and even the proper way to design storage.

SmartPy presents itself as a complete solution for developing, testing, and deploying Tezos contracts, with integrated test scenarios, metadata support, and a well-developed FA2 library. Vyper, by contrast, explicitly pursues safety, simplicity, and auditability, removing several features considered opaque or risky and favoring a small, predictable language.

## 2. Design Goals

| Category | SmartPy | Vyper |
|---|---|---|
| Source language | Tezos-oriented DSL with Python-like syntax; compiles to Michelson | EVM language with Python-like syntax; compiles to EVM bytecode |
| Design principles | Productivity, modeling of Tezos contracts, integrated testing, libraries for token standards | Safety, simplicity, auditability, explicit semantics |
| Ecosystem | Web IDE, local CLI, test scenarios, explorer, FA2 library | Vyper compiler, ABI interfaces, modules, testing with Titanoboa/Brownie, integration with the EVM ecosystem |

SmartPy officially includes test scenarios, automatic compilation to Michelson, IPFS support, and a modular FA2 library with base classes, mixins, and transfer policies. Vyper instead documents testing with Titanoboa and Brownie and aims for reuse through modules and interfaces rather than inheritance.

## 3. Contract Structure and Syntax

### SmartPy

In the current syntax, SmartPy code is organized into modules; `.py` files contain a SmartPy module and can define `sp.Contract` classes, functions, and types. A typical contract is still a class inheriting from `sp.Contract`, with storage initialized in `__init__` and entrypoints annotated with `@sp.entrypoint`. In addition, SmartPy clearly distinguishes between contract code and Python test scenarios.

### Vyper

In Vyper, functions exist at module scope. Visibility is expressed through decorators such as `@external`, `@internal`, and `@deploy`; today only `__init__()` can be marked with `@deploy`. External functions are part of the contract interface and cannot be called directly from other external functions of the same contract without going through an interface.

### Comparative Summary

| Aspect | SmartPy | Vyper |
|---|---|---|
| Contract definition | `sp.Contract` class inside a SmartPy module/file | Contract/module with state and functions at module scope |
| Public functions | `@sp.entrypoint` | `@external` |
| Internal functions | SmartPy methods/helper functions | `@internal` |
| Constructor | `__init__()` | `@deploy def __init__()` |
| Modules / reuse | Import of SmartPy modules and SmartPy libraries | Module system with `import`, `initializes`, `uses`, `__interface__` |
| Inheritance | Present on the Python/SmartPy side (`sp.Contract`, classes, FA2 mixins) | Absent; Vyper favors composition through modules |

## 4. Storage, Types, and Data Semantics

SmartPy reflects native Tezos/Michelson types and constraints: `sp.nat`, `sp.int`, `sp.mutez`, `sp.ticket`, `sp.contract`, option, variant, map, set, list, and big-map-style structures. SmartPy supports type inference, but it remains strongly tied to the Michelson type system; a variable’s type does not change arbitrarily, and in case of ambiguity it can be made explicit with `sp.cast`. In addition, some “Python-like” structures have different semantics: for example, SmartPy lists use methods that differ from standard Python because they have a *linked-list* style structure.

Vyper instead reflects the ABI/EVM model: fixed-width signed and unsigned integers, `address`, `Bytes`, `String`, `HashMap`/mapping, struct, and `DynArray[T, N]` with a known maximum bound. Potentially lossy or semantically significant conversions require `convert()`. The official documentation also emphasizes that dynamic arrays and loops must remain bounded to keep gas costs predictable.

### Summary Table

| Aspect | SmartPy | Vyper |
|---|---|---|
| Typing | Strong, with inference and `sp.cast` where useful | Strong, explicit, with `convert()` for non-trivial conversions |
| Distinctive types | `sp.nat`, `sp.mutez`, `sp.ticket`, `sp.contract`, `variant` | `uintN`, `intN`, `address`, `Bytes`, `String`, `DynArray`, `HashMap` |
| Decimals | No equivalent native type; use of `mutez` or fixed-point libraries | `decimal` base-10 fixed-point, enabled explicitly |
| Overflow | Constrained by Michelson semantics and SmartPy constructs | Overflow/underflow checks always active |

## 5. Flow Control, Loops, Pattern Matching, Exceptions

SmartPy does not support `try/except`, does not support `elif`, and does not allow `break` in loops. Pattern matching through `match` is valid only for `option` and `variant`, not for integers or strings. This confirms that SmartPy is not real Python, but a DSL with deliberate limitations required for compilation to Michelson.

Vyper does not support recursion and requires loops to have an upper bound known at compile time. This choice exists to make gas consumption statically analyzable. Vyper also avoids complex exception handling: error semantics revolve around `assert` and revert.

| Aspect | SmartPy | Vyper |
|---|---|---|
| `try/except` | Not supported | Not supported |
| `break` | Not supported | Loops are bounded, but there is no full Python model |
| Recursion | Possible only within Michelson model limits, but unnatural and discouraged in practice | Forbidden |
| Pattern matching | Only on `option` and `variant` | Not present as an equivalent native feature |

## 6. Contract Calls and Execution

In SmartPy, when an entrypoint creates an operation — for example `sp.transfer`, `sp.send`, `sp.emit`, `sp.create_contract` — the operation is not executed immediately: it is added to the operations list and only starts at the end of the entrypoint. The order is FIFO with a practical depth-first execution tree effect; if an error occurs, the operations are canceled and rolled back. This radically changes the way one reasons about “external calls.”

In Vyper, by contrast, external interactions occur through ABI interfaces and explicit `extcall` or `staticcall`, which must match the mutability of the called function. The documentation insists on making the nature of the call explicit so that state-changing calls are clearly distinguished from read-only ones.

This difference also has direct security consequences: Ethereum/Vyper is heavily shaped by the classic reentrancy problem during external calls; Tezos/SmartPy, while not magically removing all composition risks, has a different operational model that reduces direct analogy with the classic EVM pattern.

## 7. Safety and Error Control

Vyper makes safety an explicit design goal: no inline assembly, no overloading, no inheritance, no recursion, limited loops, explicit conversions, and `@nonreentrant` as a global lock on protected functions. From version 0.4.0 onward, the documentation clarifies that non-reentrancy is global and no longer per-key as in older versions.

SmartPy aims more at safety through adherence to the Tezos model. Errors are handled with `assert`, `sp.failwith`, and explicit checks; in addition, compilation and integrated testing help validate complex scenarios. On the token side, the FA2 library also provides transfer policies and standardized components.

| Aspect | SmartPy | Vyper |
|---|---|---|
| Safety philosophy | Adherence to the Tezos model + integrated testing + standard libraries | Safety by removing features + explicit semantics |
| Error handling | `assert`, `sp.failwith`, explicit checks | `assert`, revert, explicit conversions |
| Reentrancy | There is no direct equivalent to `@nonreentrant`; the Tezos operating model is different | `@nonreentrant` with global lock |
| Auditability | Good, but inside a richer toolchain | Extremely central to the language design |

## 8. Integrated Summary Comparison by Category

The following comparison highlights the main differences between SmartPy and Vyper, organized by category. Keep in mind that the two languages operate on different blockchains, so some characteristics derive directly from the network architecture itself.

### Design Goals

| Category | SmartPy | Vyper |
|---|---|---|
| **Source language** | Tezos-specific language based on Python syntax; compiles to Michelson. | EVM language with Python-like syntax; compiles to EVM bytecode. |
| **Design principles** | Ease of use and smart contract modeling with familiar syntax; testing tools and token-standard libraries. | Safety, simplicity, and auditability; removal of dangerous features and predictable code. |
| **Ecosystem** | Focused on Tezos; includes online IDE, FA2 libraries, and test scenarios. | Integrated with Ethereum tools such as Remix, Titanoboa, Brownie, Moccasin, and other EVM tools. |

### Contract Structure and Syntax

| Aspect | SmartPy | Vyper |
|---|---|---|
| **Contract definition** | Python class inheriting from `sp.Contract`, normally defined in a SmartPy module. Entrypoints are functions with the `@sp.entrypoint` decorator. | Contract defined as a module with global variables and functions annotated with `@external`, `@internal`, `@deploy`, etc. |
| **Variables and storage** | Storage accessible through `self.data`; types derived from Michelson (`nat`, `int`, `string`, `bytes`, `mutez`, `list`, `set`, `map`, `variant`). Storage variables are initialized in `__init__()`. | State variables declared globally and explicitly typed; dynamic arrays require a maximum bound (`DynArray[T, N]`). |
| **Entry points / public functions** | Functions with `@sp.entrypoint`; `self` provides storage access and `sp` provides Tezos primitives. | Functions annotated with `@external` (public) or `@internal` (internal). The `@payable` decorator allows sending ether. |
| **Constructor** | `__init__` method inside the class; executed at deployment. | Function annotated with `@deploy` (typically `__init__`). |
| **Inheritance/module systems** | Uses Python inheritance to derive from `sp.Contract`; does not allow arbitrary Python imports inside contracts, but supports SmartPy modules. | Does not support inheritance; uses a module system introduced in recent versions, with composition and explicit initialization. |
| **Exception handling** | No `try/except`; errors use `sp.failwith` or `assert`. | No complex exception handling; errors occur through `assert` and revert. |

### Typing and Semantics

| Aspect | SmartPy | Vyper |
|---|---|---|
| **Typing** | Strong; type inference is available, with explicit typing possible through `sp.cast`. The type does not change after declaration. | Strong; all parameters and variables have declared types. Potentially lossy conversions require `convert()`. |
| **Decimal numbers** | No equivalent native decimal type; use of `sp.mutez` or fixed-point libraries. | Supports `decimal`, a base-10 fixed-point type, enabled in recent versions. |
| **Overflow and checks** | Numeric safety depends on Michelson and SmartPy constructs, with explicit checks where needed. | Overflow and underflow are always checked by the compiler/runtime semantics. |
| **Loops and recursion** | Supports loops with limitations; no `break`; recursion is unnatural and discouraged. | Loops must have a known maximum bound; recursion is forbidden. |
| **Pattern matching** | Supported only for `variant` and `option`. | Not present as a native feature. |

### Libraries and Ecosystem

| Aspect | SmartPy | Vyper |
|---|---|---|
| **Token standards** | **FA2** library for fungible, non-fungible, and multi-asset tokens compliant with Tezos standards. | No equivalent built-in standard library; for ERC-20/721/1155, external libraries or examples are used. |
| **IDE and tools** | Web IDE (smartpy.io), offline editor, and CLI. | Support in EVM tools such as Remix, Titanoboa, Brownie, Moccasin, and various plugins. |
| **Testing** | Integrated `sp.test_scenario`, blockchain simulation, state checks, and Michelson generation. | Testing with Titanoboa, Brownie, and other frameworks; attention to gas and bounded loops. |

### Safety and Error Control

| Aspect | SmartPy | Vyper |
|---|---|---|
| **Re-entrancy** | Must be handled through safe Tezos patterns and storage design; the operating model differs from the EVM. | `@nonreentrant` automatically prevents reentrancy inside the contract. |
| **Parameter validation** | `assert` and explicit checks on inputs and state. | `assert`, explicit conversions, deterministic ABI, and strict compiler checks. |

## 9. Final Conclusion

SmartPy and Vyper share the choice of a Python-inspired syntax, but they have different goals, strongly shaped by their respective blockchains.

SmartPy emphasizes ease of development and provides a complete environment for Tezos, with token libraries and integrated testing. However, the constraints imposed by compilation to Michelson limit the typical freedom of Python and prevent contracts from being treated like normal Python programs.

Vyper instead aims to maximize safety by sacrificing flexibility. Severe restrictions — no inheritance, limited loops, no assembly, no overloading, recursion forbidden — reduce the attack surface but can make implementation more verbose.
