### **Technical Report: A Toolchain for Tezos Smart Contract Management**

#### **1. Introduction**

This report describes a toolchain developed in Python to automate and streamline the lifecycle of smart contracts on the Tezos blockchain. The primary goal of this tool is to optimize the processes of compiling, deploying, and interacting with contracts, while also providing features to monitor transaction costs.

The toolchain is built using the `PyTezos` library for communication with the Tezos network (specifically, the "ghostnet") and is designed to manage a variety of smart contracts written in `SmartPy`. The system is intended to be interactive, guiding the user through the various available operations, from managing a single contract to executing tests based on predefined traces.

**Key Technologies and Components:**

  * **Language:** Python 3
  * **Blockchain Library:** PyTezos
  * **Smart Contract Framework:** SmartPy
  * **Supported Operations:** Compilation, Deployment, Interaction, Trace Execution
  * **Output:** Transaction cost reports in CSV and JSON formats

-----

#### **2. Toolchain Architecture**

The toolchain consists of a main module that orchestrates several specialized utilities, each responsible for a specific phase of the workflow.

  * **Core Components:**

      * `main.py`: This is the heart of the toolchain. It manages the interactive menu, collects user input, and invokes the appropriate functions to perform the requested operation (e.g., compile, deploy).
      * `contractUtils.py`: This module provides the logical functions for interacting with the blockchain. It contains the logic to compile `SmartPy` files, originate (deploy) new contracts on the network, and call their entrypoints. It is also responsible for analyzing the results of operations to extract detailed cost information (gas, storage fees).
      * `folderScan.py`: A simple utility that scans the `../contracts/` directory to identify all available smart contract projects that the toolchain can interact with.
      * `csvUtils.py` & `jsonUtils.py`: These modules handle data persistence. `csvUtils` is used to read execution traces (CSV files defining a sequence of contract calls) and to write transaction reports. `jsonUtils` is responsible for updating the list of deployed contract addresses and saving reports in JSON format.

  * **Directory Structure:**

      * `toolchain/`: Contains all Python scripts for the toolchain.
      * `toolchain/execution_traces/`: Stores the CSV files with execution traces for automated contract testing.
      * `contracts/`: Contains subfolders for each smart contract, with each folder holding its SmartPy source code (`.py`) and, in some cases, a descriptive `README.md` file.

-----

#### **3. Workflow**

The user starts the toolchain by running `python3 main.py` from the command line. From there, the operational flow is divided into four main scenarios:

1.  **Compilation:**

      * The user selects the "Compile" option.
      * A list of available contracts, obtained via `folderScan`, is presented.
      * After a selection is made, the toolchain invokes a process to run the chosen contract's SmartPy script, which compiles it into Michelson and generates the storage and code files ready for deployment.

2.  **Deployment (Origination):**

      * The user selects the "Deploy" option and chooses a previously compiled contract.
      * They provide an initial balance for the new contract.
      * The `origination` function in `contractUtils.py` reads the Michelson files, creates an origination operation, and injects it into the blockchain via `PyTezos`.
      * Once the operation is confirmed, the new contract's address is saved to the `addressList.json` file using `jsonUtils.addressUpdate` for future use.

3.  **Interaction:**

      * The user selects "Interact" and chooses a deployed contract.
      * The toolchain analyzes the contract's entrypoints and prompts the user for which one to call, what parameters to provide, and the amount of tez to send, if any.
      * `contractUtils.entrypointCall` builds and sends the transaction.
      * Upon completion, the user is asked if they want to export the operation's details and costs to CSV and JSON files.

4.  **Trace Execution (Automated Testing):**

      * This is the most advanced feature. The user selects "Use Execution Trace".
      * The `csvUtils.csvReader` module reads files from the `execution_traces/` directory. Each CSV file contains a series of steps, where each row specifies the `entrypoint`, `wallet`, `parameters`, and `tezAmount`.
      * The `executionSetup` function iterates through these rows, simulating a sequence of real transactions and recording the results for each step. This allows for testing complex scenarios and measuring their costs in a reproducible manner.

-----

#### **4. Configuration and Usage**

  * **Prerequisites:**

      * Python 3 installed.
      * Required Python libraries, primarily `pytezos` and its dependencies.
      * A `wallet.json` file in the `toolchain/` directory containing the private keys of the Tezos accounts to be used for operations.

  * **Execution:**
    To start the toolchain, the user must navigate to the `toolchain/` directory and run the command:

    ```bash
    python3 main.py
    ```

    The main menu will then be displayed, guiding the user through the subsequent choices.

