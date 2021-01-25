# coding=gbk
import dash
from dash.dependencies import Output, Event
import dash_core_components as dcc
import dash_html_components as html
import plotly
import random #for generate random trace1, we need stream
import plotly.graph_objs as go
from collections import deque
import plotly.plotly as py
from plotly import tools

#plotly.tools.set_credentials_file(username='rtao02',api_key='zaQ7HJs2IzIu0OdzbdAV')
#X=[0,1]
#Y=[0,1]
X = deque(maxlen = 500)
Y = deque(maxlen = 500) #max elements include in queue, exceed will be popup, like FIFO
X.append(1)
Y.append(1)
X2 = deque(maxlen = 500)
Y2 = deque(maxlen = 500) #max elements include in queue, exceed will be popup, like FIFO
#X2=[0,1]
#Y2=[0,1]
X2.append(1)
Y2.append(1)
X3 = deque(maxlen = 500)
Y3 = deque(maxlen = 500) #max elements include in queue, exceed will be popup, like FIFO
X3.append(1)
Y3.append(1)
X4 = deque(maxlen = 500)
Y4 = deque(maxlen = 500) #max elements include in queue, exceed will be popup, like FIFO
X4.append(1)
Y4.append(1)
X5 = deque(maxlen = 500)
Y5 = deque(maxlen = 500) #max elements include in queue, exceed will be popup, like FIFO
X5.append(1)
Y5.append(1)
#X3=[0,1]
#Y3=[0,1]
#X4=[0,1]
#Y4=[0,1]
#X5=[0,1]
#Y5=[0,1]
app = dash.Dash(__name__)
app.layout = html.Div(
	[
		dcc.Graph(id='live-graph', animate=True),
		dcc.Interval(
			id='graph-update',
			interval=10*0.5
			)
		]
	)

@app.callback(Output('live-graph','figure'),
					events = [Event('graph-update','interval')])
					
def update_graph():
	global X
	global Y
	global X2
	global Y2
	global X3
	global Y3
	global X4
	global Y4
	global X5
	global Y5
	
	X.append(X[-1]+1) #keep add one element to X-axis
	Y.append(Y[-1]+(Y[-1]*random.uniform(-0.1,0.1)))
	X2.append(X2[-1]+1) #keep add one element to X-axis
	Y2.append(Y2[-1]+(Y2[-1]*random.uniform(-0.1,0.1)))
	X3.append(X3[-1]+1) #keep add one element to X-axis
	Y3.append(Y3[-1]+(Y3[-1]*random.uniform(-0.1,0.1)))
	X4.append(X4[-1]+1) #keep add one element to X-axis
	Y4.append(Y4[-1]+(Y4[-1]*random.uniform(-0.1,0.1)))
	X5.append(X5[-1]+1) #keep add one element to X-axis
	Y5.append(Y5[-1]+(Y5[-1]*random.uniform(-0.1,0.1)))

	fig = plotly.tools.make_subplots(rows=3, cols=2, vertical_spacing=0.1)
	fig['layout']['margin'] = {
        'l': 20, 'r': 10, 'b': 20, 't': 20
    }
	fig['layout']['legend'] = {'x': 0, 'y': 1, 'xanchor': 'left'}
	
	fig['layout']['xaxis1'].update(range=[min(X), min(X)+50])

	fig['layout']['xaxis2'].update(range=[min(X2), min(X2)+50])

	fig['layout']['xaxis3'].update(range=[min(X3), min(X3)+50])
	
	fig['layout']['xaxis4'].update(range=[min(X4), min(X4)+50])

	fig['layout']['xaxis5'].update(range=[min(X5), min(X5)+50])
	
	fig['layout']['yaxis1'].update(range=[0,2])

	fig['layout']['yaxis2'].update(range=[0,2])

	fig['layout']['yaxis3'].update(range=[0,2])
	
	fig['layout']['yaxis4'].update(range=[0,2])

	fig['layout']['yaxis5'].update(range=[0,2])
	
#	fig['layout']['xaxis4'] = dict(range=[min(X4), max(X4)])

#	fig['layout']['xaxis5'] = dict(range=[min(X5), max(X5)])
	fig.append_trace({
        'x': list(X),
        'y': list(Y),
        'name': 'Scatter1',
        'mode': 'lines+markers',
        #'type': 'scatter'
    }, 1, 1)

	fig.append_trace({
        'x': list(X2),
        'y': list(Y2),
        'name': 'Scatter2',
        'mode': 'lines+markers',
        #'type': 'scatter'
    }, 1, 2)
    
	fig.append_trace({
        'x': list(X3),
        'y': list(Y3),
        'name': 'Scatter3',
        'mode': 'lines+markers',
        #'type': 'scatter'
    }, 2, 1)
	fig.append_trace({
        'x': list(X4),
        'y': list(Y4),
        'name': 'Scatter4',
        'mode': 'lines+markers',
        #'type': 'scatter'
    }, 2, 2)
	fig.append_trace({
        'x': list(X5),
        'y': list(Y5),
        'name': 'Scatter5',
        'mode': 'lines+markers',
        #'type': 'scatter'
    }, 3, 1)
    
	return fig
		   
if __name__ =="__main__":
	app.run_server(debug=True)
