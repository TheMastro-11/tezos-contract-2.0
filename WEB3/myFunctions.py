from pytezos import pytezos, Key, PyTezosClient
import time
import sys
from prettyPrints import *
from dataStructures import *

KEY = Key.from_encoded_key("edskS7VWazgioXEcBLhZ48sXmcwNmQ9HCx4q3tWch4MHdYVC7H4qAKtMbNQCZBQbAAL5WaduKA2H4fg8B7f2anEqZhpdXwk1yK")

MUTEZ = 1000000

loginStatus = False #track the login status of user


def menu():
    # Welcome message
    print("Welcome to UnicaTezos!\n")
    
    # Function for menu selection
    print("What would you like to do?\n")
    print("1) Insert new contract\n2) Open memory\n\
    \n q to quit")
    
    # Check user input
    selection = input("...")
    if selection == "q":
        sys.exit()
    if selection in ["1", "2"]: 
        if selection == "1":
            # Insert a new contract
            newContract()
        else:
            # Choose a contract from memory
            searchContract()
    else:
        # Error message for invalid selection
        print(color.RED + color.BOLD + "ERROR! Invalid selection\n" + color.END) 
        # Recall the function for a new selection
        menu()
        
def newContract():
    # Function to insert a new contract
    contractAddress = input("Type contract address \n")
    contractName = input("Type a name for the contract\n")
    # Add the new contract to the dictionary
    contracts[contractName] = contractAddress
    print(color.GREEN + color.BOLD + "Operation Succeded\n" + color.END) 
    

def searchContract():
    # Function to search for an existing contract
    print("Contracts list\n")
    # Print the list of contracts
    count = 0
    lst = {}
    for i in contracts:
        count += 1
        lst[count] = i
        print(count, i)

    # Request the name of the contract to use
    contractSelected = input("\nType the name / number of the contract you want to use, modify or delete\n")
    
    # Check if the selected contract exists
    if contractSelected not in contracts:
        try: 
            val = int(contractSelected)
            contractSelected = lst[val]
        except:
            # Error message if the contract does not exist
            print(color.RED + color.BOLD + "ERROR! Contract not found\n" + color.END)
            # Recall the function for a new selection
            searchContract()
    
    contractManage(contractSelected)
    
    
def contractManage(contractSelected):
    print("\n\n", color.BOLD + color.BLUE + contractSelected + color.END, "\n")
    print("1) Use\n2) Modify\n3) Delete\n\n q to quit")
    
    # Check user input
    selection = input("...")
    if selection == "q":
        sys.exit()
    if selection in ["1", "2", "3"]: 
        match selection:
            case "1": 
                contractUse(contractSelected)
            case "2":
                contractModify(contractSelected)
            case "3":
                print("Are you sure you want to delete? This action is not reversible\n   (Y/N)\n")
                selection2 = input(...)
                if selection2 not in ["Y", "y", "N", "n"]:
                    # Error message for invalid selection
                    print(color.RED + color.BOLD + "ERROR! Invalid selection\n" + color.END) 
                    # Recall the function for a new selection
                    contractManage(contractSelected)
                else:
                    match selection2:
                        case "Y":
                            del contracts[contractSelected]
                        case "y":
                            del contracts[contractSelected]
                        case "N":
                            contractManage(contractSelected)
                        case "n":
                            contractManage(contractSelected)

    else:
        # Error message for invalid selection
        print(color.RED + color.BOLD + "ERROR! Invalid selection\n" + color.END) 
        # Recall the function for a new selection
        contractManage(contractSelected)
        
    
def contractUse(contractSelected):
    print("\n\n", color.BOLD + color.BLUE + contractSelected + color.END)
    
    builder = pytezos.contract(contracts[contractSelected])
    
    print("Please login before continue\n")
    loginStatus = login()
    
    print_contractsInfo(contractSelected)
    
    while(1):
        selection = input("Which Entrypoints do you want to call?\n")
        try:
            entrypoint = getattr(builder, selection)
            break
        except:
            # Error message for invalid selection
            print(color.RED + color.BOLD + "ERROR! Invalid selection\n" + color.END) 
            # Doing the loop function for a new selection
    
    entrypoint_data = {'address': pytezos.address}
    
    operation = (
        builder
        .deposit(pytezos.key.public_key_hash())
        .with_amount(1)  
        .as_transaction()
    )
   
    


def login():
    '''
    selection = input("Insert your " + color.BOLD + "secret Key" + color.END + " or " + color.BOLD + "Mnemonic Phrase" + color.END + "\n q for quit\n... ")
    
    if selection == "q":
        sys.exit()
    
    try:
        key = Key.from_encoded_key(selection)
    except:
        try:
            selection = selection.split()
            key = Key.from_mnemonic(mnemonic = selection)
        except:
            # Error message for invalid selection
            print(color.RED + color.BOLD + "ERROR! Invalid selection\n" + color.END) 
            # Recall the function for a new selection
            return login()
    '''
    
    key = KEY ##REMOVE IT
    
    global pytezos
    pytezos = pytezos.using(key=key)
    print_walletInfo()
    
    return True

    
    
    
def contractModify(contractSelected):
    print("\n\n", color.BOLD + color.BLUE + contractSelected + color.END)
    print("Do you want to change:\n 1) Name\n 2) Address\n")
    selection = input("...")
    
    if selection in ["1", "2"]:
        match selection:
            case "1": 
                print_contractsInfo(contractSelected)
                address = contracts[contractSelected]
                del contracts[contractSelected]
                print("Insert new name\n")
                newname = input(...)
                contracts[newname] = address
                print(color.GREEN + color.BOLD + "Operation Succeded\n" + color.END) 
            case "2":
                print_contractsInfo(contractSelected)
                print("Insert new address\n")
                newaddress = input(...)
                contracts[contractSelected] = newaddress
                print(color.GREEN + color.BOLD + "Operation Succeded\n" + color.END) 
    else:
        # Error message for invalid selection
        print(color.RED + color.BOLD + "ERROR! Invalid selection\n" + color.END) 
        # Recall the function for a new selection
        contractModify(contractSelected)
    
    menu()