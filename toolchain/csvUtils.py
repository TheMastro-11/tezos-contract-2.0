import csv
from folderScan import *

def csvReader():
    executionTraces = folderScan("execution_traces")
    executionTracesDict = {}
    try:
        for trace in executionTraces:
            fileName = "execution_traces/"+trace
            rows = {}
            
            with open(fileName, mode='r', newline='', encoding='utf-8') as file_csv:
                csv_read = csv.reader(file_csv)

                i = 0
                for row in csv_read:
                    newRow = row[0].split(";")
                    rows[newRow.pop(0)] = newRow
                    i += 1
                    
            executionTracesDict[trace.replace(".csv","")] = rows
            
        return executionTracesDict
    
    except FileNotFoundError:
        print(f"Error: File '{fileName}' not found.")
    except Exception as e:
        print(f"Error: {e}")
    


def csvWriter(fileName, op_result):
    i = 0
    with open(fileName, mode='r', newline='', encoding='utf-8') as file_csv:
        csv_read = csv.reader(file_csv)
        for row in csv_read:
                print("RIGA", row)
                if row != []:
                    print(row[0].split(";"))
                i += 1
        
        
    newRow = [i+1, op_result["TotalCost"], op_result["Hash"]]
    with open(fileName, mode='a', newline='', encoding='utf-8') as file_csv:
        writer = csv.writer(file_csv)

        writer.writerow(newRow)
    