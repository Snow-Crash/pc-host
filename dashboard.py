
import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go

import numpy as np

from timeit import default_timer as timer

# CONSTANTS
WINDOW = 450
SYNAPSES = 10
NEURONS = 2
PATTERNS = 10
INTERVAL_LONG = 12*60*60*1000 # 12 Hour(s)
INTERVAL_SHORT = 500

class plotConfig:
    pass

# DATA and STRUCTURES for BASIC TESTING PURPOSES ONLY
WINDOW_TOY = 12
test = np.zeros([WINDOW_TOY,2])
test[0] = [4, 9]
test[1] = [1, 4]
test[2] = [3, 1]
test[3] = [5, 4]
test[4] = [4, 9]
test[5] = [-1, 4]
test[6] = [3, 1]
test[7] = [5, -4]
test[8] = [4, 9]
test[9] = [1, -4]
test[10] = [-3, -1]
test[11] = [5, 4]

class counter_struct():
    ''' Toy class that is able to keep track of a state. Used for testing purposes only. '''
    def __init__(self):
        self.counter = 0
        self.timer = 0

    def inc(self):
        self.counter += 1

    def get_cou(self):
        return self.counter

    def reset(self):
        self.counter = 0

mcs = counter_struct()


# START OF GUI
class plot_config:
    class plot_type:
        isSpikePlot = False
        layout = go.Layout(
            showlegend=False,
            yaxis=dict(
                title='Parent Title',
                range=None
            ))

    class raw_input(plot_type):
        isSpikePlot = False
        layout = go.Layout(
            showlegend=False,
            yaxis=dict(
                title='Input Voltage',
                range=None
            ))

    class input_spike(plot_type):
        isSpikePlot = True
        layout = go.Layout(
            showlegend=False,
            yaxis=dict(
                title='Synapse Index',
                range=[0,SYNAPSES]
            ))

    class psp(plot_type):
        isSpikePlot = False
        layout = go.Layout(
                showlegend=False,
                yaxis=dict(
                    title='Post Synapse Potential',
                    range=None
                ))

    class membrane(plot_type):
        isSpikePlot = False
        layout = go.Layout(
            showlegend=False,
            yaxis=dict(
                title='Membrane Voltage',
                range=None
            ))

    class output_spike(plot_type):
        isSpikePlot = True
        layout = go.Layout(
            showlegend=False,
            yaxis=dict(
                title='Neuron Index',
                range=[0,NEURONS]
            ))

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=None)

colors = {
    'background': '#000000',
    'text': '#D44500'
}

def numpy2DArrayToPlot(array2d: np.array, config: plot_config.plot_type):
    ''' Wraps the declaration needed to create a plot. '''
    return dcc.Graph(
        # id='basic-test',
        figure={
            'data': numpy2DArrayToPlotList(array2d, config),
            'layout': config.layout
        },
        config={'staticPlot': True}
    )

def numpy2DArrayToPlotList(array2d: np.array, config: plot_config.plot_type):
    '''
    Helper function for numpy2DArrayToPlot List. Creates dictionaries for all data sets on a single plot.
    Currently only makes line plots.
    '''
    l = []
    for element in range(array2d[0].__len__()):
        d = {}
        for cycle in range(array2d.__len__()):
            d['x'] = list(range(array2d.__len__()))
            d['y'] = np.where(array2d[:,element] > 0, element, -1) if config.isSpikePlot else array2d[:,element]
        d['name'] = 'Test '+ element.__str__()
        d['mode'] = 'markers' if config.isSpikePlot else 'lines+markers'
        d['markers'] = {'size': 12}
        l.append(d)
    return l

def create_pattern_select_list(length):
    '''
    Creates the list of patterns to select using the dropdown menu. Includes an option for random (currently 'R').
    :param length:
    :return:
    '''
    l = []
    for i in range(length):
        d = {}
        d['label'] = i.__str__()
        d['value'] = i.__str__()
        l.append(d)
    l.append({'label':'Random', 'value':'R'})
    return l

