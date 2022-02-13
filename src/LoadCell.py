'''
Black Betty load cell library 
hardware used : 
    hx711
    Load Cell = FC23 (0-50 lbf)
'''
import json
import time
import os
import pickle
import RPi.GPIO as GPIO #import I/O interfaceq
from hx711 import HX711 #import HX711 class

class LoadCell():
    def __init__(self):
        GPIO.setmode(GPIO.BCM)  #set GPIO pind mode to BCM
        GPIO.setwarnings(False)
        self.pd_sckPin=20
        self.dout_pin=21
        self.gain = 128
        self.channel = 'A'
        self.configFileName = 'calibration.vlabs'
        self.calibrationFilePath = '/home/pi/BlackBetty_v2/calibrationFile/calibration.vlabs'
        
        ##Status
        self.calibrated = 0
        self.calibrationPart1 = 0 

        self.ratio = 0
        self.knownWeight = 0 


    def connectLoadCell(self):
        ##HX711 object 
        self.cell = HX711(self.dout_pin,self.pd_sckPin,self.gain,self.channel)

    def _closeGPIOconnection(self):
        GPIO.cleanup()

    def loadCalibrationFile(self):
        ##checking for previous calibration 
        if os.path.isfile(self.calibrationFilePath):
            with open(self.calibrationFilePath,'rb') as File:
                self.cell = pickle.load(File)   #loading calibrated HX711 object
                self.calibrated = 1 #update status
        else: 
            self.calibrated = 0 

    def deleteCalibrationFile(self):
        if os.path.isfile(self.calibrationFilePath):
            os.remove(self.calibrationFilePath)
        else:
            print("ERROR: {} FILE NOT FOUND".format(self.calibrationFilePath))

    def calibrateLoadCell_part1(self):
        self.deleteCalibrationFile()
        err = self.cell.zero() #set zero offset/ use to tare 
        if err:
            raise Exception('CALIBRATION LOAD CELL PART 1')
        else:
            #measure with no load --> raw data mean
            self.cell.get_raw_data_mean()
            self.calibrationPart1 = 1 


    #place calibration object before running this function
    #known weight must be in KG
    def calibrateLoadCell_part2(self,knownWeight):
        self.knownWeight = knownWeight
        if self.calibrationPart1 == 0:
            raise Exception('CALIBRATION PART 1 MUST BE DONE FIRST')
        else:
            #measure with load --> data mean (raw data - offset)
            secondReading = self.cell.get_data_mean()
            self.knownWeight = float(self.knownWeight) 
            self.ratio = secondReading/self.knownWeight
            self.cell.set_scale_ratio(self.ratio)
            self.calibrated = 1
            print("CALIBRATION PART 2 FINISHED")


    def readForce(self):
        if self.calibrated == 1:
            force_reading_raw = self.cell.get_weight_mean(5)
            force_reading_kg = round(force_reading_raw,3)
            # print(force_reading_kg)
        else:
            force_reading_kg = 0
            print('CALIBRATION FILE NOT FOUND')
        return force_reading_kg

    def zeroCell(self):
        self.cell.zero()
        print("MACHINE SUCCESFULLY TARED (ZERO)")

   
    def saveCalibrationPICKLE(self):
        with open(self.calibrationFilePath, 'wb') as savedCalibration:
            pickle.dump(self.cell, savedCalibration)
            savedCalibration.flush()
            os.fsync(savedCalibration.fileno())

if __name__ == "__main__":
    LC = LoadCell()
    LC.loadCalibrationFile()

    end_time = time.time() + 5

    while (time.time() < end_time):
        LC.readForce()
        time.sleep(0.1)

    user_input = input("input = ")
    if user_input == "true":

        LC.calibrateLoadCell_part1()
        weight = input("input known weight in KG")
        LC.calibrateLoadCell_part2(weight)
        LC.saveCalibrationPICKLE()
        LC.loadCalibrationFile()

    else:
        pass



    while True:
        LC.readForce()
        time.sleep(0.1)
        
