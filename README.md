# Smart Glasses for Gait Analysis in Parkinson’s Disease 
## Table of contents
* [General info](#general-info)
* [Technologies](#technologies)
* [How To Use](#how-to-use)

## General info
Parkinson’s disease (PD) is one of the most common neurodegenerative disorders of the central nervous system, which predominantly affects patients’ motor functions, movement, and stability. In recent years, there has been an increase in the usage of wearable sensors for PD symptom monitoring aiming at anticipating the disease diagnosis and thus providing a most efficient quality of care. In this context, the developed device aims to provide objective information on the motor state, analysing the patient's gait and classifying it. In order to accomplish this task, the SGGA device is based on the Timed Up and Go (TUG) test. This is a simple test to measure a person’s level of mobility. It measures the time it takes for a person to get up from a chair, walk three meters, turn around, return to the chair and sit down again. Some sources suggest that a score of 10 seconds or less indicates normal mobility; times between 11 and 20 seconds are within normal limits for elderly with fragility and disabled patients; times longer than 20 seconds indicate that the person needs external assistance and the need for further examinations and interventions. A score greater than 30 seconds suggests that the person may be prone to falls. The TUG was developed from a more articulated test, the Get-up and Go. The SGGA device isn't a classifier of Parkinson’s disease, but it can be a useful tool for the study of symptoms and progression of this disease. 

## Technologies
Project is created with:
* EAGLE - for the design of the PCB
* PSoC Creator - for the program of the microcontroller 
* PyQt5 - for the development the graphical user interface

## How To Use
* [Physical Device](#physical-device)
* [Interface](#interface)
* [Acquisition](#acquisition)
* [Bugs](#bugs)

### Physical Device
The SGGA device is a wearable device composed by two main parts. The first is a small case equipped with accelerometer and wearable on the own glasses or given glasses. The second part is a bigger case that contains the PCB and its components. It's equipped with a belt that must be fastened around the patient’s waist. On the short side of the case, it's possible to check the state of the SGGA device thanks to the presence of two LEDs. The red LED shows that the device is powered, so it works. The green LED shows the connection established between the device and the application. In particular, the green flashing LED indicates that the device is ready to send data to the application, while, when the green LED becomes fixed, it indicates that the device is sending data registered by the accelerometer to the application. 

### Interface
The graphic user interface allows the user to visualize the results of the Timed Up and Go (TUG) test. On the right side of the screen, it is possible to see a graph that shows the acceleration trend over time. On the left side there are two tabs: "Acquisition" and "Excel files". 
The tab "Acquisition" contains buttons "Start Acquisition", "Stop Acquisition", "Save Data", "New Session" and "Search for device". Here it is also possible to visualize a timer and a steps counter. 
The tab "Excel files" shows past acquisitions that are saved on Excel files named with data and progression number of session. Clicking on one of these files, it is possible to visualize on the screen a number between 0 and 2 that indicates the class of the result (0 - Normal Gait, 1 - Require further examinations, 2 - Patient need assistance). This classification is made using a machine learning model, the Decision Trees, that is trained using a set of acquisitions based on TUG test permed by healthy subject trying also to reproduce the gait of impaired people. 

### Acquisition 
The first step of the acquisition is the preparation of the patient. He/She should wear the belt and place the case on the side so that the LED lights are visible. Red LED will light up when the device is connected to the power supply. After that, the patient must wear glasses equipped with the second smaller case. Let sit the patient in the chair and so he/she is ready for the test. 

Now, the user has to run the application using the Python file named "FinalGUI.py" and start the pairing of the device with the application. Once the GUI is open, the user must push the button "Search for device" in order to connect the device, if the connection is successful the green LED will start flashing. At this point, the device is ready for start the acquisition. 

When the patient is ready to perform the test, the user has to push the button "Start Acquisition" and the timer and the steps counter start at the same time. On the graph it's possible to visualize in real-time the acceleration trend of the patient's walk. 

Once the patient has completed the test, the user has to push the button "Stop acquisition". At this point a dynamic window will open and it will show the result of the test, classifying it into "Normal gait detected", "Anomalous gait detected. Further examinations suggested" or "Serious anomalies on gait detected. Subject may require assistances". On the same window, it is asked to the user if he wants to save the result of test, in positive case clicking on "Yes". 

Now it is possible to start a new acquisition pushing again the button "Start Acquisition". 

At the end of the test, it is possible to save the entire session of acquisitions pushing the button "Save Data". These data are saved in files contained in the tab "Excel files". 

In order to start a new session of acquisitions, the user has to push the button "New session" and repeat all the previous steps. 

### Bugs
During the pairing between device and application may happen that the device fails to access the serial port. In this case, a dynamic window will open showing the wrong serial port and the message "ERROR PORT CONNECTION: ". It is recommended to reset the application.