def ui_main_block():
    '''
    This function builds the main data section of the GUI, including buttons and plots.
    '''
    return [html.Div(children=[html.Label('Pattern Select'),
            dcc.Dropdown(
                id='dropdown_pattern',
                options=create_pattern_select_list(PATTERNS),
                value='R'
            ),                 html.Button('Set Spikes',id='b_spikes',n_clicks_timestamp=0),
                               html.Button('Run One Step',id='b_onestep', n_clicks_timestamp=0),
                               html.Button('Run to End',id='b_run', n_clicks_timestamp=0),
                               html.Button('Reset',id='b_reset', n_clicks_timestamp=0),
                               html.Div(id='div_currentPattern'),
                               html.Div(id='div_currentButton')
            ],style={'grid-column':1}),
            html.Div(id='plot_rawInput',children=numpy2DArrayToPlot(test,plot_config.raw_input),style={'grid-column': '2 / 4', 'grid-row': '1 / 3'}),
            html.Div(id='plot_inputSpikeTrain',children=numpy2DArrayToPlot(test+20,plot_config.input_spike), style={'grid-column': '4 / 6', 'grid-row': '1 / 3'}),
            html.Div(id='plot_psp',children=numpy2DArrayToPlot(test+30,plot_config.psp), style={'grid-column': '2 / 4', 'grid-row': '4 / 6'}),
            html.Div(id='plot_membrane',children=numpy2DArrayToPlot(test+40, plot_config.membrane), style={'grid-column': '4 / 6', 'grid-row': '4 / 6'}),
            html.Div(id='plot_outputSpike',children=numpy2DArrayToPlot(test+50, plot_config.output_spike), style={'grid-column': '4 / 6', 'grid-row': '6 / 8'})
            ]

app.layout = html.Div(style={}, children=[
    # Title Bar
    html.H1(
        children='ISLPED DEMO',
        style={
            'textAlign': 'left',
            'color': colors['text']
        }
    ),
    # Main Data Block
    html.Div(
        id='div_maindata',
        children=ui_main_block(),
        style={'display':'grid',
               'grid-template-columns': 'repeat(5, 1fr)',
               'grid-gap': '10px',
               'grid-auto-rows': 'minmax(50px, auto)'}
    ),
    html.Div([dcc.Interval(id='interval_component',n_intervals=0)]),
    # Log
    html.Div(id='log')
    # TODO
])

# START OF STATE STRUCTURE
class state():
    '''
    This class keeps track of the current status of the simulation.
    '''
    def __init__(self):
        # Initiate with dummy data to avoid conflicts with plotly
        self.input_raw = np.zeros([1, SYNAPSES])
        self.input_spike_train = np.zeros([1,SYNAPSES])
        self.psp = np.zeros([1,SYNAPSES])
        self.membrane = np.zeros([1,NEURONS])
        self.output_spike = np.zeros([1,NEURONS])
        self.step = 0
        self.lastPlotStep = 0
        self.pattern = 0

    def update(self, raw_input_stream, in_spike_train, out_psp, out_membrane, out_spike):
        '''
        Update the previous state of the neuron. Automatically increments step counter.
        :param raw_input_stream:
        :param in_spike_train:
        :param out_psp:
        :param out_membrane:
        :param out_spike:
        :return:
        '''
        if self.step == WINDOW:
            return None
        if self.step == 0:
            # Replace dummy data with first actual input
            self.input_raw = raw_input_stream
            self.input_spike_train = in_spike_train
            self.psp = out_psp
            self.membrane = out_membrane
            self.output_spike = out_spike
        else:
            # Append data as a new row via np.vstack
            self.input_raw = np.vstack((self.input_raw,raw_input_stream))
            self.input_spike_train = np.vstack((self.input_spike_train,in_spike_train))
            self.psp = np.vstack((self.psp,out_psp))
            self.membrane = np.vstack((self.membrane,out_membrane))
            self.output_spike = np.vstack((self.output_spike,out_spike))
        self.step += 1 % WINDOW

    def reset(self):
        '''
        Set all internal values to a 1 dimension dummy values, and step to 0.
        :return:
        '''
        self.input_raw = np.zeros([1, SYNAPSES])
        self.input_spike_train = np.zeros([1, SYNAPSES])
        self.psp = np.zeros([1, SYNAPSES])
        self.membrane = np.zeros([1, NEURONS])
        self.output_spike = np.zeros([1, NEURONS])
        self.step = 0
        self.lastPlotStep = 0

    def set_pattern(self, pattern):
        self.pattern = pattern

    def get_pattern(self):
        return self.pattern

    def set_step(self, step):
        self.step = step

    def get_step(self):
        return self.step

