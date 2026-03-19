import json
from decimal import Decimal, InvalidOperation
from pathlib import Path

from pytezos import pytezos

from contractUtils import (
    compileContract,
    origination,
    contractInfoResult,
    entrypointAnalyse,
    entrypointCall,
    callInfoResult,
    runScenario,
    getCompiledRoot,
    waitForBlockDelay
)
from folderScan import folderScan, contractSuites, scenarioScan
from csvUtils import csvReader, csvWriter
from jsonUtils import getAddress, addressUpdate, jsonWriter, jsonReader, resolveAddress, normalizeTraceTitle, extractContractIdFromTraceTitle, updateDeploymentLevel, getDeploymentLevel


def getToolchainRoot() -> Path:
    return Path(__file__).resolve().parent


def getContractsRoot() -> Path:
    candidates = [
        (getToolchainRoot() / "../contracts").resolve(),
        getToolchainRoot() / "contracts"
    ]

    for candidate in candidates:
        if candidate.exists():
            return candidate.resolve()

    return candidates[0]


def getScenariosRoot() -> Path:
    return getContractsRoot() / "Rosetta" / "scenarios"


def getTraceRoot() -> Path:
    toolchain_root = getToolchainRoot()
    candidates = [
        toolchain_root / "rosetta_traces",
        toolchain_root / "execution_traces"
    ]

    for candidate in candidates:
        if candidate.exists():
            return candidate.resolve()

    return candidates[0]


def parseContractId(contractId):
    if ":" in contractId:
        folder, fileBase = contractId.split(":", 1)
        return folder, fileBase
    return contractId, contractId

def findCompiledArtifactDir(compiledBaseDir):
    compiledBaseDir = Path(compiledBaseDir)
    directContract = compiledBaseDir / "step_001_cont_0_contract.tz"
    directStorage = compiledBaseDir / "step_001_cont_0_storage.tz"
    if directContract.exists() and directStorage.exists():
        return compiledBaseDir

    for contractPath in sorted(compiledBaseDir.rglob("step_001_cont_0_contract.tz")):
        candidateDir = contractPath.parent
        if (candidateDir / "step_001_cont_0_storage.tz").exists():
            return candidateDir

    return None


def compiledOutputDir(contractFolder, fileBase):
    normalized_name = fileBase.removesuffix("Rosetta")
    return str((getCompiledRoot() / normalized_name).resolve())


def selectContractSuite():
    contractsRoot = getContractsRoot()
    suites = contractSuites(contractsRoot)

    if not suites:
        raise FileNotFoundError("No contract suites found.")

    print("\nContract suites available:\n")
    for index, suite in enumerate(suites, start=1):
        print(index, " " + suite)

    suiteSel = int(input("Which contract suite do you want to use?\n"))
    return suites[suiteSel - 1]


def interactionSetup(client, contractId):
    addressValid = getAddress()
    contractAddress = resolveAddress(addressValid=addressValid, contractId=contractId)
    entrypoints = entrypointAnalyse(client=client, contractAddress=contractAddress)

    print("\nEntrypoints available:")
    entryList = list(entrypoints.keys())
    for index, entrypoint in enumerate(entryList, start=1):
        print(index, " " + entrypoint)

    entrypointSel = int(input("Which entrypoint do you want to use?\n"))
    entrypointName = entryList[entrypointSel - 1]

    parameters = []
    if entrypoints[entrypointName] != "unit":
        parameters = input("Insert parameters value: ")
        if "," in parameters:
            parameters = parameters.split(",")
        else:
            parameters = [parameters]

    tezAmount = parseAmountToTez(input("Insert tez amount: "))

    opResult = entrypointCall(
        client=client,
        contractAddress=contractAddress,
        entrypointName=entrypointName,
        parameters=parameters,
        tezAmount=tezAmount
    )
    infoResult = callInfoResult(opResult=opResult)
    infoResult["contract"] = contractId
    infoResult["entryPoint"] = entrypointName
    return infoResult


