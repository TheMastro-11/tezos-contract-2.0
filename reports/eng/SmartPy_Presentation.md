# SmartPy Presentation

## What SmartPy Is

SmartPy is a high-level language and framework for developing smart contracts on Tezos using a Python-inspired syntax. Its goal is to make contract writing more readable, testable, and safe, while avoiding the direct complexity of Michelson, the low-level language of the Tezos blockchain.

In practice, SmartPy allows you to:

- write smart contracts with a syntax that feels familiar to Python developers;
- automatically compile the code to Michelson;
- simulate and test contract behavior before deployment;
- organize contracts in a modular and more maintainable way.

## How It Works

The logical workflow for using SmartPy is the following:

1. write the contract in SmartPy;
2. define storage, entrypoints, any views, and helper functions;
3. build test scenarios in Python;
4. SmartPy compiles the contract to Michelson;
5. the contract can be deployed on Tezos.

This setup makes it possible to work at a more abstract level than Michelson while still remaining compatible with the blockchain execution model.

## Usage Logic

SmartPy follows a "Python-first" logic, but with constraints derived from compilation to Michelson. This means that the code looks like Python, but it does not fully match pure Python.

The central idea is to:

- use Python as the contract modeling language;
- keep typing and structure compatible with Michelson;
- promote testability and clarity;
- reduce the verbosity of the older DSL.

## Structure of a SmartPy Contract

A modern SmartPy contract is typically defined inside a module using `@sp.module`, and the contract class inherits from `sp.Contract`.

Main elements:

- **Module**: a logical container for contracts and types.
- **Contract class**: defines the contract behavior.
- **Storage**: represented through `self.data`.
- **Entrypoints**: externally callable functions, declared with `@sp.entrypoint`.
- **Views**: functions used to read state.
- **Helper functions**: support the internal logic.

## Simplified Example

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

This example shows the essential structure:

- storage initialization in `__init__`;
- use of `self.data` for persistent fields;
- entrypoints to modify the state.

## Main Peculiarities

### 1. Compilation to Michelson

SmartPy does not execute the contract directly like traditional Python: the code is translated into Michelson. This guarantees integration with Tezos, but it also imposes stricter rules than standard Python.

### 2. Testing and Simulation

One of SmartPy’s strengths is the ability to create tests in Python. Through `@sp.add_test()` and `sp.test_scenario`, it is possible to simulate:

- contract deployment;
- entrypoint calls;
- storage evolution;
- checks through assertions or scenario validations.

### 3. Typing and Casting

SmartPy uses Michelson-compatible types such as `nat`, `int`, `mutez`, `address`, `timestamp`, `map`, `set`, `list`, `record`, `variant`, and others. In many cases, the type can be made explicit with `sp.cast()`.

### 4. Modularity

The most important evolution of the framework is the transition to a module-based architecture. This improves:

- code organization;
- component reuse;
- readability;
- maintenance of complex contracts.

### 5. Built-in Libraries

SmartPy includes libraries designed for common Tezos use cases, such as FA2 for fungible and non-fungible tokens, with a modular and easily extensible approach.

## Differences Compared to Pure Python

Although SmartPy resembles Python, there are important limitations:

- you cannot freely import external Python modules inside SmartPy modules;
- some constructs such as `try/except` are not allowed;
- loop usage is more limited;
- using `break` as in Python is not allowed;
- pattern matching is limited to structures such as `variant` and `option`;
- the behavior of lists and sets does not always match Python’s.

These differences stem from the fact that SmartPy must comply with the rules of the blockchain model and Michelson compilation.

## Advantages

- familiar syntax for Python developers;
- greater readability than Michelson;
- strong support for testing;
- a good level of safety thanks to typing;
- growing modularity in modern versions;
- useful tools for tokens and Tezos use cases.

## Limitations

- it is not pure Python;
- some syntactic restrictions can feel inconvenient;
- the ecosystem is smaller than Solidity/Ethereum;
- the logic still has to adapt to blockchain constraints.

## Conclusion

SmartPy is a tool designed to make smart contract development on Tezos more accessible, readable, and testable. Its main value lies in the combination of Python-like syntax, compilation to Michelson, integrated testing, and a progressively modular architecture. It is especially suitable for those looking for a high-level approach without giving up the control required by the blockchain environment.
