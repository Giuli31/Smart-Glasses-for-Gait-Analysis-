 #librerie per gestione file locali
import os 
import glob

from PD_multiclassification import dtree_model

#librerie per filtraggio dati
from scipy.signal import butter,filtfilt
from scipy import stats as st

#funzione filtro lowpass per acquisizione dati
def butter_lowpass_filter(data, cutoff, fs, order):
    
    nyq = 0.5 * fs # Nyquist Frequency
    normal_cutoff = cutoff / nyq
    # Get the filter coefficients 
    b, a = butter(order, normal_cutoff, btype='low', analog=False)
    y = filtfilt(b, a,data)
    return y


#libreria per importare la data della sessione
import datetime as dt

#funzioni per comunicazione seriale
import serial
import numpy as np
import sys
import ctypes

#importo librerie grafiche
from PyQt5.QtGui import QPalette, QColor
from pyqtgraph import PlotWidget, plot
import pyqtgraph as pg

##libreria per gestione e salvataggio excel
import pandas as pd

#importo librerie pyqt
from PyQt5.QtCore import (
    QObject,
    QThreadPool, 
    QRunnable, 
    pyqtSignal, 
    pyqtSlot,
    QTimer,
    
    
)

from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QPushButton,
    QHBoxLayout,
    QWidget,
    QDialog,
    QLabel,
    QVBoxLayout,
    QGridLayout,
    QTabWidget,
    QListWidget,
    )

from PyQt5.QtGui import(
    QFont,
    )
#importo funzioni e classi dai file python esterni
from class_Dati import (
    DatiSerial,
    WorkerKilled,
    DatiSignals,
    convert
)
from BTPY_class import(
    BT_search,
    ErrorW
)



#classe Datastructure
'''
Struttura dati custom utile per il salvataggio dati per ogni acquisizione
salvata. Structure usata per il salvataggio nei file excel della sessione

'''
class DataStructure:
    def __init__(self):
        
        #variabili salvataggio dati
        self.minX=[]
        self.minY=[]
        self.minZ=[]
        self.maxX=[]
        self.maxY=[]
        self.maxZ=[]
        self.varX=[]
        self.varY=[]
        self.varZ=[]
        self.minAcc=[]
        self.maxAcc=[]
        self.varAcc=[]
        self.timesave=[]
        self.stepsave=[]
        self.results=[]
    
    #funzione salvataggio dati passati in ingresso
    def CreateData(self,X,Y,Z,acc,time,passi,results):
        self.minX.append(min(X))
        self.minY.append(min(Y))
        self.minZ.append(min(Z))
        self.maxX.append(max(X))
        self.maxY.append(max(Y))
        self.maxZ.append(max(Z))
        self.varX.append(np.var(X))
        self.varY.append(np.var(Y))
        self.varZ.append(np.var(Z))
        self.minAcc.append(min(acc))
        self.maxAcc.append(max(acc))
        self.varAcc.append(np.var(acc))
        self.timesave.append(time)
        self.stepsave.append(passi)
        self.results.append(results)

    #funzione reset struttura dati per inizio nuova sessione
    def Reset(self):
        self.minX=[]
        self.minY=[]
        self.minZ=[]
        self.maxX=[]
        self.maxY=[]
        self.maxZ=[]
        self.varX=[]
        self.varY=[]
        self.varZ=[]
        self.minAcc=[]
        self.maxAcc=[]
        self.varAcc=[]
        self.timesave=[]
        self.stepsave=[]
        self.results=[]
        print("data reset")

#classe segnali per far comunicare classi esterni con la main window
class Signals(QObject):
    signal_int=pyqtSignal(int)
    string=pyqtSignal(str)