def executionSetupCsv(contractId, rows):
    infoResultDict = {}
    for element in rows:
        row = rows[element]
        entrypointSel = row[0]
        walletSel = row[1]
        tezAmount = parseAmountToTez(row[len(row)-1])
        parameters = row[2:len(row)-1] if row[2:len(row)-1] != [] else []

        addressValid = getAddress()
        contractAddress = resolveAddress(addressValid=addressValid, contractId=contractId)
        contractInterface = pytezos.contract(contractAddress)
        entrypoints = contractInterface.entrypoints
        if entrypointSel not in entrypoints:
            raise Exception("Entrypoint not found: " + entrypointSel)

        with open("wallet.json", 'r', encoding='utf-8') as file:
            wallet = json.load(file)
        key = wallet[walletSel]
        client = pytezos.using(shell="ghostnet", key=key)

        opResult = entrypointCall(
            client=client,
            contractAddress=contractAddress,
            entrypointName=entrypointSel,
            parameters=parameters,
            tezAmount=tezAmount
        )
        infoResult = callInfoResult(opResult=opResult)
        infoResult["contract"] = contractId
        infoResult["entryPoint"] = entrypointSel

        infoResultDict[element] = infoResult

    return infoResultDict


def normalizeWalletLabel(value):
    return str(value).strip().lower()


def readWallets():
    with open("wallet.json", 'r', encoding='utf-8') as file:
        return json.load(file)


def extractWalletLabels(traceData):
    labels = []
    seen = set()

    for actor in traceData.get("trace_actors", []):
        actor_label = normalizeWalletLabel(actor)
        if actor_label and actor_label not in seen:
            labels.append(actor_label)
            seen.add(actor_label)

    for step in traceData.get("trace_execution", []):
        for actor in step.get("actors", []):
            actor_label = normalizeWalletLabel(actor)
            if actor_label and actor_label not in seen:
                labels.append(actor_label)
                seen.add(actor_label)

        tezos_data = step.get("tezos", {})
        provider_wallet = tezos_data.get("provider_wallet")
        if provider_wallet:
            provider_label = normalizeWalletLabel(provider_wallet)
            if provider_label not in seen:
                labels.append(provider_label)
                seen.add(provider_label)

    return labels


def buildWalletMap(traceData, availableWallets):
    normalized_wallets = {
        normalizeWalletLabel(wallet_id): wallet_id
        for wallet_id in availableWallets.keys()
    }
    wallet_labels = extractWalletLabels(traceData)
    wallet_map = {}

    ordered_wallet_ids = list(availableWallets.keys())
    next_wallet_index = 0

    for label in wallet_labels:
        if label in normalized_wallets:
            wallet_map[label] = normalized_wallets[label]
            continue

        if next_wallet_index >= len(ordered_wallet_ids):
            raise ValueError("Not enough wallets configured in wallet.json for the execution trace.")

        wallet_map[label] = ordered_wallet_ids[next_wallet_index]
        next_wallet_index += 1

    return wallet_map


def parseAmountToTez(amountValue):
    if amountValue is None or amountValue == "":
        return Decimal("0")

    if isinstance(amountValue, Decimal):
        return amountValue

    if isinstance(amountValue, int):
        return Decimal(amountValue)

    if isinstance(amountValue, float):
        return Decimal(str(amountValue))

    text = str(amountValue).strip()

    try:
        if text.startswith("mutez(") and text.endswith(")"):
            mutez_value = Decimal(text[6:-1].strip())
            return mutez_value / Decimal("1000000")

        if text.startswith("tez(") and text.endswith(")"):
            return Decimal(text[4:-1].strip())

        return Decimal(text)
    except InvalidOperation as e:
        raise ValueError(f"Invalid tez amount: {amountValue}") from e


def getContractSourcePath(contractId):
    contractsRoot = getContractsRoot()
    normalizedName = contractId.removesuffix("Rosetta")
    matches = list((contractsRoot / "Rosetta").glob(f"**/{normalizedName}Rosetta.py"))
    if not matches:
        raise FileNotFoundError(f"Unable to resolve the source file for contract '{contractId}'.")
    return matches[0]


def getEntrypointParameterNames(contractId, entrypointName):
    import ast

    sourcePath = getContractSourcePath(contractId)
    module = ast.parse(sourcePath.read_text(encoding="utf-8"))

    for node in ast.walk(module):
        if isinstance(node, ast.FunctionDef) and node.name == entrypointName:
            decorators = []
            for decorator in node.decorator_list:
                if isinstance(decorator, ast.Attribute):
                    decorators.append(decorator.attr)
                elif isinstance(decorator, ast.Name):
                    decorators.append(decorator.id)

            if "entrypoint" in decorators:
                return [arg.arg for arg in node.args.args if arg.arg != "self"]

    raise ValueError(f"Unable to resolve entrypoint '{entrypointName}' in '{sourcePath}'.")


