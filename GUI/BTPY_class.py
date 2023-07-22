#Import delle librerie
import sys
import time
import logging
#from serial import Serial
import serial
import serial.tools.list_ports
#import libraries
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
from PyQt5.QtGui import(
    QFont,
    
)
#variabili globali utili per la comunicazione bluethooth e dimensione del widget
STATO=0

BAUDRATE=115200
#dimensioni widget
HEIGHT_M=300
WIDTH_M=300

#classe segnali per comunicare con il codice principale
class SignalSearch(QObject):
    portname=pyqtSignal(str)

'''
####CLASSE BT_search:
CLasse principale del file python BTPY_class.py: creazione di un widget custom per il pairing 
del'applicazione con il dispositivo tramite una ricerca di stringe in ingresso
alle porte seriali del bluethoot del pc. La stringa che riceve in input dal device
è fissata dalla comunicazione UART del psoc ma il widget è possibile customizzarlo con
il compare di una stringa dato in ingresso al widget nel momento di dichiarazione dello stesso
Una volta ricevuta la stringa corretta dalla porta seriale salva il nome della 
seriale in una variabile che poi tramite segnale comunica al codice principale.
'''
class BT_search(QWidget):
    def __init__(self,str_compare):
        super().__init__()
        #dichiarazioni variabili utili per la gestione connessione del dispositivo
        self.connectionFlag=0

        #bottone principale widget per far avviare la ricerca del device
        self.butt_bt=QPushButton("Search for device")
        self.butt_bt.setMinimumSize(100,100)
        
        self.stato=0

        #label utilizzata per comunicare lo stato di connessione al dispositivo
        self.label_status=QLabel()
        self.listCom=[]
        
        #Baudrate di comunicazione
        self.baud=BAUDRATE

        #Dichiarazione seriale
        self.s=serial.Serial()

        #Dichiarazione connessione bottone alla funzione ScanCom
        self.butt_bt.pressed.connect(self.ScanCom)
        #variabile utile per il salvataggio della porta seriale
        self.portName=0
        
        #dichiarazioni variabili per il compare della stringa utile al pairing del dispositivo
        self.chreceived=''
        self.chserial=''
        self.ch_compare=str(str_compare)

        #dichiarazione classe segnali utili alla comunicazione con il codice principale
        self.signalport=SignalSearch()
        
        #funzione interna al widget per farlo visualizzare sulla mainWindow
        self.visual()
        

    #funzione utile a creare una lista utile dove salvare le porte com per analizzarle
    def ScanCom(self):
        
        #global STATO(utile per far capire lo stato di connessione)
        self.stato="SEARCHING"
        
        #funzione per cambiare stato della label
        self.ChangeStatus(self.stato)

        #lista per aggiungere l'elenco delle porte seriali
        listCom=[]
        
        #aggiungo le seriali alla lista
        for x in serial.tools.list_ports.comports():
            listCom.append(str(x.name))
        print(listCom)
        
        #funzione per il pairing dell'applicazione con il dispositivo
        self.SearchCom(listCom)
        

    def SearchCom(self,list):
        
        
        try:
            #controllo variabile di connessione
            if self.connectionFlag ==0:
                #per ogni elemento della lista delle seriali controllo la stringa in ingresso
                for xc in list:
                    #dichiarazione seriale
                    self.s=serial.Serial(xc,self.baud,write_timeout=0, timeout=10)
                    if self.s.is_open and self.connectionFlag==0:
                        print(xc)
                        #leggo stringa in ingresso
                        self.chreceived=self.s.read(7)
                        print(str(self.chreceived))
                        #controllo stringa
                        if self.ch_compare in str(self.chreceived):
                            print("connection estabilished")
                            self.s.write('a'.encode('utf-8'))
                            self.stato='CONNECTED'
                            #funzione per cambiare scritta label stato connessione
                            self.ChangeStatus(self.stato+':'+xc)
                            #chiusura porta seriale
                            self.s.close()
                            self.connectionFlag=1
                            #disabilito bottone
                            self.butt_bt.setDisabled(True)
                            self.portName=xc
                            #segnale per comunicare la porta seriale al codice principale
                            self.signalport.portname.emit(xc)

                            
                        


        #in caso di errore di connessione
        except serial.SerialException:
            if self.connectionFlag==0:
                #visualizzazione finestra di dialogo di errore    
                self.displayerrorport(xc)
                self.ChangeStatus('ERROR CONNECTION')
                
            


    #funzione cambio stato label
    def ChangeStatus(self, status):
        self.label_status.setText(str(status))
        

    #definizione layout di visualizzazione
    def visual(self):
        button_hlay = QHBoxLayout()
        button_hlay.addWidget(self.butt_bt)
        button_hlay.addWidget(self.label_status)
        self.setLayout(button_hlay)
        
       
    
    
    #funzione visualizzazione finestra di errore
    def displayerrorport(self,xc):
        
        self.ErrorCOM=ErrorW(300,200,'ERROR PORT CONNECTION: '+xc,'ERROR',10,False)
        self.ErrorCOM.exec_()


'''
###CLASS ERRORDIALOG
Classe widget custom per far uscire una schermata di errore con una scritta data in ingresso.
Usata per comunicare errori di connessioni alle porte seriali per il pairing Bluethoot
'''
class ErrorW(QDialog):
    #funzione di inizializzazione finestra
    def __init__(self,width,height,errorText,windowTitle,font_size,bold=bool):
        super(QDialog,self).__init__()
        #dichiarazioni variabili di grandezza della finestra
        self.width=width
        self.height=height
        self.setMinimumSize(width, height)
        #scritta di errore
        self.err_text=str(errorText)
        
        font=QFont('Arial',font_size)
        #settaggio font in grassetto a seconda della condizione in ingresso
        if bold:
            font=QFont('Arial',font_size,QFont.Bold)
        if not bold:
            font=QFont('Arial',font_size)

        
        
        self.win_text=str(windowTitle)
        self.Text=QLabel(self.err_text.upper())
        self.Text.setFont(font)

        
        
        self.setWindowTitle(self.win_text)

        #define layout
        hlay=QHBoxLayout()
        hlay.addWidget(self.Text)
        vlay=QVBoxLayout()
        vlay.addLayout(hlay)
        self.setLayout(vlay)
    
    


