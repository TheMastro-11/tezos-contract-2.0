from dataStructures import *
from pytezos import pytezos, PyTezosClient

class color:
   PURPLE = '\033[95m'
   CYAN = '\033[96m'
   DARKCYAN = '\033[36m'
   BLUE = '\033[94m'
   GREEN = '\033[92m'
   YELLOW = '\033[93m'
   RED = '\033[91m'
   BOLD = '\033[1m'
   UNDERLINE = '\033[4m'
   END = '\033[0m'

def print_contractsInfo(contractName):
    print(color.BOLD , color.GREEN , "CONTRACT INFO\n", color.END)
    print("Alias : ", contractName , "\nAddress :", contracts[contractName])
    entrypoints = pytezos.contract(contracts[contractName]).entrypoints
    del entrypoints["default"]
    lst = []
    print("EntryPoints:\n")
    for i in entrypoints:
        print(i, "\n")
        lst += i
    
    contractsEntrypoints[contractName] = lst
    
def print_walletInfo():
    print(color.BOLD , color.GREEN , "WALLET INFO\n", color.END)
    balance = int(PyTezosClient.account(pytezos)["balance"]) / MUTEZ
    print("Address : ", pytezos.key.public_key_hash(), "\nBalance : ", balance, " tez\n")