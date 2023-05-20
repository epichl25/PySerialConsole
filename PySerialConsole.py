import sys
import time
import serial
import logging
import datetime
from pathlib import Path
from threading import Thread
from PyQt6.QtWidgets import QApplication
from pglive.sources.data_connector import DataConnector
from pglive.sources.live_plot import LiveLinePlot
from pglive.sources.live_plot_widget import LivePlotWidget

def SerialConfig():
    global ser
    port=input("Port: ")
    baudrate=input("Baudrate: ")
    ser=serial.Serial(
        port,
        baudrate,
        parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE,
        bytesize=serial.EIGHTBITS,
        timeout=1
    )   

def CMD():
    print("r: Read from serial, p: Plot graph. '+s' to save serial data")
    mode=input("Select mode:")
    global SelectMode
    while SelectMode == 0:
        if mode[0].lower() == 'r':
            if len(mode)==3 and mode[2].lower()== 's':
                SelectMode=3
            else:
                SelectMode=1
        elif mode[0].lower() == 'p':
            if len(mode)==3 and mode[2].lower()== 's':
                SelectMode=4
            else:
                SelectMode=2
        else:
            print("Error! Invalid input")
            print ("Select mode: ")

def Logger():
    global logger_start
    CurrentDateTime = datetime.datetime.now()

    log_file = './logs/%s.log' % CurrentDateTime.strftime("%d.%m.%Y_%H-%M-%S")
    logging.basicConfig(format='[%(asctime)s] %(levelname)-8s %(message)s',
                                        datefmt='%Y/%m/%d %I:%M:%S %p',
                                        filename=log_file, filemode='a',level=logging.INFO)
    console = logging.StreamHandler()
    console.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
    console.setFormatter(formatter)
    logging.getLogger().addHandler(console)
    logger_start = True

def Plotter():
    app = QApplication(sys.argv)
    global running
    running = True
    plot_widget = LivePlotWidget(title="PySerialConsole")
    plot_widget.resize(1200, 600)
    plot_curve = LiveLinePlot()
    plot_widget.addItem(plot_curve)
    data_connector = DataConnector(plot_curve, max_points=1000, update_rate=100)
    plot_widget.show()
    while True: 
        Thread(target=Update, args=(data_connector,)).start()
    
def Update(connector):
    x=0
    while running:
        x+=1
        value = ser.readline()  
        if SelectMode==4:
            logging.info(value)
        if value.strip().decode( "ascii" )!='':
            VAL=value.strip().decode()
            try:
                val=float(VAL)
                if val<4096 or val>0:
                    connector.cb_append_data_point(val, x)
            except ValueError:
                None

if __name__ =="__main__":
    print("------------------------------PySerialConsole-------------------------------------")
    print("---------------------------Developed by epichl25----------------------------------")
    print("")
    time.sleep(1)
    logger_start = False
    SelectMode=0
    Path("./logs").mkdir(parents=True, exist_ok=True)
    CMD()
    SerialConfig()
    if SelectMode==1:
        while 1:
            Data=ser.readline()
            FormattedData=Data.decode("utf-8").rstrip('\r\n')
            print(FormattedData)
    elif SelectMode==2:
        Plotter()
    elif SelectMode==3:
        Logger()
        while 1:
            Data=ser.readline()
            print(Data)
            logging.info(Data)
    elif SelectMode==4:
        Logger()
        Plotter()
    else:
        print("Error! Invalid mode.")
        exit()