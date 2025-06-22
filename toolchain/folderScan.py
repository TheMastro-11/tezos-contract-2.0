from pathlib import Path
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

    
def folderScan():
    contractsPath = Path("../contracts")


    completeList = [entry.name for entry in contractsPath.iterdir()]

    return completeList