# Create a structure to store the state of the simulation
state = state()

# Callback Functions
@app.callback(
    dash.dependencies.Output('div_currentPattern', 'children'),
    [dash.dependencies.Input('dropdown_pattern', 'value')])
def dropdown_update(value):
    '''
    This function is to update the spike pattern based on the dropdown menu.
    '''
    state.set_pattern(value)
    return 'Currently testing pattern "{}" {}.'.format(value, state.get_pattern())

@app.callback([dash.dependencies.Output('div_currentButton', 'children'),
               dash.dependencies.Output('interval_component', 'interval'),
               dash.dependencies.Output('plot_rawInput', 'children'),
               dash.dependencies.Output('plot_inputSpikeTrain', 'children'),
               dash.dependencies.Output('plot_psp', 'children'),
               dash.dependencies.Output('plot_membrane', 'children'),
               dash.dependencies.Output('plot_outputSpike', 'children')],
              [dash.dependencies.Input('b_spikes', 'n_clicks_timestamp'),
               dash.dependencies.Input('b_onestep', 'n_clicks_timestamp'),
               dash.dependencies.Input('b_run', 'n_clicks_timestamp'),
               dash.dependencies.Input('b_reset', 'n_clicks_timestamp'),
               dash.dependencies.Input('interval_component', 'n_intervals')])
