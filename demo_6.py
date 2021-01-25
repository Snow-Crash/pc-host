# -*- coding: utf-8 -*-
"""
Created on Wed Jun 19 21:45:50 2019

@author: hw, kp, dpr

reference
https://stackoverflow.com/questions/45046239/python-realtime-plot-using-pyqtgraph
http://www.pyqtgraph.org/documentation/qtcrashcourse.html
http://www.pyqtgraph.org/downloads/0.10.0/pyqtgraph-0.10.0-deb/pyqtgraph-0.10.0/examples/ScatterPlot.py

"""
# Import libraries
import numpy as np
from pyqtgraph.Qt import QtGui, QtCore, QtWidgets
import pyqtgraph as pg
import PyQt5.QtWidgets
from pyqtgraph.widgets.RemoteGraphicsView import RemoteGraphicsView
from main_program import *
from timeit import default_timer as timer
from queue import Queue
import threading
import time
from collections import OrderedDict


ploting_queue = Queue()
info_queue = Queue()

# Constants
# Experiment Constants
WINDOW = 450
SYNAPSES = 110
NEURONS = 10
PATTERNS = 10
SLIDING_WINDOW = 100
DATA_PLOT_RANGE = WINDOW

USE_SLIDING_WINDOW = True

if USE_SLIDING_WINDOW:
    DATA_PLOT_RANGE = SLIDING_WINDOW


PREPROCESSED_SPIKE_LOCATION = 'D:/islped_demo/snn/noise_train.npy'
RAW_DATA_LOCATION = 'D:/islped_demo/snn/interpolated_raw_data.npy'
LABEL_LOCATION = 'D:/islped_demo/snn/noise_train_id.npy'


# UART Com Settings
UART_PORT = 'COM5'
UART_BAUDRATE = 230400
UART_INPUT_SIZE = 243
UART_OUTPUT_SIZE = 4
UART_TIMEOUT = 0.1

# GUI Constants
DATA_SELECT_SYNAPSES = 22
DATA_SELECT_NEURONS = 10

selected_synapses_idx = np.arange(0, 110, 5)

# GUI
def dropdown_options_dict():
    d = OrderedDict()
    val = 0
    while val < PATTERNS:
        d.update({val.__str__(): val})
        val += 1
    return d
pg.setConfigOptions(antialias=True)
#pg.setConfigOptions(useOpenGL=True)
pg.setConfigOption('background', 'w')
pg.setConfigOption('foreground', (0, 0, 0))

# set stylesheet
#file = QtCore.QFile("./qss/light.qss")
#file.open(QtCore.QFile.ReadOnly | QtCore.QFile.Text)
#stream = QtCore.QTextStream(file)

font = QtGui.QFont('Microsoft YaHei', 10)
tick_font = QtGui.QFont('Microsoft YaHei', 8)

## Always start by initializing Qt (only once per application)
app = QtGui.QApplication([])
#app.setStyleSheet(stream.readAll())


## Define a top-level widget to hold everything
w = QtGui.QWidget()

colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728',
              '#9467bd', '#8c564b', '#e377c2', '#7f7f7f',
              '#bcbd22', '#17becf']


control_panel_max_width = 300
btn_background = QtGui.QPixmap('./images/start.png')
## Create some widgets to be placed inside
btn = QtGui.QPushButton('Run')
btn.setFont(font)
btn.setIcon(QtGui.QIcon(btn_background))
#btn.setIconSize(btn_background.rect().size());
btn.setIconSize(QtCore.QSize(64, 64))
btn.setMaximumWidth(control_panel_max_width)

# text = QtGui.QLineEdit('enter text')
listw = QtGui.QListWidget()
listw.setMaximumWidth(control_panel_max_width)
auto_check_box = QtGui.QCheckBox("Auto demo")
auto_check_box.setFont(font)
auto_check_box.setMaximumWidth(control_panel_max_width)
input_class_label = QtGui.QLabel()
input_class_label.setFont(font)
input_class_label.setMaximumWidth(control_panel_max_width)
dropdown_patterns = pg.ComboBox(items=dropdown_options_dict())
dropdown_patterns.setFont(font)
dropdown_patterns.setMaximumWidth(control_panel_max_width)
#control panel is a container, place widgets in it
control_panel = QtGui.QVBoxLayout()
control_panel.addWidget(btn)
control_panel.addWidget(auto_check_box)
control_panel.addWidget(dropdown_patterns)
# control_panel.addWidget(text)
control_panel.addWidget(listw)
control_panel.addWidget(input_class_label)

