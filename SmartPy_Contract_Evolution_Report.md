# The Evolution of SmartPy:

## Language-Level Architectural Transformation and Its Impact on Tezos Smart Contract Design

------------------------------------------------------------------------

## Abstract

This report analyzes the evolution of the SmartPy language
and framework over recent years, focusing on the architectural
transition from the legacy DSL-oriented model to the modern module-based
design. Rather than centering exclusively on individual contract
refactorings, this work investigates how systemic changes in SmartPy
influenced smart contract structure, typing models, storage management,
control flow, and governance patterns.

------------------------------------------------------------------------

# 1. Introduction

SmartPy is a high-level language and framework for writing Tezos smart
contracts in Python. Over time, SmartPy has undergone significant
structural changes aimed at:

-   Reducing DSL verbosity
-   Aligning more closely with Python semantics
-   Improving modularity
-   Simplifying compilation to Michelson
-   Enhancing readability and developer ergonomics

According to the official SmartPy documentation:

> "SmartPy is a Python library for writing smart contracts on Tezos."\
> --- SmartPy Documentation, Introduction Section\
> https://smartpy.io/docs/

More recent documentation introduces modular architecture:

> "Modules allow grouping contracts and types in a structured way."\
> --- SmartPy Modules Documentation\
> https://smartpy.io/docs/manual/syntax/modules

The evolution reflects a shift from a Michelson-mirroring DSL toward a
Python-integrated contract modeling paradigm.

------------------------------------------------------------------------

# 2. Historical Overview of SmartPy Architecture

## 2.1 Legacy SmartPy (Pre-Module Era)

Key characteristics:

-   `class Contract(sp.Contract)`
-   Storage defined via `self.init(...)`
-   `@sp.entry_point`
-   `sp.verify(...)`
-   DSL-style control flow (`sp.if`, `sp.for`)
-   Explicit Michelson types (`sp.TAddress`, `sp.TNat`, etc.)
-   Explicit optional handling (`sp.some`, `sp.none`, `open_some()`)

### Architectural Model (Legacy)

``` mermaid
flowchart TD
    A[SmartPy DSL Layer] --> B[Typed Michelson-like Abstraction]
    B --> C[Michelson Compilation]
    C --> D[Tezos Blockchain]
```

The design philosophy strongly mirrored Michelson.

------------------------------------------------------------------------

## 2.2 Modern SmartPy (Module-Based Architecture)

Modern characteristics:

-   `@sp.module`
-   Storage defined via `self.data.field`
-   `@sp.entrypoint`
-   Native Python `assert`
-   Native Python control flow
-   `sp.cast()` for type enforcement
-   Reduced explicit Michelson-type declarations

### Architectural Model (Modern)

``` mermaid
flowchart TD
    A[Python Semantic Layer] --> B[SmartPy Module Abstraction]
    B --> C[Michelson Compiler Backend]
    C --> D[Tezos Blockchain]
```

The framework evolved toward a Python-first design.

------------------------------------------------------------------------

# 3. Major Language-Level Transformations

## 3.1 Storage Definition Paradigm Shift

Legacy:

``` python
self.init(admin = admin, balance = sp.mutez(0))
```

Modern:

``` python
self.data.admin = admin
self.data.balance = sp.mutez(0)
```

Documentation states:

> "The storage is represented by self.data in the contract."\
> --- SmartPy Documentation\
> https://smartpy.io/docs/manual/syntax/contracts

------------------------------------------------------------------------

## 3.2 Control Flow Simplification

Legacy:

``` python
sp.if condition:
    ...
```

Modern:

``` python
if condition:
    ...
```

Documentation:

> "SmartPy uses Python control structures."\
> --- SmartPy Documentation\
> https://smartpy.io/docs/

------------------------------------------------------------------------

## 3.3 Typing Model Evolution

Legacy:

-   Explicit `sp.TNat`, `sp.TAddress`
-   Extensive optional usage

Modern:

-   `sp.cast()` for type validation
-   Reduced optional reliance

Documentation:

> "SmartPy supports type casting and annotations through sp.cast."\
> --- SmartPy Type System Documentation\
> https://smartpy.io/docs/manual/syntax/types

------------------------------------------------------------------------

## 3.4 Entrypoint Declaration Modernization

Legacy:

``` python
@sp.entry_point
```

Modern:

``` python
@sp.entrypoint
```

Documentation:

> "Entrypoints are declared with @sp.entrypoint."\
> --- SmartPy Documentation\
> https://smartpy.io/docs/manual/syntax/contracts

------------------------------------------------------------------------

# 4. Comparative Summary

  | Dimension           | Legacy SmartPy        | Modern SmartPy
  | - | - | - |
  | Typing              | Michelson-mirroring   | Python-integrated
  | Control Flow        | DSL-specific          | Native Python
  | Storage             | `self.init()`         | `self.data`
  | Optional Handling   | Explicit              | Reduced
  | Modularity          | Limited               | Strong module system

------------------------------------------------------------------------

# 5. Conclusion

The SmartPy evolution represents a shift from DSL-heavy Michelson
abstraction to a Python-native modular framework.

This transformation affects:

-   Developer ergonomics
-   Contract maintainability
-   Semantic clarity
-   Modularity and composability
------------------------------------------------------------------------

# References

1.  SmartPy Documentation -- Introduction\
    https://smartpy.io/docs/

2.  SmartPy Documentation -- Contracts and Storage\
    https://smartpy.io/docs/manual/syntax/contracts

3.  SmartPy Documentation -- Modules\
    https://smartpy.io/docs/manual/syntax/modules

4.  SmartPy Documentation -- Types\
    https://smartpy.io/docs/manual/syntax/types