def button_update(btn1, btn2, btn3, btn4, interval_count):
    '''
    This function initiates calls to the FPGA based on interactiosn with the buttons. It also updates the plots.
    '''
    button_timestamps = [int(btn1), int(btn2), int(btn3), int(btn4)]
    button_timestamps.sort(reverse = True)
    next_interval = INTERVAL_LONG
    mode = None
    delay = timer() - mcs.timer
    # s, p, v = None, None, None
    if int(btn1) == button_timestamps[0]:
        # Set the Spike Pattern
        # mcs.inc()
        mode = 'Set Spikes'
        # As picking an option on the dropdown does not need comfirmation, this button is currently unimplemented
    elif int(btn2) == button_timestamps[0]:
        mode = 'Run One Step'
        # # Run for one step and then stop
        # controller.set_spikes(spike[state.get_pattern(), state.get_step(), :])
        # s, p, v = controller.run_one_step()
        # state.update(raw_input_stream=spike[state.get_pattern(), state.get_step(), :],
        #              in_spike_train=spike[state.get_pattern(), state.get_step(), :], out_psp=p, out_membrane=v,
        #              out_spike=s)
        # State Class Testing
        if state.get_step() < WINDOW:
            gen_InputStream = np.random.randn(1,SYNAPSES)
            gen_SpikePatternInd = np.where(gen_InputStream > 0.5)[1]
            gen_SpikePattern = np.zeros([1, SYNAPSES]) - 1
            for ind in gen_SpikePatternInd:
                gen_SpikePattern[0, ind] = ind
            gen_PSP = np.random.randn(1, SYNAPSES)
            gen_Membrane = np.random.randn(1, NEURONS)
            gen_OutInd = np.where(gen_Membrane > 0.5)[1]
            gen_SpikePatternOut = np.zeros([1, NEURONS]) - 1
            for ind in gen_OutInd:
                gen_SpikePatternOut[0, ind] = ind
            state.update(raw_input_stream=gen_InputStream,in_spike_train=gen_SpikePattern,out_psp=gen_PSP,out_membrane=gen_Membrane,out_spike=gen_SpikePatternOut)
        # # Toy Example Testing
        # mcs.inc()
        # Suppress Timed Updates
        next_interval = INTERVAL_LONG
    elif int(btn3) == button_timestamps[0]:
        mode = 'Run to End'
        # Run until the end of the current window
        # for step in range(WINDOW - state.get_step()):
        #     controller.set_spikes(spike[state.get_pattern(), state.get_step(), :])
        #     s, p, v = controller.run_one_step()
        #     state.update(raw_input_stream=spike[state.get_pattern(),state.get_step(), :],in_spike_train=spike[state.get_pattern(),state.get_step(), :], out_psp=p, out_membrane=v, out_spike=s)

        # State Class Testing
        if state.get_step() < WINDOW:
            start = timer()
            # while state.get_step() < WINDOW:
            gen_InputStream = np.random.randn(1,SYNAPSES)
            gen_SpikePatternInd = np.where(gen_InputStream > 0.5)[1]
            gen_SpikePattern = np.zeros([1,SYNAPSES]) - 1
            for ind in gen_SpikePatternInd:
                gen_SpikePattern[0, ind] = ind
            gen_PSP = np.random.randn(1, SYNAPSES)
            gen_Membrane = np.random.randn(1, NEURONS)
            gen_OutInd = np.where(gen_Membrane > 0.5)[1]
            gen_SpikePatternOut = np.zeros([1, NEURONS]) - 1
            for ind in gen_OutInd:
                gen_SpikePatternOut[0, ind] = ind
            state.update(raw_input_stream=gen_InputStream,in_spike_train=gen_SpikePattern,out_psp=gen_PSP,out_membrane=gen_Membrane,out_spike=gen_SpikePatternOut)
            next_interval = INTERVAL_SHORT
            end = timer()
            print(end - start)
            mcs.timer = timer()
        else:
            # Suppress Timed Updates
            next_interval = INTERVAL_LONG
            delay = timer() - mcs.timer

        # # Toy Example Testing
        # if mcs.get_cou() < WINDOW_TOY:
        #     mcs.inc()
        #     next_interval = INTERVAL_SHORT
        # else:
        #     next_interval = INTERVAL_LONG
    elif int(btn4) == button_timestamps[0]:
        mode = 'Reset'
        # # Reset the current state both on board and in state
        # controller.reset_neuron()
        # state.reset()
        # State Class Testing
        state.reset()
        # # Toy Example Testing
        # mcs.reset()
        # Suppress Timed Updates
        next_interval =  INTERVAL_LONG

    # return 'Current Mode: "{}" {}.'.format(mode, 1), \
    #        next_interval,\
    #        numpy2DArrayToPlot(test[:mcs.get_cou()+1],plot_config.raw_input),\
    #        numpy2DArrayToPlot(test,plot_config.input_spike),\
    #        numpy2DArrayToPlot(test,plot_config.psp),\
    #        numpy2DArrayToPlot(test,plot_config.membrane),\
    #        numpy2DArrayToPlot(test,plot_config.output_spike)

    mcs.timer = timer()

    return 'Current Mode: "{}" {}.'.format(mode, delay), \
           next_interval,\
           numpy2DArrayToPlot(state.input_raw,plot_config.raw_input), \
           numpy2DArrayToPlot(state.input_spike_train,plot_config.input_spike), \
           numpy2DArrayToPlot(state.psp,plot_config.psp), \
           numpy2DArrayToPlot(state.membrane,plot_config.membrane), \
           numpy2DArrayToPlot(state.output_spike,plot_config.output_spike)

# Run the Server (Should come last)
if __name__ == '__main__':
    app.run_server(debug=False, use_reloader=False) # See https://stackoverflow.com/questions/50390506/how-to-make-serial-communication-from-python-dash-server
