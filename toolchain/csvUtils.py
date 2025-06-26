import csv
import pprint

def csvReader(fileName):
    try:
        with open(fileName, mode='r', newline='', encoding='utf-8') as file_csv:
            csv_read = csv.reader(file_csv)

            print(f"--- Reading transcations: {fileName} ---")
            for row in csv_read:
                print("RIGA", row)
                print(row[0].split(";"))

            print("--- End ---")

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
                print(row[0].split(";"))
                i += 1
        
        
    newRow = [i+1, op_result["TotalCost"], op_result["Hash"]]
    with open(fileName, mode='a', newline='', encoding='utf-8') as file_csv:
        writer = csv.writer(file_csv)

        writer.writerow(newRow)
    