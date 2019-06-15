import tkinter
import time
import serial
import numpy as np
from timeit import default_timer as timer



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
        data = self.read_data()
        decoded = data.decode('ascii')
        split = decoded.split('\n')
        spikes = None
        PSP = split[6]
        voltage = split[7]
        # TODO: determine structure of output
        # TODO: Convert bytes into fixed (private function)
        return spikes, PSP, voltage

    # Commands to write to the FPGA
    def start_cycle(self):
        cmd_start = bytearray([0,0,0,CMD_START_NEURON])
        self.uart.write_blocking(cmd_start)
    
    def run_one_step(self):
        self.start_cycle();
        data = self.read_cycle()
        return data

    def reset_neuron(self):
        cmd_reset = bytearray([0,0,0,CMD_RESET_NEURON])
        self.connection.writeb(cmd_reset)

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

    def set_test_spikes(self, spikeTrain: np.array):
        cmd_test_spikes = bytearray([0,0,0,CMD_SET_TEST_SPIKE])
        self.uart.write_blocking(cmd_test_spikes)

    def clear_spikes(self):
        cmd_clear_spikes = bytearray([0,0,0,CMD_CLEAR_BUFFERED_SPIKE])
        self.uart.write_blocking(cmd_clear_spikes)

    

#com = serial.Serial(port='COM5', baudrate=9600,bytesize=8, timeout=None)
#com = uart_com(port='COM5', baudrate=9600, timeout=1)

spike = np.load('D:/islped_demo/snn/noise_train.npy')

test_spike = spike[0]
controller = neuron_controller(450, port='COM5', baudrate=230400, timeout=0.1)

input_spike_index = np.where(test_spike[114]!=0)[0]
for idx in input_spike_index:
    spike_packet = bytearray([0,0,idx,CMD_SET_SPIKE])
    print(spike_packet)

start = timer()

for i in range(450):
    print(i)
    data = controller.run_one_step()

# ...
end = timer()
print(end - start) # Time in seconds, e.g. 5.38091952400282

#while(5):
#    controller.send_word('00000111 00000000 00000011 00001111')
#    data = controller.read_data()
#    print(data)
    
    
#    receive = com.read_blocking()
#    print(receive.decode("utf-8"))
#    inp = input('input command')
#    command = bin_str_to_bytes(inp)
#    com.write_blocking(command)
#    receive = com.read_blocking()
#    print(receive.decode("utf-8"))

'''
def test_read_data():
    # Start Timer
    st = time.time()
    # Read data from FPGA
    data_read = s.readb()
    # Update GUI with data from FPGA
    gui_data.config(text=data_read)
    # Complete timing analysis
    t = time.time() - st
    in_time_array.append(t) # Add
    in_time_array.pop(0)
    t_avg = sum(in_time_array)/time_average_range
    t_win = window_size * t_avg
    # Update GUI with timing analysis
    gui_intimer.config(text='In Time = {0:.9f} seconds. Estimated Time Per Window = {1:.9f} seconds.'.format(t_avg,t_win))
    # Schedule next write
    gui.after(DELAY, test_write_data)

def test_write_data():
    # Start Timer
    st = time.time()
    # Create next write data
    # Get current value of slider
    slider_status = var.get()
    write_data = bytearray(data_out_size)
    for i in range(data_out_size):
        offset = (slider_status + (i*1)) % 26
        write_data[i] = offset + 65
    # Write data
    s.writeb(write_data)
    # Update GUI with new data written to FPGA
    gui_wdata.config(text=write_data)
    # Complete timing analysis
    t = time.time() - st
    out_time_array.append(t)
    out_time_array.pop(0)
    t_avg = sum(out_time_array)/time_average_range
    t_win = window_size * t_avg
    # Update GUI with timing analysis
    gui_outtimer.config(text='Out Time = {0:.9f} seconds. Estimated Time Per Window = {1:.9f} seconds.'.format(t_avg,t_win))
    # Schedule next read
    gui.after(DELAY, test_read_data)

# Initialize GUI labels
gui = tkinter.Tk()
gui.title('Test COM')
var = tkinter.IntVar()
# Display Data from FPGA
gui_data = tkinter.Label(gui, text=bytearray(data_in_size), width=250)
gui_data.pack()
# Display the Data currently being written to FPGA
gui_wdata = tkinter.Label(gui, text=bytearray(data_out_size))
gui_wdata.pack()
# Display the Current time to Read and Estimated Total time
gui_intimer = tkinter.Label(gui, text=bytearray(16))
gui_intimer.pack()
# Display the Current time to Write and Estimated Total time
gui_outtimer = tkinter.Label(gui, text=bytearray(16))
gui_outtimer.pack()
# Create Slider to vary data sent to FPGA
gui_slider = tkinter.Scale(gui, from_=0, to=25, variable=var, orient=tkinter.HORIZONTAL)
gui_slider.pack()
# Create Button to destroy window
button_exit = tkinter.Button(gui, text='Close', width=25, command=gui.destroy)
button_exit.pack()
# Schedule first Write Data
gui.after(1,test_write_data())
# Display Gui
gui.mainloop()
'''