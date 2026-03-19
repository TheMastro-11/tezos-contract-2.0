import json
from pathlib import Path

import streamlit as st
from pytezos import pytezos

from contractUtils import (
    compileContract,
    origination,
    contractInfoResult,
    entrypointAnalyse,
    entrypointCall,
    callInfoResult,
    runScenario,
    getCompiledRoot
)
from folderScan import folderScan, contractSuites, scenarioScan
from csvUtils import csvReader, csvWriter
from jsonUtils import getAddress, addressUpdate, jsonWriter, jsonReader
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


def get_trace_root() -> Path:
    candidates = [
        TOOLCHAIN_ROOT / "rosetta_traces",
        TOOLCHAIN_ROOT / "execution_traces",
        Path("rosetta_traces"),
        Path("execution_traces")
    ]

    for candidate in candidates:
        if candidate.exists() and candidate.is_dir():
            return candidate.resolve()

    return candidates[0]


def get_rosetta_scenarios_root() -> Path:
    return get_contracts_root() / "Rosetta"


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


def _resolve_compiled_artifact_dir(entry: Path) -> Path | None:
    direct_contract = entry / "step_001_cont_0_contract.tz"
    direct_storage = entry / "step_001_cont_0_storage.tz"
    if direct_contract.exists() and direct_storage.exists():
        return entry

    matches = sorted(
        path.parent
        for path in entry.rglob("step_001_cont_0_contract.tz")
        if path.parent.joinpath("step_001_cont_0_storage.tz").exists()
    )
    return matches[0] if matches else None


def get_compiled_contracts() -> dict[str, dict]:
    compiled_root = getCompiledRoot()
    compiled_contracts = {}

    if not compiled_root.exists():
        return compiled_contracts

    for entry in sorted(compiled_root.iterdir()):
        if not entry.is_dir():
            continue

        artifact_dir = _resolve_compiled_artifact_dir(entry)
        if artifact_dir is None:
            continue

        contract_path = artifact_dir / "step_001_cont_0_contract.tz"
        storage_path = artifact_dir / "step_001_cont_0_storage.tz"
        metadata_path = entry / "metadata.json"

        metadata = {}
        if metadata_path.exists():
            try:
                metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
            except Exception:
                metadata = {}

        display_name = metadata.get("contract_id") or metadata.get("contract_name") or entry.name
        compiled_contracts[display_name] = {
            "dir": artifact_dir,
            "contract_path": contract_path,
            "storage_path": storage_path,
            "metadata": metadata,
        }

    return compiled_contracts

def execution_setup_auto(contract: str, rows):
    if isinstance(rows, dict) and "trace_execution" in rows:
        return executionSetupJson(contractId=contract, traceData=rows)
    return executionSetupCsv(contractId=contract, rows=rows)


def compile_view(client):
    st.header("1. Compile SmartPy Contracts")
    contracts_root = get_contracts_root()
    suites = contractSuites(contracts_root)

    if not suites:
        st.warning("No contract families found in the contracts directory.")
        return

    selected_suite = st.selectbox(
        "Select a contract family:",
        options=suites,
        key="compile_suite_select"
    )

    contracts = folderScan(contracts_root, suite=selected_suite)

    if not contracts:
        st.warning(f"No contracts found in '{selected_suite}'.")
        return

    contract_to_compile = st.selectbox(
        "Select a contract to compile:",
        options=contracts,
        key="compile_select"
    )

    if st.button("🚀 Compile"):
        if contract_to_compile and client:
            folder, impl = parse_contract_id(contract_to_compile)
            contract_path = contracts_root / folder / f"{impl}.py"
            with st.spinner(f"Compiling {contract_path}..."):
                try:
                    compileContract(contractPath=str(contract_path))
                    st.success(f"Contract '{contract_to_compile}' compiled successfully!")
                    st.info(f"The Michelson files have been generated in `{getCompiledRoot()}`.")
                except Exception as e:
                    st.error("Error during compilation")
                    st.code(str(e))


def deploy_view(client):
    st.header("2. Deploy a Contract (Origination)")
    compiled_contracts = get_compiled_contracts()

    if not compiled_contracts:
        st.warning("No compiled contracts found in `toolchain/compiled`. Compile a contract before deploying.")
        return

    contract_to_deploy = st.selectbox(
        "Select a compiled contract to deploy:",
        options=list(compiled_contracts.keys()),
        key="deploy_select"
    )

    initial_balance = st.number_input("Initial balance (in tez):", min_value=0, value=1, step=1)

    if st.button("🌐 Deploy"):
        if contract_to_deploy and client:
            compiled_info = compiled_contracts[contract_to_deploy]
            michelson_path = compiled_info["contract_path"]
            storage_path = compiled_info["storage_path"]

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


def load_json_traces():
    return jsonReader(traceRoot=get_trace_root())


def render_trace_execution(trace_name, trace_data):
    with st.spinner(f"Executing trace '{trace_name}'..."):
        results = execution_setup_auto(contract=trace_name, rows=trace_data)
        for _, result in results.items():
            exportResult(result)
        return results


def trace_view():
    st.header("4. Execute Trace")
    trace_root = get_trace_root()
    st.info(f"Trace source folder: `{trace_root}`")

    execution_mode = st.radio(
        "Select the execution mode:",
        options=("Complete execution", "Single selection"),
        key="trace_execution_mode"
    )

    try:
        execution_traces = load_json_traces()
    except Exception as e:
        st.error(f"Error while loading traces: {e}")
        return

    if not execution_traces:
        st.warning("No execution traces found.")
        return

    trace_names = list(execution_traces.keys())

    if execution_mode == "Complete execution":
        st.write("The following traces will be executed together:")
        st.write(", ".join(trace_names))

        if st.button("▶️ Execute all traces"):
            try:
                all_results = {}
                for trace_name in trace_names:
                    st.write(f"--- Executing trace **{trace_name}** ---")
                    all_results[trace_name] = render_trace_execution(trace_name, execution_traces[trace_name])

                st.success("All traces have been executed and the results saved.")
                st.json(all_results)
            except Exception as e:
                st.error(f"Error during trace execution: {e}")
    else:
        selected_trace = st.selectbox(
            "Select a trace to execute:",
            options=trace_names,
            key="single_trace_select"
        )

        if st.button("▶️ Execute selected trace"):
            try:
                results = render_trace_execution(selected_trace, execution_traces[selected_trace])
                st.success(f"Trace '{selected_trace}' executed successfully.")
                st.json(results)
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
