# Fundamental Differences Adopted Over the Years in SmartPy

## Introduction

Over the years, SmartPy has undergone a significant transformation. The evolution did not concern syntax alone, but the entire framework architecture, moving from a Michelson-oriented DSL to a modern, modular approach that is more integrated with Python semantics.

## General View of the Evolution

The direction of change can be summarized as follows:

- reduced verbosity;
- greater adherence to Python syntax;
- better modularity;
- clearer storage handling;
- more ergonomic typing;
- less dependence on specific DSL constructs.

## 1. From a Michelson-like DSL to a Python-first Design

### Before

Legacy versions of SmartPy strongly reflected Michelson logic. Writing contracts was closer to a dedicated DSL than to idiomatic Python.

Typical elements:

- `class Contract(sp.Contract)`
- `self.init(...)`
- `@sp.entry_point`
- `sp.verify(...)`
- `sp.if`, `sp.for`
- explicit types such as `sp.TNat`, `sp.TAddress`
- frequent use of `sp.some`, `sp.none`, `open_some()`

### Today

The modern framework aims for a more natural experience for Python developers:

- `@sp.module`
- `self.data.field`
- `@sp.entrypoint`
- `assert`
- native `if`, `for`
- `sp.cast()` to clarify types

### Impact

This change has made contracts:

- more readable;
- less verbose;
- easier to maintain;
- closer to the mental model of Python developers.

## 2. Evolution of Storage Management

### Legacy

Storage was initialized with `self.init(...)`:

```python
self.init(admin = admin, balance = sp.mutez(0))
```

### Modern

Storage is represented directly through `self.data`:

```python
self.data.admin = admin
self.data.balance = sp.mutez(0)
```

### Fundamental Difference

The modern model is more explicit, more linear, and semantically closer to a Python object, while still remaining compliant with blockchain compilation logic.

## 3. Evolution of Control Flow

### Legacy

Control flow was expressed with DSL constructs:

```python
sp.if condition:
    ...
```

### Modern

Native Python control structures are used:

```python
if condition:
    ...
```

### Fundamental Difference

Abandoning dedicated DSL constructs reduces cognitive friction and improves code comprehension.

## 4. Modernization of Entrypoints

### Legacy

```python
@sp.entry_point
```

### Modern

```python
@sp.entrypoint
```

### Fundamental Difference

The change looks small, but it reflects a broader syntax standardization and a simplification of the framework API.

## 5. Evolution of Typing

### Legacy

The older model required very explicit declaration of Michelson types:

- `sp.TNat`
- `sp.TAddress`
- `sp.TMap`
- etc.

In addition, optional values and similar constructs were often managed manually.

### Modern

The modern system reduces dependence on that verbosity and uses tools such as `sp.cast()` to clarify type when needed.

### Fundamental Difference

Typing remains rigorous, but it becomes more ergonomic and less invasive in the code.

## 6. Growth of Modularity

### Before

Contract organization was more limited and less structured.

### Today

With `@sp.module`, SmartPy makes it possible to group in a more orderly way:

- contracts;
- types;
- reusable components;
- common logic.

### Fundamental Difference

Modularity improves:

- code reuse;
- project scalability;
- architectural clarity;
- separation of concerns.

## 7. Reduced Explicit Handling of Optional Values

### Legacy

It was common to use:

- `sp.some(...)`
- `sp.none`
- `open_some()`

### Modern

The modern approach tends to reduce the centrality of these patterns, favoring a cleaner and more linear style of writing.

### Fundamental Difference

The contract semantics become less weighed down by low-level details.

## 8. Improvement of Overall Ergonomics

Overall, the evolution of SmartPy has produced:

- better code readability;
- less distance between intent and implementation;
- easier onboarding;
- simpler maintenance;
- more expressive contracts.

## Summary Comparison Table

| Dimension | SmartPy Legacy | SmartPy Modern |
|---|---|---|
| Paradigm | Michelson-like DSL | Python-first |
| Storage | `self.init()` | `self.data` |
| Control flow | `sp.if`, `sp.for` | `if`, `for` |
| Entrypoint | `@sp.entry_point` | `@sp.entrypoint` |
| Typing | Explicit, very verbose | More ergonomic with `sp.cast()` |
| Optionals | Very explicit handling | Less central |
| Modularity | Limited | Strong module system |
| Ergonomics | More technical | More readable and maintainable |

## Conclusion

The fundamental differences adopted over time clearly show that SmartPy has evolved from a framework heavily conditioned by Michelson structure into a more modern, modular, and developer-oriented platform. The most important change is not only syntactic, but conceptual: today SmartPy aims to model smart contracts in a more natural way while still preserving the discipline required by the Tezos blockchain.
