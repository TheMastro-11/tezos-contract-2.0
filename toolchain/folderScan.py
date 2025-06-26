from pathlib import Path

def folderScan():
    contractsPath = Path("../contracts")


    completeList = [entry.name for entry in contractsPath.iterdir()]

    return completeList