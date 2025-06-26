from contractUtils import *    
from folderScan import *
from csvUtils import *


def interactionSetup(client, contract):
    addressValid = getAddress()
    contractAddress = addressValid[contract]
    contractInterface = pytezos.contract(contractAddress)
    entrypoints = contractInterface.entrypoints
    del entrypoints["default"]
    
    i = 1
    entryList = []
    for entry in entrypoints:
        print(i, entry)
        entryList.append(entry)
        i += 1
        
    entrypointSel = int(input("Which entrypoint do you want to use?\n"))
    entrypointSchema = entrypointAnalyse(client=client, contractAddress=contractAddress)
    entrypointParam = entrypointSchema[entryList[entrypointSel-1]]
    parameters = None
    if entrypointParam != "unit":
        parameters = input("Insert parameters value: ")
    tezAmount = int(input("Insert tez amount: "))
    
    op_result = entrypointCall(client=client, contractAddress=contractAddress, entrypointName=entryList[entrypointSel-1], parameters=parameters, tezAmount=tezAmount)
    return callInfoResult(opResult=op_result)
    
def exportResult(opResult):
    sel = input("Do you want to export the result?(y/n):  ")
    
    if sel == "y":
        fileName = "transactionsOutput.csv"
        csvWriter(fileName=fileName, op_result=opResult)
        print("\nFile Updated!\n\n")
    
    
      
def main(client):
    stdPath = "../contracts/"
    
    operationSel = int(input("Now, select an option: \n"
        "1 Compile\n" 
        "2 Deploy\n" 
        "3 Interact\n\n"))

    allContracts = folderScan()
    print("\nContracts avaiable: \n")
    i = 1
    for contract in allContracts:
        print(i," " + contract)
        i += 1
        
   
    contractSel = int(input("Which contract do you want to use?\n"))
    contract = allContracts[contractSel-1]
    
    match operationSel:
        case 1:
            contractPath = stdPath+contract+"/"+contract+".py"
            compileContract(contractPath=contractPath)
            main(client=client)
        
        case 2: 
            if Path("./"+contract).exists():   
                michelsonPath = Path(f"./{contract}/step_001_cont_0_contract.tz").read_text()
                storagePath = Path(f"./{contract}/step_001_cont_0_storage.tz").read_text()
                op_result = origination(client=client, michelsonCode=michelsonPath, initialStorage=storagePath)
                contractInfo = contractInfoResult(op_result=op_result)
                addressUpdate(contract=contract, newAddress=contractInfo["address"])
            else:
                print("\n\033[1m Contract must be compiled before \033[0m\n\n")
            
            main(client=client)
            
        case 3: 
            op_report = interactionSetup(client=client, contract=contract)
            exportResult(opResult=op_report)
            main(client=client)
            

if __name__ in "__main__":
    print("Hi, welcome to the Tezos-Contract toolchain!\n")
    print("Here you can compile, deploy or interact with any contract from the archive.\n")
    with open("secretKey", 'r') as f:
        my_secret_key = f.read().strip()
        key = my_secret_key
        client = pytezos.using(shell="ghostnet", key=key)
    main(client)
    
    
        
    