#This is a container
raw_data_plot = pg.PlotWidget()
#list stores references to all 
raw_data_lines = []
#insert lines to container
for i in range(DATA_SELECT_SYNAPSES):
    line = raw_data_plot.plot(np.random.rand(DATA_PLOT_RANGE), pen=colors[i%len(colors)])
    raw_data_lines.append(line)
raw_data_plot.plotItem.setTitle('Input stimulus')
raw_data_plot.plotItem.titleLabel.item.setFont(font)
raw_data_plot.getAxis("left").tickFont = tick_font
raw_data_plot.getAxis("bottom").tickFont = tick_font

psp_plot = pg.PlotWidget()
psp_plot.plotItem.setTitle('PSP')
psp_plot.plotItem.titleLabel.item.setFont(font)
psp_plot.getAxis("left").tickFont = tick_font
psp_plot.getAxis("bottom").tickFont = tick_font

psp_lines = []
for i in range(DATA_SELECT_SYNAPSES):
    line = psp_plot.plot(np.random.rand(WINDOW), pen=colors[i%len(colors)])
    psp_lines.append(line)

voltage_plot = pg.PlotWidget()
voltage_plot.plotItem.titleLabel.item.setFont(font)
voltage_plot.getAxis("left").tickFont = tick_font
voltage_plot.getAxis("bottom").tickFont = tick_font
voltage_plot.plotItem.setYRange(-5,1.5)

voltage_lines = []
for i in range(DATA_SELECT_NEURONS):
    line = voltage_plot.plot(np.random.rand(DATA_PLOT_RANGE), pen=colors[i%len(colors)])
    voltage_lines.append(line)
voltage_plot.plotItem.setTitle('Membrane Potential')

inspike_plot = pg.PlotWidget()
inspike_plot.plotItem.titleLabel.item.setFont(font)
inspike_plot.getAxis("left").tickFont = tick_font
inspike_plot.getAxis("bottom").tickFont = tick_font

in_scatter = pg.ScatterPlotItem(size=10, pen=pg.mkPen(None), brush=pg.mkBrush(0, 0, 0, 120))
#in_scatter.addPoints([-5], [-5])
inspike_plot.addItem(in_scatter)
inspike_plot.plotItem.setTitle('Input Spike Train')
inspike_plot.setXRange(0, WINDOW, padding=0)
inspike_plot.setYRange(-0.5, DATA_SELECT_SYNAPSES + 0.5, padding=0)

outspike_plot = pg.PlotWidget()
outspike_plot.plotItem.titleLabel.item.setFont(font)
outspike_plot.getAxis("left").tickFont = tick_font
outspike_plot.getAxis("bottom").tickFont = tick_font

out_scatter = pg.ScatterPlotItem(size=10, pen=pg.mkPen(None), brush=pg.mkBrush(0, 0, 0, 120))
#out_scatter.addPoints([-5], [-5])
outspike_plot.addItem(out_scatter)
outspike_plot.plotItem.setTitle('Output Spike Train')
outspike_plot.setXRange(0, WINDOW, padding=0)
outspike_plot.setYRange(-0.5, NEURONS + 0.5, padding=0)

## Create a grid layout to manage the widgets size and position
layout = QtGui.QGridLayout()
w.setLayout(layout)

#######################################################################
drop_down_instruction = QtWidgets.QLabel()
# drop_down_instruction.setStyleSheet("QLabel {\n"
# "font-family: \"Arial\";\n"
# "font-size: 30px;\n"
# "color : rgb(219,61,1);\n"
# "}")
drop_down_instruction.setText("Select input pattern:")
drop_down_instruction.setAlignment(QtCore.Qt.AlignLeft)
drop_down_instruction.setFont(font)
control_panel.insertWidget(2,drop_down_instruction)

_translate = QtCore.QCoreApplication.translate

