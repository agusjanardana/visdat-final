import pandas as pd
from bokeh.io import curdoc
from bokeh.plotting import figure
from bokeh.models import HoverTool, ColumnDataSource
from bokeh.models import CategoricalColorMapper
from bokeh.palettes import Spectral6
from bokeh.layouts import widgetbox, row, gridplot, column
from bokeh.models import Slider, Select, RangeSlider, Div, Column, CustomJS

data = pd.read_csv("./data/dataset-india.csv")

# Make a list of the unique values from the region column: states_list
states_list = data.State.unique().tolist()

# Make a color mapper: color_mapper
color_mapper = CategoricalColorMapper(factors=states_list, palette=Spectral6)
data['Negative'] = pd.to_numeric(data['Negative'],errors='coerce')
data['Negative'] = data['Negative'].fillna(0)
data['Positive'] = data['Positive'].fillna(0)

# change date column to date type
data['Date'] = pd.to_datetime(data['Date'])
data_month_year = data['Date'].dt.to_period('M').astype(str)
data_month_year =  pd.to_datetime(data_month_year)
date_unique = data_month_year.unique()
number_dates = len(list(date_unique))
start_dates = date_unique.copy()
end_dates = date_unique.copy()

data_grouped_by_state = data.loc[data['State'] == states_list[0]]
mask = (data_grouped_by_state['Date'] >= start_dates[0]) & (data_grouped_by_state['Date'] <= end_dates[len(end_dates)-1] )
data_x = data_grouped_by_state.loc[mask]
print(data_x)
min_date = min(data['Date'])


# list wilayah
# # array(['Andaman And Nicobar', 'Andhra Pradesh', 'Arunachal Pradesh',
#        'Assam', 'Bihar', 'Chandigarh', 'Chhattisgarh',
#        'Dadra And Nagar Haveli And Daman And Diu', 'Delhi', 'Goa',
#        'Gujarat', 'Haryana', 'Himachal Pradesh', 'Jammu And Kashmir',
#        'Jharkhand', 'Karnataka', 'Kerala', 'Ladakh', 'Lakshadweep',
#        'Madhya Pradesh', 'Maharashtra', 'Manipur', 'Meghalaya', 'Mizoram',
#        'Nagaland', 'Odisha', 'Puducherry', 'Punjab', 'Rajasthan',
#        'Sikkim', 'Tamil Nadu', 'Telengana', 'Tripura', 'Uttar Pradesh',
#        'Uttarakhand', 'West Bengal']
       

# Make the ColumnDataSource: source
# source = ColumnDataSource(data={
#     'x'       : data.loc[data['Date'] == min_date].Date, 
#     'y'       : data.loc[data['Date'] == min_date].Negative, 
#     'State'     : data.loc[data['Date'] == min_date].State,
# })
source = ColumnDataSource(data={
    'x'       : data_x.Date, 
    'y'       : data_x.Negative,
    'State'   : data_x.State 
})

# Create the figure: plot
plot = figure(title="Chart", x_axis_label='Tahun', y_axis_label='Jumlah')

# Add a circle glyph to the figure p
plot.line(source=source, x='x', y='y', line_width=1)

# Set the legend and axis attributes
# plot.legend.location = 'bottom_left'

# Define the callback function: update_plot
def update_plot(attr, old, new):
    # set the `yr` name to `slider.value` and `source.data = new_data`
    # yr = slider.value
    # x = x_select.value
    y = y_select.value
    # Label axes of plot
    plot.xaxis.axis_label = x
    plot.yaxis.axis_label = y
    # new data
    new_data = {
    'x'       : data.loc[yr][x],
    'y'       : data.loc[yr][y],
    'country' : data.loc[yr].Country,
    'pop'     : (data.loc[yr].population / 20000000) + 2,
    'region'  : data.loc[yr].region,
    }
    source.data = new_data
    
    # Add title to figure: plot.title.text
    plot.title.text = 'Gapminder data for %d' % yr



range_slider = RangeSlider(start=0, end=number_dates, value=(0, number_dates), step=1, title="",  tooltips = False, width=600, show_value = False)
div = Div(text = "Date Range: <b>" + str(start_dates[range_slider.value[0]]) + ' . . . ' + str(end_dates[range_slider.value[1]-1]) + '</b>', render_as_text = False, width = 575)

code = '''
range = Math.round(Number(cb_obj.value[1] - cb_obj.value[0]), 10)
range = range < 10 ? '0' + range : range
div.text = "Date Range: <b>" + start_dates[Math.round(cb_obj.value[0], 10)] + '&nbsp;.&nbsp;.&nbsp;.&nbsp;' + end_dates[Math.round(cb_obj.value[1], 10) + -1] + '</b>'
'''

range_slider.js_on_change('value_throttled', CustomJS(args = {'div': div, 'start_dates': start_dates, 'end_dates': end_dates}, code=code))


# Create a dropdown Select widget for the y data: y_select
y_select = Select(
    options=['Negative', 'Positive'],
    value='Negative',
    title='y-axis data'
)
# Attach the update_plot callback to the 'value' property of y_select
y_select.on_change('value', update_plot)
    
# Create layout and add to current document
layout = column(row(widgetbox(range_slider,  y_select), plot)) 
curdoc().add_root(layout)