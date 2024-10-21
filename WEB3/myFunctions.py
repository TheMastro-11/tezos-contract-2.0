import myLibrary as lb

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
   
#dict with all contracts
contracts = {
    "simpleTransfer" : "KT1JPWgfwodv4j2zD1FATzfGsRCNkAhfVa7D",
    "auction" : "KT19Yw7uupmjzkCUsAmLEsujpZoR3LHwHjTJ",
    "kingOfTezos" : "KT1XTv6oPMgX6RbepELh8E6R1GCYU6rArX1x",
    "crowdFunding" : "KT1XQ3Vkxqd54kbpFozpSGd676zdSfPMqrPS",
    "hashTimedLockedContract" : "KT1SHqNQ7L3gSo9mPWUaTnwRh9RidTmbf7c7",
    "tokenTransfer" : "KT1DDT97EvCDR1PYLo1umZt3RuAdJ3Yg1ruZ"
    }

def print_contractsInfo(contractSelected):
    print("Alias :",contractSelected, "\nAddress :", contracts[contractSelected])
    
    
def menu():
    # Welcome message
    print("Welcome to UnicaTezos!\n")

    while(1):{
        # Menu selection
        menuSelection()
    }
        
    #builder = lb.pytezos.contract(contracts[contract])
    #print(builder.parameter)
    
def menuSelection():
    # Function for menu selection
    print("What would you like to do?\n")
    print("1) Insert new contract\n2) Open memory\n\
    \n q to quit")
    
    # Check user input
    selection = input("...")
    if selection == "q":
        lb.sys.exit()
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
        menuSelection()
        
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
        lb.sys.exit()
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
    address = contracts[contractSelected]
    print("ciao")
    
    
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
    
    menuSelection()