# result_container = QtWidgets.QWidget()
# result_container.setStyleSheet("background-color: rgb(250, 250, 250);")
# result_container.setObjectName("result_container")
# gridLayout_6 = QtWidgets.QGridLayout(result_container)
# gridLayout_6.setContentsMargins(0, 0, 0, 0)
# gridLayout_6.setSpacing(0)
# gridLayout_6.setObjectName("gridLayout_6")
# input_class_value = QtWidgets.QLabel(result_container)
# input_class_value.setStyleSheet("QLabel {\n"
# "font-family: \"Arial\";\n"
# "font-size: 30px;\n"
# "color : rgb(219,61,1);\n"
# "}")
# input_class_value.setText("")
# input_class_value.setAlignment(QtCore.Qt.AlignCenter)
# input_class_value.setObjectName("input_class_value")
# gridLayout_6.addWidget(input_class_value, 1, 0, 1, 1)
# output_class_value = QtWidgets.QLabel(result_container)
# output_class_value.setStyleSheet("QLabel {\n"
# "font-family: \"Arial\";\n"
# "font-size: 30px;\n"
# "color : rgb(219,61,1);\n"
# "}")
# output_class_value.setText("")
# output_class_value.setAlignment(QtCore.Qt.AlignCenter)
# output_class_value.setObjectName("output_class_value")
# gridLayout_6.addWidget(output_class_value, 1, 1, 1, 1)
# input_class_text = QtWidgets.QLabel(result_container)
# input_class_text.setObjectName("input_class_text")
# gridLayout_6.addWidget(input_class_text, 2, 0, 1, 1)
# output_class_text = QtWidgets.QLabel(result_container)
# output_class_text.setObjectName("output_class_text")
# gridLayout_6.addWidget(output_class_text, 2, 1, 1, 1)
# spike_count_value = QtWidgets.QLabel(result_container)
# spike_count_value.setStyleSheet("QLabel {\n"
# "font-family: \"Arial\";\n"
# "font-size: 30px;\n"
# "color : rgb(219,61,1);\n"
# "}")
# spike_count_value.setText("")
# spike_count_value.setAlignment(QtCore.Qt.AlignCenter)
# spike_count_value.setObjectName("spike_count_value")
# gridLayout_6.addWidget(spike_count_value, 1, 2, 1, 1)
# spike_count_text = QtWidgets.QLabel(result_container)
# spike_count_text.setObjectName("spike_count_text")
# gridLayout_6.addWidget(spike_count_text, 2, 2, 1, 1)
# result_title = QtWidgets.QLabel(result_container)
# result_title.setMinimumSize(QtCore.QSize(0, 30))
# result_title.setMaximumSize(QtCore.QSize(16777215, 30))
# result_title.setObjectName("result_title")
# gridLayout_6.addWidget(result_title, 0, 0, 1, 3)

# input_class_value.setText("-")
# output_class_value.setText("-")
# spike_count_value.setText("-")


# input_class_text.setText(_translate("MainWindow", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
# "<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
# "p, li { white-space: pre-wrap; }\n"
# "</style></head><body style=\" font-family:\'SimSun\'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
# "<p align=\"center\" style=\" margin-top:5px; margin-bottom:5px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'Arial\'; font-size:10pt; color:#6f777d;\">Input</span></p>\n"
# "<p align=\"center\" style=\" margin-top:5px; margin-bottom:5px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'Arial\'; font-size:10pt; color:#6f777d;\">Class</span></p></body></html>"))
# output_class_text.setText(_translate("MainWindow", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
# "<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
# "p, li { white-space: pre-wrap; }\n"
# "</style></head><body style=\" font-family:\'SimSun\'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
# "<p align=\"center\" style=\" margin-top:5px; margin-bottom:5px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'Arial\'; font-size:10pt; color:#6f777d;\">Output</span></p>\n"
# "<p align=\"center\" style=\" margin-top:5px; margin-bottom:5px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'Arial\'; font-size:10pt; color:#6f777d;\">Class</span></p></body></html>"))
# spike_count_text.setText(_translate("MainWindow", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
# "<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
# "p, li { white-space: pre-wrap; }\n"
# "</style></head><body style=\" font-family:\'SimSun\'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
# "<p align=\"center\" style=\" margin-top:5px; margin-bottom:5px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'Arial\'; font-size:10pt; color:#6f777d;\">Spike</span></p>\n"
# "<p align=\"center\" style=\" margin-top:5px; margin-bottom:5px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'Arial\'; font-size:10pt; color:#6f777d;\">Count</span></p></body></html>"))
# result_title.setText(_translate("MainWindow", "<html><head/><body><p align=\"center\"><span style=\" font-family:\'Arial\'; font-size:10pt; \">Result</span></p></body></html>"))
# layout.addWidget(result_container, 5, 3, 2, 2)  #

logo = QtWidgets.QLabel()
logo.setMinimumSize(QtCore.QSize(128, 128))
logo.setMaximumSize(QtCore.QSize(300, 300))
logo.setStyleSheet("background-color: rgb(212, 69, 1);")
logo.setText("")
logo.setObjectName("logo")
su_logo_background = QtGui.QPixmap('./images/su_logo_white.png')
logo.setPixmap(su_logo_background.scaled(QtCore.QSize(150, 150)))
logo.setAlignment(QtCore.Qt.AlignCenter)
control_panel.insertWidget(0,logo)


