import json


def addressUpdate(contract,newAddress):
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


def jsonWriter(fileName, opReport):
    transactionsValid = {}
    
    try:
        with open(fileName, 'r', encoding='utf-8') as file:
            data = json.load(file)
            
        if isinstance(data, dict):
            transactionsValid = data
    except(FileNotFoundError, json.JSONDecodeError):
        pass
        
        
    nextItemIndex = len(transactionsValid) +1
    item = {
        "TotalCost" : opReport["TotalCost"],
        "Hash" : opReport["Hash"]
    }
    transactionsValid[nextItemIndex] = item
    
    with open(fileName, 'w', encoding='utf-8') as file:
        json.dump(transactionsValid, file, indent=4)
