import tkinter
import time
import serial
import numpy as np
from timeit import default_timer as timer
import matplotlib.pyplot as plt
import tkinter as Tk
import numpy as np
import matplotlib.animation as animation
from pyqtgraph.Qt import QtCore, QtGui
import pyqtgraph.opengl as gl
import pyqtgraph as pg
from PyQt5 import QtTest
import sys
import multiprocessing



# UART Com Settings
UART_PORT = 'COM6'
UART_BAUDRATE = 230400
UART_INPUT_SIZE = 243
UART_OUTPUT_SIZE = 4

WINDOW = 450

# FPGA Command values
CMD_START_NEURON = 1
CMD_RESET_NEURON = 2
CMD_SET_SPIKE = 3
CMD_SET_TEST_SPIKE = 4
CMD_CLEAR_BUFFERED_SPIKE = 5

class uart_com:
    """ A class that encapsulates the UART connection between a PC and FPGA via a USB UART."""

    def __init__(self, port=None, baudrate=None, timeout=0.1):
        # Set internal variables
        if port is None:
            self.port = 'COM6'
        else:
            self.port = port
        if baudrate is None:
            self.baudrate = 230400
        else:
            self.baudrate = baudrate
            
        self.serial = serial.Serial()
        self.serial.baudrate = self.baudrate
        self.serial.port = self.port
        self.serial.timeout = timeout
        # Open the serial connection
        self.serial.open()
        # Clear any excess data sitting in the buffers
        self.serial.reset_input_buffer()
        self.serial.reset_output_buffer()

    def __del__(self):
        # Release the serial connection
        self.serial.close()

    def read_blocking(self):
        """ A blocking read. stop until receive four 0xff or timeout"""
        stop_frame_count = 0
        receive = bytearray()
#        receive.append(1)
        while(1):
            data_read = self.serial.read(1)
            #if read() returns empty array, break
            if len(data_read) == 0:
                print('timeout')
                break
#            print(data_read)
            if data_read[0] != 255:
                receive.append(data_read[0])
            else:
                stop_frame_count += 1
            if stop_frame_count == 4:
                break
        return receive

    def write_blocking(self, write_data):
        """ A blocking write. The expected number of bytes written is set during initialization. """
        self.serial.write(write_data)

    def dataInReadBuffer(self):
        return True if self.serial.in_waiting > 0 else False


class neuron_controller():
    
    def __init__(self, window, port=None, baudrate=None, timeout=0.1):
        
        self.uart = uart_com(port=port, baudrate=baudrate, timeout=timeout)
        
        self.window = window
        
        self.decoding = 'ascii'
  
    def send_word(self, binary_string):
        byte_array = self.bin_str_to_bytes(binary_string)
        self.uart.write_blocking(byte_array)
    
    def read_data(self):
        data = self.uart.read_blocking()
        return data
        
    def bin_str_to_bytes(self, bin_str):
        '''
        seperate every 8 bits by whitespace
        msb                             lsb
        31                                0
        00000000 00000000 00000000 00000000
        store msb in bytearray[3], lsb in bytearray[0]
        '''
        bin_str = bin_str.split(' ')
        byte_array = bytearray()
        for field in reversed(bin_str):
            int_val = int(field, 2)
            byte_array.append(int_val)
        return byte_array

    def check_for_output(self):
        return self.connection.dataInReadBuffer()
    
    # Commands to read from the FPGA
    def read_cycle(self):
        '''
        convert raw output from fpga to numpy 
        '''       
        psp = np.zeros(110)
        voltage = np.zeros(10)
        spikes = np.zeros(10)
        
        data = self.read_data()
         
        if self.decoding == 'ascii':
            decoded = data.decode('ascii')
            split = decoded.split('\n')
            psp_str = split[0].split(',')
            voltage_str = split[1].split(',')
            
            #data in fpga is is represented by fixed(16,4) format, so divided by 2^12
            for i in range(110):
                psp[i] = int(psp_str[i]) / 4096
            
            for i in range(10):
                voltage[i] = int(voltage_str[i]) / 4096
                spikes[i] = int(voltage[i] > 1)
         
        else:
            #data is a list, every 5 bytes belong to a packet
            #split data into chunks of 5
            split_data = [data[i:i + 5] for i in range(0, len(data), 5)]
            #0-110 are psp
            psp_bytes = split_data[0:110]
            #110 to 120 are voltage
            voltage_bytes = split_data[110:]
            #convert raw bytes to integers
            for i,val_byte in enumerate(psp_bytes):
                #microblaze sends lsb fisrt, so lsb stores in [1], msb in [3]
                #byte order is little endian
                u16 = int.from_bytes(val_byte[1:], byteorder = 'little')
                int16 = self.u16toint(u16)
                psp[i] = int16
            
            voltage_bytes = split_data[110:]
            for i,val_byte in enumerate(psp_bytes):
                u16 = int.from_bytes(val_byte[1:], byteorder = 'little')
                int16 = self.u16toint(u16)
                psp_bytes[i] = int16
        return spikes, psp, voltage


    # Commands to write to the FPGA
    def start_cycle(self):
        cmd_start = bytearray([0,0,0,CMD_START_NEURON])
        self.uart.write_blocking(cmd_start)
    
    def run_one_step(self):
        '''
        run neuron for one time step, including send start command, and read results
        '''
        self.start_cycle();
        data = self.read_cycle()
        return data

    def reset_neuron(self):
        '''
        reset psp
        '''
        cmd_reset = bytearray([0,0,0,CMD_RESET_NEURON])
        self.uart.write_blocking(cmd_reset)

    def set_spikes(self, spike_array: np.array):
        '''
        spike_array: 1d numpy array, 1 for spike, 0 for nothing, each position
            is a synapse input
        '''
        #find non zero positions
        input_spike_index = np.where(spike_array!=0)[0]
        for idx in input_spike_index:
            spike_packet = bytearray([0,0,idx,CMD_SET_SPIKE])
            self.uart.write_blocking(spike_packet)

    def set_test_spikes(self):
        cmd_test_spikes = bytearray([0,0,0,CMD_SET_TEST_SPIKE])
        self.uart.write_blocking(cmd_test_spikes)

    def clear_spikes(self):
        '''
        set spike buffer in microblaze to 0
        '''
        cmd_clear_spikes = bytearray([0,0,0,CMD_CLEAR_BUFFERED_SPIKE])
        self.uart.write_blocking(cmd_clear_spikes)
    
    def chunks(self, l, n):
        """Yield successive n-sized chunks from l.
        https://stackoverflow.com/questions/312443/how-do-you-split-a-list-into-evenly-sized-chunks
        """
        for i in range(0, len(l), n):
            yield l[i:i + n]
    
    def u16toint(self, u16):
        '''
        assume the u16 is unsigned integer, convert it to int
        '''
        #value in fpga is represented by fixpoint(16,4), while in microblaze,
        #it is converted to u32. so only keep lower 16 bits
        u16 = u16 & 0xFFFF
        
        #convert unsigned to signed
        if u16 > 32767:
            return u16-65536
        else:
            return u16
    
    def disconnect(self):
        self.uart.serial.close()
    
    def run_one_step_fake(self):
        return np.random.rand(10), np.random.rand(110), np.random.rand(10)
        
