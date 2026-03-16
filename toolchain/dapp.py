import streamlit as st
from pathlib import Path

from contractUtils import (
    compileContract,
    origination,
    contractInfoResult,
    entrypointAnalyse,
    entrypointCall,
    callInfoResult,
    runScenario
)
from folderScan import folderScan, scenarioScan
from csvUtils import csvReader, csvWriter
from jsonUtils import getAddress, addressUpdate, jsonWriter
from pytezos import pytezos
import json
from main import executionSetupCsv, executionSetupJson
st.set_page_config(
    page_title="Tezos Smart Contract Toolchain",
    layout="centered"
)

st.title("🏗️ Tezos Smart Contract Toolchain")
st.caption("An interface to compile, deploy, interact with, and test Tezos smart contracts.")

TOOLCHAIN_ROOT = Path(__file__).resolve().parent
PROJECT_ROOT = TOOLCHAIN_ROOT.parent

def get_contracts_root() -> Path:
    candidates = [
        PROJECT_ROOT / "contracts",
        TOOLCHAIN_ROOT / "contracts",
        (TOOLCHAIN_ROOT / "../contracts").resolve(),
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate.resolve()
    return candidates[0]

def get_rosetta_scenarios_root() -> Path:
    return get_contracts_root() / "Rosetta" / "scenarios"

def get_client(wallet_id):
    try:
        with open("wallet.json", 'r', encoding='utf-8') as f:
            wallets = json.load(f)
        key = wallets.get(str(wallet_id))
        if not key:
            st.error(f"Wallet with ID {wallet_id} not found in wallet.json.")
            return None
        return pytezos.using(shell="ghostnet", key=key)
    except FileNotFoundError:
        st.error("The wallet.json file was not found. Make sure it is in the correct directory.")
        return None
    except Exception as e:
        st.error(f"Error during client configuration: {e}")
        return None

def parse_contract_id(contract_id: str) -> tuple[str, str]:
    if ":" in contract_id:
        folder, impl = contract_id.split(":", 1)
        return folder, impl
    return contract_id, contract_id

def resolve_compiled_paths(folder: str, impl: str) -> tuple[Path, Path]:
    folder_name = Path(folder).name
    candidate_dirs = [
        Path(f"./{impl}"),
        Path(f"./{folder_name}"),
        Path(f"./{folder}"),
    ]
    for base_dir in candidate_dirs:
        c = base_dir / "step_001_cont_0_contract.tz"
        s = base_dir / "step_001_cont_0_storage.tz"
        if c.exists() and s.exists():
            return c, s
    return (
        candidate_dirs[0] / "step_001_cont_0_contract.tz",
        candidate_dirs[0] / "step_001_cont_0_storage.tz",
    )

def execution_setup_auto(contract: str, rows):
    if isinstance(rows, dict):
        return executionSetupCsv(contractId=contract, rows=rows)
    return executionSetupJson(contractId=contract, rows=rows)

def compile_view(client):
    st.header("1. Compile SmartPy Contracts")
    contracts = folderScan(get_contracts_root())
    contract_to_compile = st.selectbox("Select a contract to compile:", options=contracts, key="compile_select")

    if st.button("🚀 Compile"):
        if contract_to_compile and client:
            folder, impl = parse_contract_id(contract_to_compile)
            contract_path = get_contracts_root() / folder / f"{impl}.py"
            with st.spinner(f"Compiling {contract_path}..."):
                try:
                    compileContract(contractPath=str(contract_path))
                    st.success(f"Contract '{contract_to_compile}' compiled successfully!")
                    st.info("The Michelson files have been generated in the contract's directory.")
                except Exception as e:
                    st.error("Error during compilation")
                    st.code(str(e))

def deploy_view(client):
    st.header("2. Deploy a Contract (Origination)")
    contracts = folderScan(get_contracts_root())
    contract_to_deploy = st.selectbox("Select a contract to deploy:", options=contracts, key="deploy_select")

    initial_balance = st.number_input("Initial balance (in tez):", min_value=0, value=1, step=1)

    if st.button("🌐 Deploy"):
        if contract_to_deploy and client:
            folder, impl = parse_contract_id(contract_to_deploy)
            michelson_path, storage_path = resolve_compiled_paths(folder, impl)

            if not michelson_path.exists() or not storage_path.exists():
                st.error("Contract not compiled. Compile it before deploying.")
                return

            michelson_code = michelson_path.read_text()
            storage_code = storage_path.read_text()

            with st.spinner("Origination in progress... The operation may take a few minutes."):
                try:
                    op_result = origination(
                        client=client,
                        michelsonCode=michelson_code,
                        initialStorage=storage_code,
                        initialBalance=initial_balance
                    )
                    if op_result:
                        contract_info = contractInfoResult(op_result=op_result)
                        addressUpdate(contract=contract_to_deploy, newAddress=contract_info["address"])
                        st.success(f"Contract '{contract_to_deploy}' deployed successfully!")
                        st.write("New contract address:")
                        st.code(contract_info["address"], language="text")
                        st.write("Operation hash:")
                        st.code(contract_info["hash"], language="text")
                    else:
                        st.error("Origination failed. Check the console log for details.")
                except Exception as e:
                    st.error(f"Error during deployment: {e}")

def interact_view(client):
    st.header("3. Interact with a Contract")
    try:
        deployed_contracts = getAddress()
        if not deployed_contracts:
            st.warning("No deployed contracts found in `addressList.json`.")
            return
    except Exception:
        st.error("`addressList.json` not found or corrupted.")
        return

    contract_name = st.selectbox("Select a contract to interact with:", options=list(deployed_contracts.keys()))

    if contract_name and client:
        contract_address = deployed_contracts[contract_name]
        st.info(f"Contract address: `{contract_address}`")

        try:
            entrypoints_schema = entrypointAnalyse(client=client, contractAddress=contract_address)
            entrypoint_name = st.selectbox("Select an entrypoint:", options=list(entrypoints_schema.keys()))

            params_input = ""
            if entrypoints_schema.get(entrypoint_name) != "unit":
                params_input = st.text_input("Enter the parameters (comma-separated if multiple):", placeholder="value1,value2")

            tez_amount = st.number_input("Amount of Tez to send:", min_value=0.0, value=0.0, step=0.1, format="%.6f")

            if st.button("➡️ Execute Call"):
                parameters = params_input.split(',') if params_input else []
                with st.spinner(f"Calling entrypoint '{entrypoint_name}'..."):
                    try:
                        op_result = entrypointCall(
                            client=client,
                            contractAddress=contract_address,
                            entrypointName=entrypoint_name,
                            parameters=parameters,
                            tezAmount=tez_amount
                        )
                        info_result = callInfoResult(opResult=op_result)
                        info_result["contract"] = contract_name
                        info_result["entryPoint"] = entrypoint_name

                        st.success("Call executed successfully!")
                        st.json(info_result)

                        if st.checkbox("Save result to CSV/JSON"):
                            exportResult(info_result)
                            st.info("Results exported.")

                    except Exception as e:
                        st.error(f"Error during call: {e}")
        except Exception as e:
            st.error(f"Unable to analyze contract entrypoints: {e}")

def trace_view():
    st.header("4. Execute Trace from CSV File")
    st.info("This function executes a series of predefined transactions from the files in `execution_traces/`.")

    if st.button("▶️ Start Trace Execution"):
        try:
            execution_traces = csvReader()
            if not execution_traces:
                st.warning("No execution traces found.")
                return

            with st.spinner("Executing traces..."):
                all_results = {}
                for contract, rows in execution_traces.items():
                    st.write(f"--- Executing trace for **{contract}** ---")
                    results = execution_setup_auto(contract=contract, rows=rows)
                    all_results[contract] = results
                    for element, result in results.items():
                        st.write(f"Step `{element}` completed.")
                        exportResult(result)

            st.success("All traces have been executed and the results saved.")
            st.json(all_results)

        except Exception as e:
            st.error(f"Error during trace execution: {e}")

def scenario_view():
    st.header("5. Test Scenario")
    scenarios_root = get_rosetta_scenarios_root()

    if not scenarios_root.exists():
        st.error(f"Scenario folder not found: {scenarios_root}")
        return

    scenarios = scenarioScan(scenarios_root)
    if not scenarios:
        st.warning("No scenario files found in `contracts/Rosetta/scenarios`.")
        return

    selected_scenario = st.selectbox("Select a scenario to test:", options=scenarios, key="scenario_select")
    scenario_path = scenarios_root / f"{selected_scenario}.py"
    st.caption(f"Resolved path: {scenario_path}")

    if st.button("🧪 Run Scenario"):
        with st.spinner(f"Running {selected_scenario}..."):
            try:
                result = runScenario(str(scenario_path))
                st.success(f"Scenario '{selected_scenario}' executed successfully!")
                if result.stdout.strip():
                    st.code(result.stdout, language="text")
                else:
                    st.info("Scenario executed without console output.")
                if result.stderr.strip():
                    st.warning("Scenario stderr output")
                    st.code(result.stderr, language="text")
            except Exception as e:
                st.error("Error during scenario execution")
                st.code(str(e), language="text")

def exportResult(opResult):
    fileName = "transactionsOutput"
    csvWriter(fileName=fileName+".csv", op_result=opResult)
    jsonWriter(fileName=fileName+".json", opReport=opResult)
    st.success(f"Result of operation {opResult['entryPoint']} saved to file.")

st.sidebar.header("🔧 Configuration")
wallet_selection = st.sidebar.selectbox("Select an Account (from wallet.json):", options=["1", "2", "3"])

st.sidebar.header("Features")
operation = st.sidebar.radio(
    "Select an operation:",
    ("Compile", "Deploy", "Interact", "Execute Trace", "Test Scenario")
)

client = get_client(wallet_selection)

if client or operation in {"Execute Trace", "Test Scenario"}:
    if operation == "Compile":
        compile_view(client)
    elif operation == "Deploy":
        deploy_view(client)
    elif operation == "Interact":
        interact_view(client)
    elif operation == "Execute Trace":
        trace_view()
    elif operation == "Test Scenario":
        scenario_view()
else:
    st.error("Cannot proceed without a valid Tezos client. Check the wallet selection and the `wallet.json` file.")
