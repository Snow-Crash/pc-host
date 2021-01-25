import serial

from UART_COM import UART_COM
import numpy as np

# UART Com Settings
UART_PORT = 'COM6'
UART_BAUDRATE = 230400
UART_INPUT_SIZE = 243
UART_OUTPUT_SIZE = 4
# FPGA Command values
CMD_START_NEURON = 1
CMD_RESET_NEURON = 2
CMD_SET_SPIKE = 3
CMD_SET_TEST_SPIKE = 4
CMD_CLEAR_BUFFERED_SPIKE = 5

class interpreter:
    # Create an instance of the UART Communication
    def __init__(self):
        self.connection = UART_COM(port=UART_PORT, baudrate=UART_BAUDRATE, readSize=UART_INPUT_SIZE, writeSize=UART_OUTPUT_SIZE)

    # Commands to read from the FPGA
    def read_cycle(self):
        spikes = None
        PSP = None
        membrane = None
        # TODO: determine structure of output
        # TODO: Convert bytes into fixed (private function)
        return spikes, PSP, membrane

    def check_for_output(self):
        return self.connection.dataInReadBuffer()

    # Commands to write to the FPGA
    def start_cycle(self):
        self.connection.writeb(self.__output_start_neuron())

    def reset_neuron(self):
        self.connection.writeb(self.__output_reset_neuron())

    def set_spikes(self, spikeTrain: np.array):
        for i in range(spikeTrain.__len__()):
            if spikeTrain[i] != 0:
                self.connection.writeb(self.__output_set_spike(i))

    def set_test_spikes(self, spikeTrain: np.array):
        for i in range(spikeTrain.__len__()):
            if spikeTrain[i] != 0:
                self.connection.writeb(self.__output_set_test_spike(i))

    def clear_spikes(self):
        self.connection.writeb(self.__output_clear_buffered_spike())

    # This set of private functions generates the appropriate byte array structure for each write command
    def __output_start_neuron(self):
        # block = bytes([0,0,0,CMD_START_NEURON])
        block = bytearray(UART_OUTPUT_SIZE)
        block[-1] = CMD_START_NEURON
        return block

    def __output_reset_neuron(self):
        # block = bytes([0,0,0,CMD_START_NEURON])
        block = bytearray(UART_OUTPUT_SIZE)
        block[-1] = CMD_RESET_NEURON
        return block

    def __output_set_spike(self, index: int):
        # block = bytes([0,0,index,CMD_SET_SPIKE])
        block = bytearray(UART_OUTPUT_SIZE)
        block[-1] = CMD_SET_SPIKE
        block[-2] = index
        return block

    def __output_set_test_spike(self, index: int):
        # block = bytes([0,0,index,CMD_SET_TEST_SPIKE])
        block = bytearray(UART_OUTPUT_SIZE)
        block[-1] = CMD_SET_TEST_SPIKE
        block[-2] = index
        return block

    def __output_clear_buffered_spike(self):
        # block = bytes([0,0,0,CMD_START_NEURON])
        block = bytearray(UART_OUTPUT_SIZE)
        block[-1] = CMD_CLEAR_BUFFERED_SPIKE
        return block
