import json
from folderScan import folderScan

def addressUpdate(contract, newAddress):
    addressList = "../contracts/addressList.json"
    with open(addressList, 'r', encoding='utf-8') as file:
        addressValid = json.load(file)

    addressValid[contract] = newAddress

    with open(addressList, 'w', encoding='utf-8') as file:
        json.dump(addressValid, file, indent=4)

    return addressValid

def getAddress():
    addressList = "../contracts/addressList.json"
    with open(addressList, 'r', encoding='utf-8') as file:
        addressValid = json.load(file)

    return addressValid

def resolveAddress(addressValid, contractId):
    if contractId in addressValid:
        return addressValid[contractId]

    if ':' in contractId:
        folder = contractId.split(':', 1)[0]
        if folder in addressValid:
            return addressValid[folder]
        legacy_folder = Path(folder).name
        if legacy_folder in addressValid:
            return addressValid[legacy_folder]

    raise KeyError(f"Address not found for '{contractId}'")

def jsonWriter(fileName, opReport):
    transactionsValid = {}

    try:
        with open(fileName, 'r', encoding='utf-8') as file:
            data = json.load(file)

        if isinstance(data, dict):
            transactionsValid = data
    except(FileNotFoundError, json.JSONDecodeError):
        pass

    item = {
        "Entrypoint" : opReport["entryPoint"],
        "TotalCost" : opReport["TotalCost"],
        "Weight" : opReport["Weight"],
        "Hash" : opReport["Hash"]
    }
    transactionsValid[opReport["contract"]] = item

    with open(fileName, 'w', encoding='utf-8') as file:
        json.dump(transactionsValid, file, indent=4)

def jsonReader():
    executionTraces = folderScan("execution_traces")
    executionTracesDict = {}

    try:
        for trace in executionTraces:
            fileName = "execution_traces/"+trace

            with open(fileName, 'r', encoding='utf-8') as file:
                executionTracesDict[trace.replace(".json","")] = json.load(file)

        return executionTracesDict

    except FileNotFoundError:
        print(f"Error: File '{fileName}' not found.")
    except Exception as e:
        print(f"Error: {e}")