#classe lista per visualizzare sessioni passate salvati in locali come file excel nell cartella 'Session Excel'
class List_Acquisitions(QWidget):
    def __init__(self):
        QWidget.__init__(self)
        #definizione layout
        layout = QGridLayout()
        self.stringalista=Signals()


        self.setLayout(layout)
        self.listwidget = QListWidget()
        self.Qlistexcel=QListWidget()
        
       
        self.listwidget.clicked.connect(self.clicked)
        self.Qlistexcel.clicked.connect(self.clicked)
        layout.addWidget(self.Qlistexcel)

    #funzione per visualizzare risultati sessioni passati in caso si clicchi sulla lista
    def clicked(self, qmodelindex):
        item = self.Qlistexcel.currentItem()
        self.stringalista.string.emit(str(item.text()))
        print(item.text())

    #funzione aggiornamento lista con l'elenco file excel
    def aggiorna(self):
        self.Qlistexcel.clear()
        #salvo la main directory per la gestione dei file
        wd=os.getcwd()
        #cerco la cartella dove sono salvati gli excel
        os.chdir(wd+"/Session Excel")
        listexcel=glob.glob('*.xlsx')
        
        for x in range(len(listexcel)):
            
            #aggiungo alla lista i file excel trovati
            self.Qlistexcel.insertItem(x,listexcel[x])
        #cambio directory di lavoro del codice a quella principale
        os.chdir(wd)

        


#classe di finestra di dialogo per chiedere all'utente se è intenzionato a salvare i dati dell'acquisizione
class SaveDialog(QDialog):
    def __init__(self,text,prediction):
        super(QDialog,self).__init__()
        self.maintext=str(text)
        maintextfont=QFont('Arial',10)
        
        
        #gestione risultato acquisizione in ingresso alla classe
        if prediction==0:
            resulttext="Normal gait detected"
        if prediction==1:
            resulttext="Anomalous gait detected.Further examinations suggested"
        if prediction==2:
            resulttext="Serious anomalies on gait detected. Subject may require assistances"
        self.MainTextlabel=QLabel(self.maintext)
        self.MainTextlabel.setFont(maintextfont)
        #label per la visualizzazione dei risultati
        self.result_label=QLabel("Result acquisition: "+resulttext)
        fontresult=QFont('Arial',12,QFont.Bold)
        self.result_label.setFont(fontresult)
        #bottoni per il salvataggio dei dati
        self.si=QPushButton("Yes")
        self.no=QPushButton("No")
        self.flag=False
        self.segnale=Signals()
        

        #impostazione layout
        hlayout=QHBoxLayout()
        
        hlayout.addWidget(self.si)
        hlayout.addWidget(self.no)


        vlayout=QVBoxLayout()
        vlayout.addWidget(self.result_label)
        vlayout.addWidget(self.MainTextlabel)
        vlayout.addLayout(hlayout)

        self.setLayout(vlayout)
        self.setWindowTitle("SaveData")
        #connessioni funzioni bottoni per il salvataggio dati
        self.si.pressed.connect(self.PressedSi)
        self.no.pressed.connect(self.PressedNo)

    #funzioni gestione salvataggio dati acquisizione
    def PressedSi(self):
        #flag salvataggio dati
        self.flag=True
        fontresult=QFont('Arial',12,QFont.Bold)
        
        self.segnale.signal_int.emit(0)
        self.si.setDisabled(True)
        self.no.setDisabled(True)
        self.MainTextlabel.setText("Acquisition saved, close this window")
        self.MainTextlabel.setFont(fontresult)
            

    def PressedNo(self):
        self.flag=False
        fontresult=QFont('Arial',12,QFont.Bold)
        
        self.segnale.signal_int.emit(0)
        self.si.setDisabled(True)
        self.no.setDisabled(True)
        self.MainTextlabel.setText("Acquisition not saved, close this window")
        self.MainTextlabel.setFont(fontresult)
        
