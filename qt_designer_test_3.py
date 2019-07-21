
if __name__ == "__main__":
    import sys

    import pyqtgraph as pg
    from main_program import *
    from timeit import default_timer as timer
    from queue import Queue
    import threading
    import time
    from collections import OrderedDict

    from pyqt_ui_3 import *

    # pg.setConfigOptions(antialias=True)
    #pg.setConfigOptions(useOpenGL=True)
    pg.setConfigOption('background', 'w')
    pg.setConfigOption('foreground', (0, 0, 0))
    
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)

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
    pg.setConfigOption('background', 'w')
    pg.setConfigOption('foreground', (0, 0, 0))
    
    font = QtGui.QFont('Microsoft YaHei', 10)
    tick_font = QtGui.QFont('Microsoft YaHei', 8)

    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728',
                '#9467bd', '#8c564b', '#e377c2', '#7f7f7f',
                '#bcbd22', '#17becf']

    # banner_logo_img = QtGui.QPixmap('./images/eng_logo_2.png')
    # ui.banner_logo.setPixmap(banner_logo_img.scaled(QtCore.QSize(250, 300),
                                                        # QtCore.Qt.KeepAspectRatio))


    # su_logo_background = QtGui.QPixmap('./images/su_logo_white.png')
    # ui.logo.setPixmap(su_logo_background.scaled(QtCore.QSize(150, 150)))
    # ui.logo.setAlignment(QtCore.Qt.AlignCenter)


    # btn_background = QtGui.QPixmap('./images/start.png')
    ## Create some widgets to be placed inside
    ui.btn.setFont(font)
    # ui.btn.setIcon(QtGui.QIcon(btn_background))
    # ui.btn.setIconSize(QtCore.QSize(64, 64))
    ui.btn.setToolButtonStyle(QtCore.Qt.ToolButtonTextBesideIcon)

    ui.auto_check_box.setFont(font)
    ui.input_class_label.setFont(font)
    ui.dropdown_patterns.setFont(font)

    ui.dropdown_patterns.setItems(dropdown_options_dict())



    ui.input_class_value.setText("-")
    ui.output_class_value.setText("-")
    ui.spike_count_value.setText("-")

    #list stores references to all 
    raw_data_lines = []
    #insert lines to container
    for i in range(DATA_SELECT_SYNAPSES):
        line = ui.raw_data_plot.plot(np.random.rand(DATA_PLOT_RANGE), pen=colors[i%len(colors)])
        raw_data_lines.append(line)



    psp_lines = []
    for i in range(DATA_SELECT_SYNAPSES):
        line = ui.psp_plot.plot(np.random.rand(WINDOW), pen=colors[i%len(colors)])
        psp_lines.append(line)

    voltage_lines = []
    for i in range(DATA_SELECT_NEURONS):
        line = ui.voltage_plot.plot(np.random.rand(DATA_PLOT_RANGE), pen=colors[i%len(colors)])
        voltage_lines.append(line)
    # ui.voltage_plot.plotItem.setTitle('Membrane Potential')


    in_scatter = pg.ScatterPlotItem(size=10, pen=pg.mkPen(None), brush=pg.mkBrush(0, 0, 0, 120))
    #in_scatter.addPoints([-5], [-5])
    ui.inspike_plot.addItem(in_scatter)
    #ui.inspike_plot.plotItem.setTitle('Input Spike Train')
    ui.inspike_plot.setXRange(0, WINDOW, padding=0)
    ui.inspike_plot.setYRange(-0.5, DATA_SELECT_SYNAPSES + 0.5, padding=0)


    ui.outspike_plot.setXRange(0, WINDOW, padding=0)
    ui.inspike_plot.setYRange(0, 22, padding=0)

    out_scatter = pg.ScatterPlotItem(size=10, pen=pg.mkPen(None), brush=pg.mkBrush(0, 0, 0, 120))
    #out_scatter.addPoints([-5], [-5])
    ui.outspike_plot.addItem(out_scatter)
    #ui.outspike_plot.plotItem.setTitle('Output Spike Train')
    ui.outspike_plot.setXRange(0, WINDOW, padding=0)
    ui.outspike_plot.setYRange(-0.5, NEURONS + 0.5, padding=0)



    def classid2sampleidx(drop_down_value):
        #find all samples of this class
        selected_class = unique_label[drop_down_value]
        candidate_sample_idx = np.where(labels == selected_class)[0]
        # print(candidate_sample_idx)
        #randomly pick one
        selected_sample_idx = np.random.choice(candidate_sample_idx)
        # print(selected_sample_idx)
        return selected_sample_idx
    
    sample_count = 0
    ########################################################################
    def send_recieve_packages():
        
        
        global sample_count
        sample_count += 1
    
        if sample_count % 3 == 0:
            window.psp_plot.update()
            window.raw_data_plot.update()
            window.voltage_plot.update()
            for line in raw_data_lines:
                line.update()
            
            for line in psp_lines:
                line.update()
        
        start = timer()
        current_pattern = ui.dropdown_patterns.value()
        while True:
            selected_sample_idx = classid2sampleidx(current_pattern)
            print('send current', current_pattern, 'select', selected_sample_idx)

            info_queue.put((current_pattern, selected_sample_idx))

            ui.input_class_label.setText("Current Running Pattern :" + current_pattern.__str__()+ "\n Step :" )
            # print("Current Pattern: {}".format(current_pattern))
            ui.listw.clear()
            ui.listw.insertItem(0, "Start Pattern: " + current_pattern.__str__())
            for t in range(WINDOW):   
                controller.set_spikes(spike[selected_sample_idx, t, :])
    #            controller.set_spikes(spike[current_pattern, t, :])
                s, p, v = controller.run_one_step()
                merge_data = [s, p, v, t]
                ploting_queue.put(merge_data)
                ui.input_class_label.setText("Current Running Pattern :" + current_pattern.__str__() + "\nStep :" + t.__str__())
                for n in range(s.__len__()):
                    if s[n] > 0:
                        ui.listw.insertItem(0, "Spike Detected! Neuron: {}, Step: {} ".format(n, t))
                # Reset psp at last step
                if (t == 450-1):
                    controller.reset_neuron()
                    
            ui.listw.insertItem(0, "End Pattern: " + current_pattern.__str__())
            if not ui.auto_check_box.checkState():
                break
            # Wait to allow for observation of complete run
            time.sleep(3.0)
            current_pattern = np.random.randint(0, high=PATTERNS)
            selected_sample_idx = classid2sampleidx(current_pattern)

            
        print(timer() - start)

    ####################################################################

    def btn_clicked_function():
        send_receive = threading.Thread(target=send_recieve_packages)
        send_receive.daemon = False
        send_receive.start()

    ####################################################################

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
                    raw_data[:, 0:-1] = raw_data[:,1:]
                    voltage[:, -1] = v
                    raw_data[:, -1] = raw_input[selected_sample_idx, :, t]
                else:
                    voltage[:, t] = v
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
                    
                    try:
                        ui.input_class_value.setText(str(current_pattern))
                    except Exception:
                        pass

                spike_count = spike[selected_sample_idx, :current_t, :].sum()
                
                try:
                    ui.spike_count_value.setText('{:4d}'.format(spike_count))
                except Exception:
                    pass
                # ui.spike_count_value.setText('{:4d}'.format(spike_count))

            # Synapse Plotting
            x = []
            y = []
            sc = 0
            for i, syn_idx in enumerate(selected_synapses_idx):
                raw_data_lines[i].setData(raw_data[i])
                psp_lines[i].setData(psp[::5][i] + i)
            
                if USE_SLIDING_WINDOW:
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

    ui.btn.clicked.connect(btn_clicked_function)

    spike = np.load(PREPROCESSED_SPIKE_LOCATION)/1000
    spike = spike.astype(int)

    raw_input = np.load(RAW_DATA_LOCATION)
    labels = np.load(LABEL_LOCATION)
    unique_label = np.unique(labels)

    test_spike = spike[0]
    controller = neuron_controller(WINDOW, port=UART_PORT, baudrate=UART_BAUDRATE, timeout=UART_TIMEOUT)

    v_record = np.zeros([100,10,WINDOW])
    controller.reset_neuron()

    display_data = threading.Thread(target=update)

    display_data.daemon = True    
    display_data.start()

    MainWindow.show()
    sys.exit(app.exec_())