banner = QtWidgets.QWidget()
banner.setMinimumSize(QtCore.QSize(0, 100))
banner.setMaximumSize(QtCore.QSize(16777215, 100))
banner.setObjectName("banner")
gridLayout_10 = QtWidgets.QGridLayout(banner)
gridLayout_10.setContentsMargins(100, 0, 0, 0)
gridLayout_10.setSpacing(0)
gridLayout_10.setObjectName("gridLayout_10")
banner_logo = QtWidgets.QLabel(banner)
banner_logo.setMaximumSize(QtCore.QSize(300, 16777215))
banner_logo.setText("")
banner_logo.setObjectName("banner_logo")
banner_logo_img = QtGui.QPixmap('./images/eng_logo_2.png')
banner_logo.setPixmap(banner_logo_img.scaled(QtCore.QSize(250, 300),
                                                    QtCore.Qt.KeepAspectRatio))
gridLayout_10.addWidget(banner_logo, 0, 1, 1, 1)
title_label = QtWidgets.QLabel(banner)
title_label.setMinimumSize(QtCore.QSize(0, 50))
title_label.setText(_translate("MainWindow", "<html><head/><body><p><span style=\" font-size:x-large; font-weight:600; color:#6f777d;\">Neuromorphic System for Temporal Data Classification</span></p></body></html>"))
font = QtGui.QFont()
font.setFamily("Arial")
title_label.setFont(font)
title_label.setObjectName("title_label")
gridLayout_10.addWidget(title_label, 0, 2, 1, 3)
layout.addWidget(banner, 0,1,1,4)
#######################################################################

#add control panel and figures to it
layout.addLayout(control_panel, 0, 0, 6, 1)
layout.addWidget(raw_data_plot, 1, 1, 2, 2)  #
layout.addWidget(inspike_plot, 1, 3, 2, 2)  #
layout.addWidget(psp_plot, 3, 1, 2, 2)  #
layout.addWidget(voltage_plot, 3, 3, 2, 2)  #
layout.addWidget(outspike_plot, 5, 1, 2, 2)  #
layout.setSpacing(30)
layout.setMargin(30)

def classid2sampleidx(drop_down_value):
    #find all samples of this class
    selected_class = unique_label[drop_down_value]
    candidate_sample_idx = np.where(labels == selected_class)[0]
    # print(candidate_sample_idx)
    #randomly pick one
    selected_sample_idx = np.random.choice(candidate_sample_idx)
    # print(selected_sample_idx)
    return selected_sample_idx


def send_recieve_packages():
    
    start = timer()
    current_pattern = dropdown_patterns.value()
    while True:
        selected_sample_idx = classid2sampleidx(current_pattern)
        print('send current', current_pattern, 'select', selected_sample_idx)

        info_queue.put((current_pattern, selected_sample_idx))

        input_class_label.setText("Current Running Pattern :" + current_pattern.__str__()+ "\n Step :" )
        # print("Current Pattern: {}".format(current_pattern))
        listw.clear()
        listw.insertItem(0, "Start Pattern: " + current_pattern.__str__())
        for t in range(WINDOW):   
            controller.set_spikes(spike[selected_sample_idx, t, :])
#            controller.set_spikes(spike[current_pattern, t, :])
            s, p, v = controller.run_one_step()
            merge_data = [s, p, v, t]
            ploting_queue.put(merge_data)
            input_class_label.setText("Current Running Pattern :" + current_pattern.__str__() + "\nStep :" + t.__str__())
            for n in range(s.__len__()):
                if s[n] > 0:
                    listw.insertItem(0, "Spike Detected! Neuron: {}, Step: {} ".format(n, t))
            # Reset psp at last step
            if (t == WINDOW-1):
                controller.reset_neuron()
                
        listw.insertItem(0, "End Pattern: " + current_pattern.__str__())
        if not auto_check_box.checkState():
            break
        # Wait to allow for observation of complete run
        time.sleep(3.0)
        current_pattern = np.random.randint(0, high=PATTERNS)
        selected_sample_idx = classid2sampleidx(current_pattern)

        
    print(timer() - start)


def btn_clicked_function():
    send_receive = threading.Thread(target=send_recieve_packages)
    send_receive.daemon = False
    send_receive.start()