#MAIN WINDOW
class MainW(QMainWindow):
    def __init__(self):
        super(MainW,self).__init__()
        #variabili per la gestione dati
        self.X=[]
        self.Y=[]
        self.Z=[]
        self.time=[]
        self.provatimer=0
        self.portname=''
        self.totalsignal=[]
        self.passi=None
        #flah per la gestione salvataggio dati
        self.CreateDataFlag=None

        self.resultAcuisition=None
        #dataframe risultato predizione modello
        self.dataframe_pr=None
        #salvataggio predizione
        self.prediction=None
        #salvataggio data sessione
        today_date=dt.date.today()
        
        self.date=str(today_date)
        print(self.date)
        

        #DataStructure per il salvataggio sessione
        self.DataSession=DataStructure()
        #variabile gestione finestra di salvataggio
        self.ShowDialog=True
        
        
        
        #####Graph#####
        pen = pg.mkPen(color=(255, 0, 0))
        self.graphWidget = pg.PlotWidget()
        self.graphWidget
        self.graphWidget = PlotWidget(pen=pen)
        self.graphWidget.showGrid(x=True, y=True)
        self.graphWidget.setBackground('w')
        self.graphWidget.setTitle("Acceleration measurement")
        #Graph: Add axis labels
        styles = {'color': 'k', 'font-size': '15px'}
        self.graphWidget.setLabel('left', 'Acceleration [g]', **styles)
        self.graphWidget.setLabel('bottom', 'Acquisition Data', **styles)
        self.graphWidget.addLegend()
        self.graphWidget.setXRange(-0.5,10)
        self.graphWidget.setYRange(-20,20)

        ####label step
        self.label_steps = QLabel()
        self.label_steps_text = QLabel('The number of Steps is:', self)
        
        self.label_steps.resize(170, 40)
        self.label_steps_text.resize(50, 40)
        


        ####timer####
        self.timerstring=QLabel("Time: ")
        #size 
        self.timerstring.resize(50, 40)
        
        
        self.timerstring.move(560,25)
        self.timelabel=QLabel()
        self.timelabel.resize(50, 40)
        
        self.timelabel.move(560, 25)

        self.timer =QTimer()
        self.timer.timeout.connect(self.showTimer)
        self.start = False
        self.count = 0
        self.firststart=True

        

        ####excel###
        #variabile conteggio file excel
        self.n_ex=0
        
        
        
        
        #dichiarazioni bottoni
        
        self.startAcq=QPushButton("Start Acquisition")
        self.startAcq.setDisabled(True)
        self.stopAcq=QPushButton("Stop Acquisition")
        self.stopAcq.setDisabled(True)
        self.ShowData=QPushButton("SaveData")
        self.ShowData.setDisabled(True)
        #bottone per nuova sessione
        self.NewSession=QPushButton("New Session")
        self.NewSession.setDisabled(True)
        
        #dichiarazione lista
        self.lista=List_Acquisitions()

        #dichiarazione classe per acquisizione dati
        self.Dati=DatiSerial(self.portname,'Ready')
        
        #thread
        self.ThreadDati=QThreadPool()
        
        #classe per il pairing del device
        self.searchWdiget=BT_search('Ready')
        
        #dichiarazione connessione segnale classe pairing device
        self.searchWdiget.signalport.portname.connect(self.SetPort)
        
        #dichiarazione connessioni bottoni
        self.startAcq.pressed.connect(self.StartAcquisition)
        self.stopAcq.pressed.connect(self.AbortAcquisition)
        self.ShowData.pressed.connect(self.ShowVectData)
        self.NewSession.pressed.connect(self.NewSessionStart)
        
        #segnali dall'acquisione dati
        
        self.Dati.signals.service_string.connect(self.SignalThreadStr)
        self.Dati.signals.dati.connect(self.SignalDati)
        self.Dati.signals.conn_status.connect(self.CheckStatusConnection)
        self.Dati.signals.dialog_string.connect(self.CheckDialogCondition)
        
        ##result list show
        #dichiarazione funzione per mostrare a video i risulatati sessioni passate
        self.lista.stringalista.string.connect(self.resultshow)
        
            
        #gestione lista
        try:
            self.lista.aggiorna()    
        except FileNotFoundError:
            print('file not found')
            pass 

        ######DEFINE GUI LAYOUT######
    
        self.initGUI()

        ####palette
        self.qp = QPalette()
        self.qp.setColor(QPalette.Window, QColor(141, 201, 247)) #azzurro 172, 216, 227 - 141, 201, 247
        self.qp.setColor(QPalette.WindowText, QColor(2, 43, 125)) #scritte blu 2, 43, 125
        self.qp.setColor(QPalette.Base, QColor(205, 229, 247)) #sfondo secondo tab 205, 229, 247
        
        self.qp.setColor(QPalette.Text, QColor(2, 43, 125)) # scritte tab
        self.qp.setColor(QPalette.Button, QColor(169, 185, 196)) #bottoni grigi
        self.qp.setColor(QPalette.ButtonText, QColor(2, 43, 125))
        

        app.setPalette(self.qp)

    
    #funzione controllo condizione finestra di dialogo
    def CheckDialogCondition(self,str):
        print(str+"  fun")
        if "no save" in str:
            
            self.ShowDialog=False
            

    #funzione start acquisizione
    def StartAcquisition(self):
            #reset dati
            self.ResetXYZ()
            #acquisizione dati
            self.graphWidget.clear()
            self.Dati=DatiSerial(str(self.portname),'Ready')
            self.Dati.signals.service_string.connect(self.SignalThreadStr)
            self.Dati.signals.dati.connect(self.SignalDati)
            
            
            self.FlagStart=True
            self.ThreadDati=QThreadPool()

            self.ThreadDati.start(self.Dati)
            
            self.Dati.is_killed=False
            
            self.startAcq.setDisabled(True)
            self.label_steps.setText(str('0'))
    #funzione reset dati        
    def ResetXYZ(self):
        self.X=[]
        self.Y=[]
        self.Z=[]
        #print to check
        print("Reset Data")
    
    #funzione sto acquisizione
    def AbortAcquisition(self):
        #controllo condizione finestra di dialogo
        self.Dati.signals.dialog_string.connect(self.CheckDialogCondition)
        
        self.resetTimer()
        
        #abort thread
        self.Dati.Abort()
        
        
        
        
        
        if self.ShowDialog:
            #creazione dataframe
            self.CreateDataFrame(self.X,self.Y,self.Z,self.totalsignal,self.provatimer,self.passi)

            #predizione modello per l'acquisizione
            prediction = dtree_model.predict(self.dataframe_pr)
            self.prediction=int(prediction[1])
            print(self.prediction)
            #finestra di salvataggio
            self.messageSave()

            
        if not self.ShowDialog:
            self.ShowDialog=True
       
        
       
        #riabilito bottone start acquisizione
        self.startAcq.setDisabled(False)    
        
    #visualizzazione finestra di salvataggio dati
    def messageSave(self):
      
        self.dialogsave=SaveDialog("Do you want to save this acquisition?",self.prediction)
        self.dialogsave.segnale.signal_int.connect(self.AppendVectorAcquisition)
        self.dialogsave.exec_()
        
    

    #fuzione per creazione database dati
    def AppendVectorAcquisition(self):
        
        

        if self.dialogsave.flag:
            self.DataSession.CreateData(self.X,self.Y,self.Z,self.totalsignal,self.provatimer,self.passi,
            self.prediction
            )
            #print to check
            print("Acquisition saved")
        
        

    #comunicazione con thread
    def CheckStatusConnection(self,stringa):
        if "Serial Exception" in stringa:
            self.startAcq.setDisabled(False)
    #comunicazione thread
    def SignalThreadStr(self,stringa):
        print(str(stringa))
    #salvataggio dati in ingresso
    def SignalDati(self,x,y,z):
        #filtraggio dati
        self.X=butter_lowpass_filter(x,2,50,3)
        self.Y=butter_lowpass_filter(y,2,50,3)
        self.Z=butter_lowpass_filter(z,2,50,3)
        
        
        #controllo lunghezza vettore dati
        if len(self.X) and len(self.Y) and len(self.Z):
            l=len(self.Z)
        #plot dati sul grafico
        self.draw(self.X,self.Y,self.Z)
        #start timer
        if self.firststart:    
            self.startTimer()
            self.firststart=False

        print("x:{}\r\ny:{}\r\nz:{}".format(self.X[l-1],self.Y[l-1],self.Z[l-1]))
    #funzione per plottaggio dati
    def draw(self,X,Y,Z):
        #calcolo accelerazione totale
        ax_sq = np.square(X)
        ay_sq = np.square(Y)
        az_sq = np.square(Z)
        acc = np.sqrt(ax_sq + ay_sq + az_sq)
        
        self.totalsignal=acc

        l=len(acc)
        length=l-1
        l = np.arange(0, length+1, 1)

        self.graphWidget.enableAutoRange()
        self.graphWidget.clear()
        
        self.graphWidget.plot(l,acc)
        #conteggio passi
        steps=self.ThresholdCount(acc,l)
        self.passi=steps-2
        #cambio label conteggio passi
        if self.passi<0:
            self.label_steps.setText(str(0))
        if self.passi>0:
            self.label_steps.setText(str(self.passi))

    #funzione conteggio passi
    def ThresholdCount(self,a,l):
        thr = 260 #soglia settata 
        count = 0
        for i in l:
            if not a[i-1]>=thr:
                if a[i] >= thr:
                    
                    count += 1
        steps = int(count)
        return steps
    
    #SHOW DATAS
    #funzione salvataggio excel sessione
    def ShowVectData(self):

     

        self.ExcelSave(self.DataSession)
        
        self.lista.aggiorna()  

    #funzione inizializzazione nuova sessione di acquisizioni
    def NewSessionStart(self):
        self.DataSession.Reset()

        
        
    
    #EXCEL FUNCTION
    # #funzione dalvataggio dati in excel tramite database in ingresso 
    def ExcelSave(self,data):
        
        
        #controllo file locali con creazione cartella sessioni
        wd=os.getcwd()
        
        listexcel=glob.glob(wd+'*.xlsx')
        
        if not listexcel:
            try:
                os.mkdir("Session Excel")
                os.chdir(wd+"/Session Excel")
                
                
            except FileExistsError:
                os.chdir(wd+"/Session Excel")
                
                listexcel=glob.glob(self.date+'*.xlsx')
                
                
                 
                
                self.n_ex=len(listexcel)
                

                

        

        
        
        #creazione database per excel
        data={ 'minX':data.minX,
            'minY':data.minY,
            'minZ':data.minZ,
            'maxX':data.maxX,
            'maxY':data.maxY,
            'maxZ':data.maxZ,
            'varX':data.varX,
            'varY':data.varY,
            'varZ':data.varZ,
            'minAcc':data.minAcc,
            'maxAcc':data.maxAcc,
            'varAcc':data.varAcc,
            'tempo':data.timesave,
            'passi':data.stepsave,
            'risultati':data.results
            }
        
        #salvataggio excel
        df=pd.DataFrame(data=data)
        
        df.to_excel(self.date+"_Session_{}.xlsx".format(str(self.n_ex).zfill(3)),)
        self.n_ex+=1
        os.chdir(wd)
        
       


    #creazione database per la predizione del modello
    def CreateDataFrame(self,X,Y,Z,acc,timer,passi):
        minX=[0]
        minY=[0]
        minZ=[0]
        maxX=[0]
        maxY=[0]
        maxZ=[0]
        varX=[0]
        varY=[0]
        varZ=[0]
        minAcc=[0]
        maxAcc=[0]
        varAcc=[0]
        timesave=[0]
        stepsave=[0]
        #insert data
        minX.append(min(X))
        minY.append(min(Y))
        minZ.append(min(Z))
        maxX.append(max(X))
        maxY.append(max(Y))
        maxZ.append(max(Z))
        varX.append(np.var(X))
        varY.append(np.var(Y))
        varZ.append(np.var(Z))
        minAcc.append(min(acc))
        maxAcc.append(max(acc))
        varAcc.append(np.var(acc))
        timesave.append(timer)
        stepsave.append(passi)
        data={ 'minX':minX,
            'minY':minY,
            'minZ':minZ,
            'maxX':maxX,
            'maxY':maxY,
            'maxZ':maxZ,
            'varX':varX,
            'varY':varY,
            'varZ':varZ,
            'minAcc':minAcc,
            'maxAcc':maxAcc,
            'varAcc':varAcc,
            'tempo':timesave,
            'passi':stepsave,
            }

        self.dataframe_pr=pd.DataFrame(data=data)






    #salvataggio porta seriale utile alla connessione
    #in ingresso viene passato il risultato del pairing della funzione pairing device
    def SetPort(self,Port):
        self.portname=str(Port)
        print(self.portname)
        
        self.startAcq.setDisabled(False)
        self.stopAcq.setDisabled(False)
        self.ShowData.setDisabled(False)
        self.NewSession.setDisabled(False)

    ####Timer Functions###
    def stopTimer(self):
        self.timer.stop()
        self.start = False
        self.start_btn.setDisabled(False)

    def showTimer(self):
        if self.start:
            self.count += 0.1

        if self.start:
            text_timer = str(round(self.count, 2)) + ' s'
            self.timelabel.setText(text_timer)

    def startTimer(self):
        self.start = True
        self.timer.start(100)
        

    def resetTimer(self):
        self.provatimer=self.count
        self.count = 0
       
        self.start = False
        self.firststart=True
        
    
    #funzione per mostrare i risultati sessioni vecchie
        
    def resultshow(self,session):
        sessione_click=str(session)
        wd=os.getcwd()
        os.chdir(wd+"/Session Excel")
        listsession=glob.glob('*.xlsx')
        if sessione_click in listsession:
            
            exc=pd.read_excel(sessione_click)
            try:
                results=exc.iloc[:,15]
                results=list(results)
                moderesult=st.mode(results,axis=None,keepdims=False)

                label=QLabel(str(moderesult))

                stringalabel=QLabel("Result: "+str(moderesult[0]))
                font=QFont('Arial',50)
                stringalabel.setFont(font)
                
            
            except IndexError:
                self.ErrorCOM=ErrorW(300,200,'Session selected does not have prediction result(check integrity file)','ERROR',10,False)
                self.ErrorCOM.exec_()
                moderesult="result not found"
                stringalabel=QLabel("Result: Not Found")
                font=QFont('Arial',50)
                stringalabel.setFont(font)
                os.chdir(wd)
                

            
            #aggiunta legenda per capire i risultati prove passate
            legend="Legend:\n0=Normal Gait\n1=Require further examinations\n2=Patient need assistance"

            
            
            label_prova_pg=pg.TextItem(text=str(stringalabel.text()),color=(256, 256, 256),anchor=(0.5,0.5))
            label_prova_pg.setFont(font)


            fontlegend=QFont('Arial',10)
            label_legend_pg=pg.TextItem(text=str(legend),color=(256, 256, 256),anchor=(0,1))
            label_legend_pg.setPos(-0.5,-0.7)
            label_legend_pg.setFont(fontlegend)
            
            
            
            
            
            self.graphWidget.clear()
            self.graphWidget.setXRange(-1,1)
            self.graphWidget.setYRange(-1,1)
            self.graphWidget.hideAxis('left')
            self.graphWidget.hideAxis('bottom')
            self.graphWidget.setTitle("Session Result")

            
            self.graphWidget.addItem(label_prova_pg,ignoreBounds=True)
            self.graphWidget.addItem(label_legend_pg,ignoreBounds=True)
            
            
            os.chdir(wd)


    
    #definizione layout GUI
    def initGUI(self):
        self.setWindowTitle("G.G.A.D.(Glass Gait Analysis Device)")
        
        WindowWid=QWidget()
        mainlayout=QGridLayout()

        
        

        #layout for buttons
        AcqButtonlayH=QHBoxLayout()
        AcqButtonlayH.addWidget(self.startAcq)
        AcqButtonlayH.addWidget(self.stopAcq)
        AcqButtonlayV=QVBoxLayout()
        AcqButtonlayV.addLayout(AcqButtonlayH)
        AcqButtonlayV.addWidget(self.ShowData)
        AcqButtonlayV.addWidget(self.NewSession)
        

        ##label fontsize
        labelfont=QFont('Arial',9)
        #layoulabels steps
        layoutlabel=QHBoxLayout()
        self.label_steps.setFont(labelfont)
        layoutlabel.addWidget(self.label_steps_text)
        self.label_steps_text.setFont(labelfont)
        layoutlabel.addWidget(self.label_steps)

        #layoutlabels timer
        layoutlabel_timer=QHBoxLayout()
        self.timerstring.setFont(labelfont)
        layoutlabel_timer.addWidget(self.timerstring)
        self.timelabel.setFont(labelfont)
        layoutlabel_timer.addWidget(self.timelabel)

        #sx tab main window
        sx_lay_w=QWidget()
        
        tabAcquisition=QWidget()
        tabAcquisition.layout=QVBoxLayout()
        tabAcquisition.layout.addLayout(AcqButtonlayV)
        tabAcquisition.layout.addWidget(self.searchWdiget)
        tabAcquisition.layout.addLayout(layoutlabel)
        tabAcquisition.layout.addLayout(layoutlabel_timer)

        tabAcquisition.setLayout(tabAcquisition.layout)

        tablist=QWidget()
        tablist.layout=QVBoxLayout()
        tablist.layout.addWidget(self.lista)
        tablist.setLayout(tablist.layout)


        tabsx=QTabWidget()
        tabsx.addTab(tabAcquisition,'Acquisition')
        tabsx.addTab(tablist,'Excel files')
        tabsx.tabBarClicked.connect(self.clearGraph)
        #tabsx.setMaximumWidth(400)
        tabsx.resize(250,600)
        '''
        tabsx.setMaximumSize(250,600)
        
        tabsx.setMinimumSize(250, 250)
        '''

        sx_lay_w.layout=QVBoxLayout()
        sx_lay_w.layout.addWidget(tabsx)
        sx_lay_w.setLayout(sx_lay_w.layout)
        


        


        #dx tab
        dx_lay_w=QWidget()
        

        dx_HL=QVBoxLayout()
        
        dx_HL.addWidget(self.graphWidget)
        dx_lay_w.setLayout(dx_HL)

        #mainlayout
        mainlayout.addWidget(sx_lay_w,0,0)
        mainlayout.addWidget(dx_lay_w,0,1)
        WindowWid.setLayout(mainlayout)

        
        

        self.setCentralWidget(WindowWid)
    #funzioni per pulire il grafico
    def clearGraph(self):
        self.graphWidget.clear()
        self.graphWidget.setXRange(-0.5,10)
        self.graphWidget.setYRange(-20,20)
        self.graphWidget.showAxis('left')
        self.graphWidget.showAxis('bottom')
        self.graphWidget.setTitle("Acceleration measurement")
    #funzione gestione stato device in chiusura dell'applicazione
    def closeEvent(self, event):
        if event.spontaneous():
            self.Dati=DatiSerial(str(self.portname),'Ready')
            self.Dati.AppClose()
            print("app closed")
    
    

            

        


 





if __name__ == '__main__':
    
    app = QApplication(sys.argv)
    w = MainW()
    w.show() 
    sys.exit(app.exec_())



        
