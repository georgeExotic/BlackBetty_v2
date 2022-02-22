import threading
import csv

dataInput = ['jorge','roa']
def logDataThread():
    i = 0

    fileName = "./test.csv"
    with open(fileName,"w") as csvFile:
        csvFileWriter = csv.writer(csvFile)
        while i < 50:
            csvFileWriter.writerow([i,dataInput])
            i+=1

if __name__ == "__main__":
    thread = threading.Thread(target=logDataThread)
    thread.start()