def update():
    
    voltage = np.zeros([NEURONS, DATA_PLOT_RANGE])
    psp = np.zeros([SYNAPSES, WINDOW])
    out_spikes = np.zeros([NEURONS, WINDOW])
    raw_data = np.zeros([22, DATA_PLOT_RANGE])
    last_t = 0
    current_t = 0
    ptr = -SLIDING_WINDOW
    while True:
        while not info_queue.empty():
            current_pattern, selected_sample_idx = info_queue.get()
            print('update current', current_pattern)
            print('update selected', selected_sample_idx)
        
        while not ploting_queue.empty():
            merge_data = ploting_queue.get()
            s, p, v, t = merge_data
            v_record[0, :, t] = v
            ptr += 1
            if USE_SLIDING_WINDOW:
                voltage[:,0:-1] = voltage[:,1:]
#                psp[:,0:-1] = psp[:,1:]
                raw_data[:, 0:-1] = raw_data[:,1:]
                
                voltage[:, -1] = v
#                psp[:, -1] = p
                raw_data[:, -1] = raw_input[selected_sample_idx, :, t]
            else:
                voltage[:, t] = v
#                psp[:, t] = p
                raw_data[:, :t] = raw_input[selected_sample_idx, :, :t]
            
            psp[:, t] = p
            out_spikes[:, t] = s
            current_t = t
            if t < last_t:
                in_scatter.setData([-5], [-5])
                out_scatter.setData([-5], [-5])
                in_scatter.clear()
                out_scatter.clear()

            
            #reset all data at the begining of each run
            if t == 0:
                out_spikes = np.zeros([NEURONS, WINDOW])
                voltage = np.zeros([NEURONS, DATA_PLOT_RANGE])
                psp = np.zeros([SYNAPSES, WINDOW])
                raw_data = np.zeros([22, DATA_PLOT_RANGE])
                ptr = -SLIDING_WINDOW

            #     try:
            #         input_class_value.setText(str(current_pattern))
            #         output_class_value.setText("-")
            #     except Exception:
            #         pass
            
            # spike_count = spike[selected_sample_idx, :current_t, :].sum()

            # try:
            #     spike_count_value.setText('{:4d}'.format(spike_count))
            # except Exception:
            #     pass
                


        # Synapse Plotting
        x = []
        y = []
        sc = 0
        for i, syn_idx in enumerate(selected_synapses_idx):
            # use setdata instead of plot. setdata is faster
            # raw_data_lines[i].setData(np.random.random(WINDOW) + i)
            raw_data_lines[i].setData(raw_data[i])
            psp_lines[i].setData(psp[::5][i] + i)
        
            if USE_SLIDING_WINDOW:
#                psp_lines[i].setPos(ptr, 0)
                raw_data_lines[i].setPos(ptr, 0)

            # Plotting Input Spikes
            if current_t > last_t:
                for step in range(last_t, current_t):
                    if spike[selected_sample_idx, step, syn_idx] > 0:
                        x.append(step)
                        y.append(i)
                        sc += 1
        if sc > 0:
            in_scatter.addPoints(x=x, y=y)

        # Neuron Plotting
        x = []
        y = []
        sc = 0
        
        for i in range(DATA_SELECT_NEURONS):
            
            if USE_SLIDING_WINDOW:
                voltage_lines[i].setPos(ptr, 0)
                
            voltage_lines[i].setData(voltage[i, :])
            
            # Plotting Output Spikes
            if current_t > last_t:
                for step in range(last_t, current_t):
                    if out_spikes[i][step] > 0:
                        x.append(step)
                        y.append(i)
                        sc += 1
        if sc > 0:
            out_scatter.addPoints(x=x, y=y)

        last_t = current_t
        QtGui.QApplication.processEvents()    # you MUST process the plot now, otherwise no update
        time.sleep(0.2)


btn.clicked.connect(btn_clicked_function)

spike = np.load(PREPROCESSED_SPIKE_LOCATION)/1000
spike = spike.astype(int)
raw_input = np.load(RAW_DATA_LOCATION)
labels = np.load(LABEL_LOCATION)
unique_label = np.unique(labels)


test_spike = spike[0]
controller = neuron_controller(WINDOW, port=UART_PORT, baudrate=UART_BAUDRATE, timeout=UART_TIMEOUT)

v_record = np.zeros([100,10,WINDOW])
controller.reset_neuron()


## Display the widget as a new window
w.show() # showFullScreen()
display_data = threading.Thread(target=update)
display_data.daemon = True    
display_data.start()

## Start the Qt event loop
app.exec_()
display_data.join()