def buildStepParameters(contractId, entrypointName, stepArgs):
    filteredArgs = {
        key: value
        for key, value in stepArgs.items()
        if not key.startswith("_")
    }

    if not filteredArgs:
        return []

    parameterNames = getEntrypointParameterNames(contractId, entrypointName)

    if len(parameterNames) == 1:
        parameterName = parameterNames[0]
        if parameterName not in filteredArgs:
            raise KeyError(
                f"Parameter '{parameterName}' not found in trace args for '{contractId}.{entrypointName}'."
            )
        return filteredArgs[parameterName]

    return {
        parameterName: filteredArgs[parameterName]
        for parameterName in parameterNames
        if parameterName in filteredArgs
    }


def resolveStepWallet(step, walletMap):
    tezos_data = step.get("tezos", {})
    provider_wallet = tezos_data.get("provider_wallet")
    if provider_wallet:
        provider_label = normalizeWalletLabel(provider_wallet)
        if provider_label in walletMap:
            return walletMap[provider_label]

    for actor in step.get("actors", []):
        actor_label = normalizeWalletLabel(actor)
        if actor_label in walletMap:
            return walletMap[actor_label]

    trace_actors = walletMap.keys()
    for actor_label in trace_actors:
        return walletMap[actor_label]

    raise ValueError("No wallet could be resolved for the trace step.")


def normalizeJsonTrace(traceData):
    availableWallets = readWallets()
    walletMap = buildWalletMap(traceData, availableWallets)
    normalizedRows = {}
    traceContractId = extractContractIdFromTraceTitle(traceData.get("trace_title", ""))

    if not traceContractId:
        raise ValueError("Unable to resolve the contract name from 'trace_title'.")

    for step in traceData.get("trace_execution", []):
        args = step.get("args", {})
        tezos_data = step.get("tezos", {})

        normalizedRows[step["sequence_id"]] = {
            "entrypoint": step["function_name"],
            "wallet": resolveStepWallet(step, walletMap),
            "contractId": traceContractId,
            "parameters": buildStepParameters(traceContractId, step["function_name"], args),
            "tezAmount": parseAmountToTez(tezos_data.get("_amount", args.get("_amount"))),
            "waitingTime": int(step.get("waiting_time", 0) or 0)
        }

    return normalizedRows


def executionSetupJson(contractId, traceData):
    normalizedRows = normalizeJsonTrace(traceData)
    infoResultDict = {}
    lastConfirmedBlockLevel = getDeploymentLevel(contractId)

    for element, row in normalizedRows.items():
        currentContractId = row["contractId"]
        entrypointSel = row["entrypoint"]
        walletSel = row["wallet"]
        parameters = row["parameters"]
        tezAmount = row["tezAmount"]
        waitingTime = row["waitingTime"]

        addressValid = getAddress()
        contractAddress = resolveAddress(addressValid=addressValid, contractId=currentContractId)
        contractInterface = pytezos.contract(contractAddress)
        entrypoints = contractInterface.entrypoints
        if entrypointSel not in entrypoints:
            raise Exception("Entrypoint not found: " + entrypointSel)

        with open("wallet.json", 'r', encoding='utf-8') as file:
            wallet = json.load(file)
        key = wallet[walletSel]
        client = pytezos.using(shell="ghostnet", key=key)

        if waitingTime > 0 and lastConfirmedBlockLevel is not None:
            waitForBlockDelay(
                client=client,
                startBlockLevel=lastConfirmedBlockLevel,
                waitingTime=waitingTime
            )

        opResult = entrypointCall(
            client=client,
            contractAddress=contractAddress,
            entrypointName=entrypointSel,
            parameters=parameters,
            tezAmount=tezAmount
        )
        infoResult = callInfoResult(opResult=opResult)
        infoResult["contract"] = currentContractId
        infoResult["entryPoint"] = entrypointSel

        if "confirmed_level" in opResult:
            lastConfirmedBlockLevel = opResult["confirmed_level"]

        infoResultDict[element] = infoResult

    return infoResultDict


