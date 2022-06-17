from cmath import pi
import pandas as pd
from bokeh.palettes import Category20c
from bokeh.transform import cumsum
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

# change negative data type to float and change NaN to 0
data['Negative'] = pd.to_numeric(data['Negative'], errors='coerce')
data['Negative'] = data['Negative'].fillna(0)
data['Positive'] = data['Positive'].fillna(0)

# change date column to date type
data['Date'] = pd.to_datetime(data['Date'])

# get date period per month
data_month_year = data['Date'].dt.to_period('M').astype(str)
data_month_year = pd.to_datetime(data_month_year)

# get unique date
date_unique = data_month_year.unique()
date_unique.sort()

# data for range sliders
number_dates = len(list(date_unique))
start_dates = date_unique.copy()
end_dates = date_unique.copy()

# initialize data for plot
data_grouped_by_state = data.loc[data['State'] == states_list[0]]
mask = (data_grouped_by_state['Date'] >= start_dates[0]) & (
    data_grouped_by_state['Date'] <= end_dates[len(end_dates)-1])
data_plot = data_grouped_by_state.loc[mask]

source = ColumnDataSource(data={
    'x': data_plot.Date,
    'y': data_plot.Negative,
    'State': data_plot.State
})

# Create the figure: plot
plot = figure(title="Chart", x_axis_label='Tahun',
              y_axis_label='Jumlah', x_axis_type='datetime')

# Add a circle glyph to the figure p
plot.line(source=source, x='x', y='y', line_width=1)

plot.left[0].formatter.use_scientific = False


def update_plot(attr, old, new):
    slidervalue = range_slider.value
    startdate = start_dates[slidervalue[0]]
    enddate_index = slidervalue[1]
    if slidervalue[1] == len(end_dates):
        enddate_index = slidervalue[1]-1
    enddate = end_dates[enddate_index]

    posneg = positive_negative_select.value
    selected_state = states_select.value

    data_by_state = data.loc[data['State'] == selected_state]
    mask = (data_by_state['Date'] >= startdate) & (
        data_by_state['Date'] <= enddate)
    data_plot = data_by_state.loc[mask]
    new_data = {
        'x': data_plot.Date,
        'y': data_plot[posneg],
    }
    source.data = new_data


range_slider = RangeSlider(start=0, end=number_dates, value=(
    0, number_dates), step=1, title="",  tooltips=False, width=600, show_value=False)

div = Div(text="Date Range: <b>" + pd.to_datetime(start_dates[range_slider.value[0]]).strftime('%Y-%m-%d') + ' . . . ' + pd.to_datetime(
    end_dates[range_slider.value[1]-1]).strftime('%Y-%m-%d') + '</b>', render_as_text=False, width=575)

code = '''
var range = Math.round(Number(cb_obj.value[1] - cb_obj.value[0]), 10)
range = range < 10 ? '0' + range : range
console.log(start_dates[Math.round(cb_obj.value[0], 10)], end_dates[Math.round(cb_obj.value[1], 10) + -1])
var start = new Date(start_dates[Math.round(cb_obj.value[0], 10)]).toISOString().split('T')[0]
var end = new Date(end_dates[Math.round(cb_obj.value[1], 10) + -1]).toISOString().split('T')[0]
div.text = "Date Range: <b>" + start + '&nbsp;.&nbsp;.&nbsp;.&nbsp;' + end + '</b>'
'''

# range_slider.js_on_change('value_throttled', test)
range_slider.js_on_change('value_throttled', CustomJS(
    args={'div': div, 'start_dates': start_dates, 'end_dates': end_dates}, code=code))


range_slider.on_change('value', update_plot)

# Create a dropdown Select widget for the y data: y_select
positive_negative_select = Select(
    options=['Negative', 'Positive'],
    value='Negative',
    title='Positive/Negative'
)
# Attach the update_plot callback to the 'value' property of y_select
positive_negative_select.on_change('value', update_plot)

states_select = Select(
    options=states_list,
    value=states_list[0],
    title='State'
)

states_select.on_change('value', update_plot)

# layout piechart


x = {
    'Positive': data_plot['Positive'].sum(),
    'Negative': data_plot['Negative'].sum(),
}

chart_colors = ['#44e5e2', '#e29e44', '#e244db',
                '#d8e244', '#eeeeee', '#56e244', '#007bff', 'black']

data_pie = pd.Series(x).reset_index(name='value').rename(columns={'index': 'country'})
data_pie['angle'] = data_pie['value']/data_pie['value'].sum() * 2*pi
data_pie['color'] = chart_colors[:len(x)]


p = figure(height=350, title="Pie Chart", toolbar_location=None,
           tools="hover", tooltips="@country: @value", x_range=(-0.5, 1.0))

p.wedge(x=0, y=1, radius=0.4,
        start_angle=cumsum('angle', include_zero=True), end_angle=cumsum('angle'),
        line_color="white", color='color', legend_field='country', source=data_pie)

# callback
def update_plot(attr, old, new):
    selected_state = states_select.value

    data_by_state = data.loc[data['State'] == selected_state]
    
    new_data = {
        'Positive': data_by_state['Positive'].sum(),
        'Negative': data_by_state['Negative'].sum(),
    }
    data_pie = pd.Series(new_data).reset_index(name='value').rename(columns={'index': 'country'})
    data_pie['angle'] = data_pie['value']/data_pie['value'].sum() * 2*pi
    data_pie['color'] = chart_colors[:len(new_data)]
    
states_select_pie = Select(
    options=states_list,
    value=states_list[0],
    title='State'
)

states_select_pie.on_change('value', update_plot)
# Create layout and add to current document
layout = column(
    row(widgetbox(div, range_slider,  positive_negative_select, states_select), plot),
    row(widgetbox(states_select_pie),p))
curdoc().add_root(layout)