if __name__ == '__main__':
    spike = np.load('D:/islped_demo/snn/noise_train.npy')
    
    test_spike = spike[0]
    controller = neuron_controller(WINDOW, port='COM5', baudrate=230400, timeout=0.1)
    
    #manager = multiprocessing.Manager()
    #shared_list = manager.list()
    #n = 0
    #process1 = multiprocessing.Process(
    #    target=write_only, args=[shared_list,n])
    #process2 = multiprocessing.Process(
    #    target=read_only, args=[shared_list])
    #process1.start()
    #process2.start()
    #process1.join()
    #process2.join()
    
    #record voltage[instance_idx, neuron_id, time_step]
    v_record = np.zeros([100,10,WINDOW])
    controller.reset_neuron()
    
    test_pyqtgraph = False
    use_fake_data = True
    
    if test_pyqtgraph:
        start = timer()
        app = QtGui.QApplication(sys.argv)
        w = gl.GLViewWidget()
        w.setBackgroundColor('w')
        w.opts['azimuth'] = 90
        w.opts['elevation'] = 0
        w.setGeometry(0, 110, 1920, 1080)
        w.show()
        
        traces = dict()  
        
        for i in range(10):
            x = np.array(range(450))
            y = np.zeros(450)
            z = np.zeros(450)
            pts = np.vstack([x, y, z]).transpose()
            traces[i] = gl.GLLinePlotItem(
                pos=pts,
                color=pg.glColor((i, 10 * 1.3)),
                width=(i + 1) / 10,
                antialias=True,
            )
            #if use white background
            #reference: https://github.com/pyqtgraph/pyqtgraph/issues/193
            traces[i].setGLOptions('translucent')
            w.addItem(traces[i])
        
        for j in range(450):
            for i in range(10):
                if use_fake_data:
                    s,p,v = controller.run_one_step_fake()
                    v_record[i,:,j] = v
                    z = v_record[0,i,0:j] + i*5
                else:   
                    controller.set_spikes(spike[i,j,:])
                    s,p,v = controller.run_one_step()
                    v_record[i,:,j] = v
                    # z coordinates represent voltage
                    # + 5 to plac each trace at different vertical position
                    z = v_record[0,i,0:j] + i*5
                    #reset psp at last step
                    if (j == 450-1):
                        controller.reset_neuron()
                
                x = np.array(range(0,j))
                y = np.zeros(j)
    
                z = np.random.rand(j) + i * 5
                pts = np.vstack([x, y, z]).transpose()
                
                traces[i].setData(pos=pts, color=pg.glColor((i, 10 * 1.3)), width=3)
            print(j)
        #    QtTest.QTest.qWait(1000)
            app.processEvents()
            
        end = timer()
        print(end - start) # Time in seconds, e.g. 5.38091952400282
    ###############################################################################
    else:
        fig, ax = plt.subplots()
        for i in range(10):
            line = ax.plot(np.random.randn(450))
        plt.show(block=False)
        fig.canvas.draw()
    
        plt.ioff()
        #run for multiple samples
        start = timer()
        for i in range(1):
            #for every time step
            for j in range(WINDOW):
                controller.set_spikes(spike[i,j,:])
                s,p,v = controller.run_one_step()
                v_record[i,:,j] = v
                #reset psp at last step
                if (j == 450-1):
                    controller.reset_neuron()
    #            if j % 5 == 0:
                ax.draw_artist(ax.patch)
                for n, l in enumerate(ax.lines):
                    l.set_ydata( v_record[0,n,:])
    #                
                    ax.draw_artist(l)
                
                fig.canvas.update()
                fig.canvas.flush_events()
                
        #plt.show()
        # ...
        end = timer()
        print(end - start) # Time in seconds, e.g. 5.38091952400282
    