def scenarioSetup():
    scenariosRoot = getScenariosRoot()
    if not scenariosRoot.exists():
        raise FileNotFoundError(f"Scenario folder not found: {scenariosRoot}")

    scenarios = scenarioScan(scenariosRoot)
    if not scenarios:
        raise FileNotFoundError("No scenario files found.")

    print("\nScenarios available:\n")
    for index, scenario in enumerate(scenarios, start=1):
        print(index, " " + scenario)

    scenarioSel = int(input("Which scenario do you want to test?\n"))
    scenarioPath = scenariosRoot / f"{scenarios[scenarioSel-1]}.py"
    return runScenario(str(scenarioPath))


def exportResult(opResult):
    fileName = "transactionsOutput"
    csvWriter(fileName=fileName + ".csv", op_result=opResult)
    print("\nCSV Updated!\n\n")
    jsonWriter(fileName=fileName + ".json", opReport=opResult)
    print("\nJSON Updated!\n\n")


def main():
    print("Hi, welcome to the Tezos-Contract toolchain!\n")
    print("Here you can compile, deploy, interact with, or test any contract from the archive.\n")

    contractsRoot = getContractsRoot()
    operationSel = int(input(
        "Now, select an option: \n"
        "1 Compile\n"
        "2 Deploy\n"
        "3 Interact\n"
        "4 Use Execution Trace\n"
        "5 Test Scenario\n"
    ))

    if operationSel not in {4, 5}:
        walletSel = input("Which account do you want to use?\n")
        with open("wallet.json", 'r', encoding='utf-8') as file:
            wallet = json.load(file)

        key = wallet[walletSel]
        client = pytezos.using(shell="ghostnet", key=key)

        selectedSuite = None
        if operationSel == 1:
            selectedSuite = selectContractSuite()

        allContracts = folderScan(contractsRoot, suite=selectedSuite)
        print("\nContracts available (Folder:Implementation): \n")
        for index, contractId in enumerate(allContracts, start=1):
            print(index, " " + contractId)

        contractSel = int(input("Which contract do you want to use?\n"))
        contractId = allContracts[contractSel-1]
        contractFolder, fileBase = parseContractId(contractId)

    match operationSel:
        case 1:
            contractPath = contractsRoot / contractFolder / f"{fileBase}.py"
            try:
                compileContract(contractPath=str(contractPath))
            except Exception as e:
                print(f"\nERROR: {e}\n")
            main()

        case 2:
            out_dir = Path(compiledOutputDir(contractFolder=contractFolder, fileBase=fileBase))
            artifact_dir = findCompiledArtifactDir(out_dir) if out_dir.exists() else None
            if artifact_dir is not None:
                michelsonPath = (artifact_dir / "step_001_cont_0_contract.tz").read_text()
                storagePath = (artifact_dir / "step_001_cont_0_storage.tz").read_text()
                initialBalance = int(input("Insert an initial balance:"))
                op_result = origination(
                    client=client,
                    michelsonCode=michelsonPath,
                    initialStorage=storagePath,
                    initialBalance=initialBalance
                )
                contractInfo = contractInfoResult(op_result=op_result)
                addressUpdate(contract=contractId, newAddress=contractInfo["address"])
                if "ConfirmedLevel" in contractInfo:
                    updateDeploymentLevel(contract=contractId, confirmedLevel=contractInfo["ConfirmedLevel"])
            else:
                print("\n\033[1m Contract must be compiled before \033[0m\n\n")

            main()

        case 3:
            op_report = interactionSetup(client=client, contractId=contractId)
            sel = input("Do you want to export the result?(y/n):  ")
            if sel == "y":
                exportResult(opResult=op_report)
            main()

        case 4:
            formatSel = input("CSV(1) or JSON(2)?")
            if str(formatSel) == "1":
                contractExecutionTraces = csvReader()
                for contract in contractExecutionTraces:
                    results = executionSetupCsv(contractId=contract, rows=contractExecutionTraces[contract])
                    for result in results:
                        exportResult(results[result])
            else:
                traceExecutionTraces = jsonReader(traceRoot=getTraceRoot())
                for traceName, traceData in traceExecutionTraces.items():
                    results = executionSetupJson(contractId=traceName, traceData=traceData)
                    for result in results:
                        exportResult(results[result])

            main()

        case 5:
            try:
                result = scenarioSetup()
                if result.stdout:
                    print(result.stdout)
                if result.stderr:
                    print(result.stderr)
            except Exception as e:
                print(f"\nERROR: {e}\n")
            main()


if __name__ == "__main__":
    main()
