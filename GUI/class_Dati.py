#importo librerie
import serial
import numpy as np
import sys
import ctypes
import time

from PyQt5.QtCore import (
    QObject,
    QThreadPool, 
    QRunnable, 
    pyqtSignal, 
    pyqtSlot
)

from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QPushButton,
    QComboBox,
    QHBoxLayout,
    QWidget,
    QDialog,
    QLabel,
    QMessageBox,
    QVBoxLayout,
    
)

#importo librerie da altri file utili per la visualizzazione errori
from BTPY_class import ErrorW
class WorkerKilled(Exception):
    pass

#funzione conversione dati in ingresso accelerometro
'''
Conversione complemento a 2


'''
def convert(int):
            b = 0
            for i in range(0, 10, 1):
                bit = int & 1 << i
                if not bit:
                    b = b | (1 << i)
            b = b+1
            int = b * -1
            return int


#classe segnali custom utili a comunicare con il codice principale
class DatiSignals(QObject):

    bool=pyqtSignal(bool)
    deviceport=pyqtSignal(str)
    dati=pyqtSignal(list,list,list)
    service_string=pyqtSignal(str)
    conn_status=pyqtSignal(str)
    dialog_string=pyqtSignal(str)


#classe thread Runnable utile a recepire in ingresso i dati dell'accellerometro
class DatiSerial(QRunnable):
    #iniziallizzazione classe, 'portname' e 'chcompare' dati in ingresso sono utili
    #a definire la porta seriale ela stringa di gestione comunicazione con il device
    def __init__(self,portname,chcompare):
        super().__init__()
        #dichiarazione seriale e variabili di raccolta dati
        self.serialPort = serial.Serial()
        self.chcompare=str(chcompare)
        self.PortName=str(portname)
        self.acc_vect = []
        self.X = []
        self.Y = []
        self.Z = []
        #variabili gestione thread e connessione
        self.is_killed=False
        self.FlagConnection=False

        #dichiarazione classe segnali
        self.signals=DatiSignals()

    #funzione per stoppare il thread
    def Abort(self):
        #variabile flag per il kill thread
        self.is_killed=True
        #scrittura seriale al device per resettare stato device
        try:
            self.serialPort.write('a'.encode('utf-8'))
        #gestione caso di perdita connessione con il device
        except serial.PortNotOpenError:
            self.signals.dialog_string.emit("no save")
            self.signals.service_string.emit("no save")
            #funzione di reset stato device
            self.Reset()

        #chiusura porta seriale    
        self.serialPort.close()
        self.FlagConnection=False
        
        time.sleep(0.01)
       
    #funzione di reset stato device
    def Reset(self):
        self.serialPort = serial.Serial(port = self.PortName, baudrate=115200,bytesize=8, timeout=None, stopbits=serial.STOPBITS_ONE)
        self.serialPort.write('a'.encode('utf-8'))
        self.serialPort.close()
        print("Reset")

    #funzione per resettare stato device in caso di chiusura applicazione
    def AppClose(self):
        
        try:
            self.serialPort = serial.Serial(port = self.PortName, baudrate=115200,bytesize=8, timeout=None, stopbits=serial.STOPBITS_ONE)
            self.serialPort.write('c'.encode('utf-8'))
            self.serialPort.close()
        #gestione casi device spento nel momento di chiusura applicazione
        except serial.PortNotOpenError:
            
            print("device OFF")
            pass
        except serial.SerialException:
            
            print("device OFF")
            pass    

    
        
    #thread per acquisizione dati
    @pyqtSlot()
    def run(self):
        #varibili per acquisizione pacchetti dati   
        header = 160
        tail = 192
        byte_to_receiv = 194
        sData = []
        #segnale per comunicare inizio thread al codice principale
        self.signals.service_string.emit("run")

            
        try:
                #check condizione connessione iniziale
                if self.FlagConnection==False:
                    try:
                        self.serialPort = serial.Serial(port = self.PortName, baudrate=115200,bytesize=8, timeout=None, stopbits=serial.STOPBITS_ONE)
                    #gestione errore non connessione porta seriale
                    except serial.SerialException:
                        self.signals.conn_status.emit("Serial Exception")
                    #check stringa in ingresso alla seriale
                    self.checkStringInit()
                    self.FlagConnection=True
                
                
                try:    
                    if(self.serialPort.is_open):
                        #controllo condizione thread
                        if self.is_killed==True:
                            
                            raise WorkerKilled
                        
                        #lettura dati accelerometro
                        sData = self.serialPort.read(194)
                        
                        byte =[]
                        
                        #controllo struttura dati header e tail
                        if (sData[0] == header and sData[193] == tail and len(sData) == byte_to_receiv):
                            #salvataggio dati in una variabile e riorganizzati in base all'accelerazione dei 3 assi
                            byte = [sData[i:i + 2] for i in range(1, len(sData) - 2, 2)]
                        #comunicazione in caso strutura dati non coerente    
                        else:
                            self.signals.service_string.emit("condition not satisfied")

                        vect = []
                        #conversione dati ottenuti dai 3 assi
                        for value in byte:
                            sign = value[1] & 0b10000000
                            a = (value[0] | value[1] << 8) >> 6
                            if sign:
                                a = convert(a)
                            vect.append(a)
                        #salvataggio accelerazioni nelle varibili
                        for i in range (0,len(vect),3):
                            self.X.append(vect[i])
                            self.Y.append(vect[i+1])
                            self.Z.append(vect[i+2])

                    
                        #comunicazione dati con il codice principali
                        self.acc_vect.append(vect)
                        self.signals.service_string.emit("vector ready")
                        self.signals.dati.emit(self.X,self.Y,self.Z)
                        
                    
                        

                        #richiamo funzione per la continua recezione dati
                        self.run()
                #gestione caso porta non aperta
                except serial.PortNotOpenError:
                    self.serialPort.close()

                    
                        
                        

        #funzione di kill del thread
        except WorkerKilled:
            
            self.serialPort.close()
            self.signals.service_string.emit("killed")
            
        

    #funzione check stringa in ingresso per inizio acquisizione dati
    def checkStringInit(self):
        #lettura stringa in ingresso seriale
        try:
            stringInit=str(self.serialPort.readline())
        except serial.PortNotOpenError:

            self.serialPort = serial.Serial(port = self.PortName, baudrate=115200,bytesize=8, timeout=None, stopbits=serial.STOPBITS_ONE)
            stringInit=str(self.serialPort.readline())
            

        
        self.signals.service_string.emit(stringInit)
        #comunicazione avvenuta connessione con il codice principale e invio stringa per inizio ricezione dati
        if self.chcompare in stringInit:
            
            self.serialPort.write('b'.encode('utf-8'))
            
            self.signals.service_string.emit("WROTE") 

   


             
                
    

