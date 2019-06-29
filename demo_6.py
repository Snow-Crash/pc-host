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
from pyqtgraph.Qt import QtGui, QtCore
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
file = QtCore.QFile("./qss/light.qss")
file.open(QtCore.QFile.ReadOnly | QtCore.QFile.Text)
stream = QtCore.QTextStream(file)

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

## Create some widgets to be placed inside
btn = QtGui.QPushButton('Run')
btn.setFont(font)
text = QtGui.QLineEdit('enter text')
listw = QtGui.QListWidget()
auto_check_box = QtGui.QCheckBox("Auto demo")
auto_check_box.setFont(font)
input_class_label = QtGui.QLabel()
input_class_label.setFont(font)
dropdown_patterns = pg.ComboBox(items=dropdown_options_dict())
dropdown_patterns.setFont(font)
#control panel is a container, place widgets in it
control_panel = QtGui.QVBoxLayout()
control_panel.addWidget(btn)
control_panel.addWidget(dropdown_patterns)
control_panel.addWidget(text)
control_panel.addWidget(listw)
control_panel.addWidget(auto_check_box)
control_panel.addWidget(input_class_label)

#This is a container
raw_data_plot = pg.PlotWidget()
#list stores references to all 
raw_data_lines = []
#insert lines to container
for i in range(DATA_SELECT_SYNAPSES):
    line = raw_data_plot.plot(np.random.rand(WINDOW), pen=colors[i%len(colors)])
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

voltage_lines = []
for i in range(DATA_SELECT_NEURONS):
    line = voltage_plot.plot(np.random.rand(WINDOW), pen=colors[i%len(colors)])
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

#add control panel and figures to it
layout.addLayout(control_panel, 0, 0, 5, 1)
layout.addWidget(raw_data_plot, 0, 1, 2, 2)  #
layout.addWidget(inspike_plot, 0, 3, 2, 2)  #
layout.addWidget(psp_plot, 2, 1, 2, 2)  #
layout.addWidget(voltage_plot, 2, 3, 2, 2)  #
layout.addWidget(outspike_plot, 4, 1, 2, 2)  #
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
    # voltage = np.zeros([10,WINDOW])
    # psp = np.zeros([110,WINDOW])
    
    start = timer()
#    global current_pattern # Allows for communication between Comm. Loop and Plotting Loop
#    global selected_sample_idx
    current_pattern = dropdown_patterns.value()
    while True:
        selected_sample_idx = classid2sampleidx(current_pattern)
        print('send current', current_pattern, 'select', selected_sample_idx)

        info_queue.put((current_pattern, selected_sample_idx))

        input_class_label.setText("Current Running Pattern :" + current_pattern.__str__()+ "\n Step :" )
        # print("Current Pattern: {}".format(current_pattern))
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
        listw.insertItem(0, "End Pattern: " + current_pattern.__str__())
        if not auto_check_box.checkState():
            break
        # Wait to allow for observation of complete run
        time.sleep(3.0)
        current_pattern = np.random.randint(0, high=PATTERNS)
        selected_sample_idx = classid2sampleidx(current_pattern)
#        print(selected_sample_idx)

        
    print(timer() - start)


def btn_clicked_function():
    send_receive = threading.Thread(target=send_recieve_packages)
    send_receive.daemon = False
    send_receive.start()


def update():
    
#    global current_pattern # Allows for communication between Comm. Loop and Plotting Loop
#    global selected_sample_idx

    
    voltage = np.zeros([NEURONS, WINDOW])
    psp = np.zeros([SYNAPSES, WINDOW])
    out_spikes = np.zeros([NEURONS, WINDOW])
    raw_data = np.zeros([22, WINDOW])
    last_t = 0
    current_t = 0
    while True:
        while not info_queue.empty():
            current_pattern, selected_sample_idx = info_queue.get()
            print('update current', current_pattern)
            print('update selected', selected_sample_idx)
        
        while not ploting_queue.empty():
            merge_data = ploting_queue.get()
            s, p, v, t = merge_data
            v_record[0, :, t] = v
            voltage[:, t] = v
            psp[:, t] = p
            out_spikes[:, t] = s
            current_t = t
            if t < last_t:
                last_t = 0
                in_scatter.setData([-5], [-5])
                out_scatter.setData([-5], [-5])
#                in_scatter.clear()
#                out_scatter.clear()
                
            # Reset psp at last step
            if (t == 450-1):
                controller.reset_neuron()
            
            #reset all data at the begining of each run
            if t == 0:
                pass
                voltage = np.zeros([NEURONS, WINDOW])
                psp = np.zeros([SYNAPSES, WINDOW])
                out_spikes = np.zeros([NEURONS, WINDOW])
                raw_data = np.zeros([22, WINDOW])
#                for i in range(DATA_SELECT_SYNAPSES):
#                    raw_data_lines[i].setData(spike[current_pattern, 0:current_t, i] + i * 1000)
#                    psp_lines[i].setData(psp[::5][i] + i)
        
            raw_data[:, :t] = raw_input[selected_sample_idx, :, :t]

        # Synapse Plotting
        x = []
        y = []
        sc = 0
        for i, syn_idx in enumerate(selected_synapses_idx):
#        for i in range(DATA_SELECT_SYNAPSES):
#        for i,idx in enumerate(selected_synapse):
            # use setdata instead of plot. setdata is faster
            # raw_data_lines[i].setData(np.random.random(WINDOW) + i)
#            raw_data_lines[i].setData(spike[current_pattern, 0:current_t, i] + i * 1000)
#            print("psp shape", psp.shape)
#            print("psp[::5] shape", psp[::5].shape)
            raw_data_lines[i].setData(raw_data[i])
            psp_lines[i].setData(psp[::5][i] + i)
#            print(i, idx)
            # Plotting Input Spikes
#        for i in range(SYNAPSES):
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
        time.sleep(0.3)


# Allows for communication between Comm. Loop and Plotting Loop
#current_pattern = 0
#selected_sample_idx = 0

btn.clicked.connect(btn_clicked_function)

spike = np.load(PREPROCESSED_SPIKE_LOCATION)
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
