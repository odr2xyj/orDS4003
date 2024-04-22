# %% [markdown]
# ### DS 4003 Final Project

# %%
# import dependencies
from dash import Dash, dcc, html, Input, Output, callback
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt
import numpy as np
import plotly.graph_objs as go
import textwrap
import dash_bootstrap_components as dbc
import base64
from PIL import Image

# %%
# read in data
df = pd.read_csv('/Users/oliviarichine/Documents/DS 4003/data.csv')

#%%
# create avg sleep variable
df['avg_sleep_hours'] = (df['work_sleep_hours'] + df['nonwork_sleep_hours']) / 2

#%%
# drop rows with outlier values for boxplots
columns_to_drop_outliers = ['caffeine_per_day', 'alcohol_per_week', 'min_sleep_to_function']
Q1 = df[columns_to_drop_outliers].quantile(0.25)
Q3 = df[columns_to_drop_outliers].quantile(0.75)
IQR = Q3 - Q1
lower_bound = Q1 - 1.5 * IQR
upper_bound = Q3 + 1.5 * IQR
df = df[~((df[columns_to_drop_outliers] < lower_bound) | (df[columns_to_drop_outliers] > upper_bound)).any(axis=1)]

#%%
# drop rows with missing values in the callback columns
drop_columns_missing = ['gender', 'age', 'weight', 'avg_sleep_hours', 'think_sleep_problem']
df = df.dropna(subset=drop_columns_missing)

#%%
# define the image path for sleepy cloud pic
image_path = "dreamy-night-cloud-png-5693617.webp"
# Function to convert image to base64
def b64_image(image_filename):
    with open(image_filename, 'rb') as f:
        image = f.read()
    return 'data:image/png;base64,' + base64.b64encode(image).decode('utf-8')
# load image
pil_img = Image.open(image_path)


#%%
# set up app and use stylesheet and colors
app = Dash(__name__, external_stylesheets=[dbc.themes.LITERA])
server = app.server
night_colors = ['#443266', '#7165a3', '#a29ac9', '#d3c0f1', '#eae3ff']

# define layout structure 
app.layout = html.Div([

    # set up nav bar with links to git hub and data source
    html.Nav([
        html.Ul([
            html.Li(html.A("Link to Git Hub", href="https://github.com/odr2xyj", target="_blank", style={'color': 'white'})),
            html.Li(html.A("Link to Original Data Source", href="https://ropercenter.cornell.edu/ipoll/study/31115353", target="_blank", style={'color': 'white'}))  
        # make text to the right side
        ], style={'list-style-type': 'none', 'margin': '0', 'padding': '0', 'overflow': 'hidden', 'text-align': 'right'}),
    # make color purple
    ], style={'background-color': night_colors[2], 'overflow': 'hidden'}),
    

    # set up app title and sleep image, make them both centered
    html.Div(style={'display': 'flex', 'justify-content': 'center', 'align-items': 'center'}, children=[
        html.H1("Sleep and Health Database", style={'font-size': '2.5rem'}),
        html.Img(src=b64_image(image_path), style={'height': '100px', 'margin-left': '10px'})
    ]),

    # set up paragraph text explaining app interactivity
    html.Div(style={'text-align': 'center'}, children=[
        # make first line slightly bigger than others
        html.P("Sleep is an essential part of health and well-being.", style={'font-size': '1.2rem'}),
        html.P("This app utilizes sleep data to analyze its correlation with certain health factors.", style={'font-size': '.8rem'}),
        html.P("Drag the sliders and adjust the radio buttons to explore different demographics of sleepers.", style={'font-size': '.8rem'}),
        html.P("Have fun exploring insights and happy sleeping:)", style={'font-size': '.8rem'}),
        # make divider after text
        html.Hr(style={'margin': '20px 0', 'width': '100%'})
    ]),
    

    # range slider for weight
    html.Div([
        html.Label('Weight Range:'),
        # pull min and max from data varaible 'weight' and make slider start at 70 and go every 40
        dcc.RangeSlider(
            id='weight-slider',
            min=int(df['weight'].min()),
            max=int(df['weight'].max()),
            step=1,
            value=[int(df['weight'].min()), int(df['weight'].max())],  
            marks={i: str(i) for i in range(int(df['weight'].min()) - 7, int(df['weight'].max()) + 1, 40)}
        )
    # text in the center, fourth of the width
    ], style={'width': '25%', 'display': 'inline-block', 'text-align': 'center'}),

    # range slider for age
    html.Div([
        # pull min and max from variable 'age', make slider marks every 10
        html.Label('Age Range:'),
        dcc.RangeSlider(
            id='age-slider',
            min=int(df['age'].min()),
            max=int(df['age'].max()),
            step=1,
            value=[int(df['age'].min()), int(df['age'].max())],
            marks={i: str(i) for i in range(int(df['age'].min()), int(df['age'].max()) + 1, 10)}
        )
    # text in the center, fourth of the width
    ], style={'width': '25%', 'display': 'inline-block', 'text-align': 'center'}),

    # checkbox for gender
   html.Div([
       # pull radio buttons from variable 'gender'
        html.Label('Gender:', style={'text-align': 'center'}),
        dcc.Checklist(
            id='gender-checkbox',
            options=[{'label': gender, 'value': gender} for gender in df['gender'].unique()],
            value=df['gender'].unique(),
            inline=True
        )
    # text in the center, fourth of the width
    ], style={'width': '25%', 'display': 'inline-block', 'text-align': 'center'}),

    # range slider for sleep hours
    html.Div([
        # pull max and min from variable 'avg_sleep_hours' 
        html.Label('Average Sleep Hours Range:'),
        dcc.RangeSlider(
            id='sleep-slider',
            min=df['avg_sleep_hours'].min(),
            max=df['avg_sleep_hours'].max(),
            step=0.1,  # Adjust step to allow fractional values
            value=[df['avg_sleep_hours'].min(), df['avg_sleep_hours'].max()],
            marks={i: str(i) for i in range(int(df['avg_sleep_hours'].min()), int(df['avg_sleep_hours'].max()) + 1, 1)}
        )
        # text in the center, fourth of the width
    ], style={'width': '25%', 'display': 'inline-block', 'text-align': 'center'}),

    # divider after interactivities
    html.Hr(style={'width': '100%', 'margin': '20px 0'}),

    # line for text above charts
    html.Div([
        html.Div(id='characteristics-info'),
        html.Div(id='total-people-info')
    ], style={'width': '100%', 'text-align': 'center'}),
    
    
    # bar and pie graph
    html.Div([
        # bar graph taking 75% of width
        html.Div([
            dcc.Graph(id='health-graph', style={'height': '50vh', 'width': '100%', 'display': 'inline-block'})
        ], style={'width': '75%', 'display': 'inline-block'}),

        # pie charts (takes up 25% width)
        html.Div([
            # sleep disorder pie chart
            html.Div([
                dcc.Graph(id='sleep-disorder-pie', style={'height': '100%', 'width': '100%', 'display': 'inline-block'})
            ], style={'flex': '1', 'margin': '0'}),  

            # morning or evening pie chart
            html.Div([
                dcc.Graph(id='morning-evening-pie', style={'height': '100%', 'width': '100%', 'display': 'inline-block'})
            ], style={'flex': '1', 'margin': '0'})

        ], style={'display': 'flex', 'flex-direction': 'column', 'width': '25%'})

    ], style={'display': 'flex', 'flex-direction': 'row'}),

    # box plots ( each 33.3% width)
    html.Div([
        # caffeine per day box plot
        html.Div([
            dcc.Graph(id='caffeine-box-plot', style={'height': '50vh', 'width': '100%'})
        ], style={'width': '33.33%', 'display': 'inline-block'}),

        # alcohol per week box plot
        html.Div([
            dcc.Graph(id='alcohol-box-plot', style={'height': '50vh', 'width': '100%'})
        ], style={'width': '33.33%', 'display': 'inline-block'}),

        # min sleep to function box plot
        html.Div([
            dcc.Graph(id='min-sleep-box-plot', style={'height': '50vh', 'width': '100%'})
        ], style={'width': '33.33%', 'display': 'inline-block'}),
    ])

])
 

# define callback
@app.callback(
    [
        Output('characteristics-info', 'children'),
        Output('total-people-info', 'children'),
        Output('health-graph', 'figure'),
        Output('sleep-disorder-pie', 'figure'),
        Output('morning-evening-pie', 'figure'),
        Output('caffeine-box-plot', 'figure'),
        Output('alcohol-box-plot', 'figure'),
        Output('min-sleep-box-plot', 'figure')
    ],
    [
        Input('weight-slider', 'value'),
        Input('age-slider', 'value'),
        Input('gender-checkbox', 'value'),
        Input('sleep-slider', 'value')
    ]
)
def update_graph(weight, age, gender, sleep_hours):
    # make a filtered database that takes in user entries from sliders and drop downs
    df_filtered = df[(df['weight'] >= weight[0]) & (df['weight'] <= weight[1]) & 
                     (df['age'] >= age[0]) & (df['age'] <= age[1]) & 
                     (df['gender'].isin(gender)) & 
                     (df['avg_sleep_hours'] >= sleep_hours[0]) & (df['avg_sleep_hours'] <= sleep_hours[1])]
    
    # find total number of people in filtered data
    total_individuals = len(df_filtered)

    # update numbers to display the number of people in filtered data
    characteristics_info = f"Number of people with your characteristics: {total_individuals}"
    total_people_info = f"Total number of people: {len(df)}"
    
    # calculate total percentage of "Yes" respondents to disorders in filtered data
    percentages_filtered = df_filtered[['depression', 'anxiety_disorder', 'lung_disease', 'high_blood_pressure']].apply(lambda col: col.value_counts(normalize=True).get('Yes', 0) * 100)
    
    # calculate total percentage of "Yes" respondents to disorders in filtered data
    percentages_total = df[['depression', 'anxiety_disorder', 'lung_disease', 'high_blood_pressure']].apply(lambda col: col.value_counts(normalize=True).get('Yes', 0) * 100)
    
    # create bar graph of health conditions with color scheme
    health_graph = go.Figure(data=[
        go.Bar(name='Filtered', 
               x=percentages_filtered.index, 
               y=percentages_filtered, 
               marker_color= night_colors[0]),
        go.Bar(name='Total', 
               x=percentages_total.index, 
               y=percentages_total, 
               marker_color=night_colors[1])
    ])
    
    # update graph titles, width, height, ticks, grid, and background
    health_graph.update_layout(
        title='Percentage of People with Health Disorders',
        xaxis_title='Health Condition',
        yaxis_title='Percentage of People (%)',
        barmode='group',
        width=900,
        height=600,
        xaxis=dict(
            ticktext=['Anxiety', 'Depression', 'Lung Disease', 'High Blood Pressure'],  # List of x-axis labels
            tickvals=percentages_filtered.index,
            showgrid=True, 
            gridcolor='lightgrey',
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor='lightgrey',  
        ),
        plot_bgcolor='white',
    )

    # create pie chart with percentages of people who think they have a sleep problem 
    sleep_disorder_pie = px.pie(
        names=['Yes', 'No', 'Maybe'],
        values=[
            (df_filtered['think_sleep_problem'].value_counts(normalize=True).get('Yes', 0)) * 100,
            (df_filtered['think_sleep_problem'].value_counts(normalize=True).get('No', 0)) * 100,
            (df_filtered['think_sleep_problem'].value_counts(normalize=True).get('Maybe', 0)) * 100
        ],
        # set color scheme and size
        color_discrete_sequence=night_colors,
        width=300,
        height=300
    )

    # wrap title bc was too big before
    wrapped_pie_title = "<br>".join(textwrap.wrap('Percentage of People Who Think They Have a Sleep Disorder', width=30))
    sleep_disorder_pie.update_layout(
        title=wrapped_pie_title,  
        title_font=dict(size=12)  # set title font size
    )

    # Create pie chart for morning or evening preference
    morning_evening_pie = px.pie(
        names=['Morning', 'Evening'],
        values=[
            (df_filtered['morning_person_or_evening'].value_counts(normalize=True).get('Morning person', 0)) * 100,
            (df_filtered['morning_person_or_evening'].value_counts(normalize=True).get('Evening person', 0)) * 100
        ],
        # set color scheme
        color_discrete_sequence=night_colors,
        width=300,
        height=300
    )

    # wrap title for morning or evening pie chart
    wrapped_pie_title_morning_evening = "<br>".join(textwrap.wrap('Percent of Morning or Evening People', width=30))
    morning_evening_pie.update_layout(
        title=wrapped_pie_title_morning_evening,  
        title_font=dict(size=12)  # set font size
    )

    # create box plots function for three box plots
    def create_box_plot(df, y_column, title, color_sequence, y_title):
        box_plot = px.box(df, y=y_column, color_discrete_sequence=color_sequence)

        # update background color, titles, ticks, and gridlines
        box_plot.update_layout(
            plot_bgcolor='white',
            title=title,
            yaxis_title=y_title,
            yaxis_tickfont=dict(size=10),
            xaxis_showgrid=True,
            yaxis_showgrid=True,
            xaxis_gridcolor='lightgrey',
            yaxis_gridcolor='lightgrey'
        )

        return box_plot

    # define the y-axis title for each box plot
    y_titles = {
        'caffeine_per_day': 'Number of Daily Caffeinated Beverages',
        'alcohol_per_week': 'Number of Weekly Alcoholic Beverages',
        'min_sleep_to_function': 'Number of Hours'
    }

    # define the three box plots with their respective variables
    caffeine_box = create_box_plot(df_filtered, 'caffeine_per_day', 'Average Caffeine per Day', [night_colors[0]], y_titles['caffeine_per_day'])
    alcohol_box = create_box_plot(df_filtered, 'alcohol_per_week', 'Average Alcohol per Week', [night_colors[0]], y_titles['alcohol_per_week'])
    min_sleep_box = create_box_plot(df_filtered, 'min_sleep_to_function', 'Average Minimum Sleep to Function', [night_colors[0]], y_titles['min_sleep_to_function'])

    # retuns all parts
    return characteristics_info, total_people_info, health_graph, sleep_disorder_pie, morning_evening_pie, caffeine_box, alcohol_box, min_sleep_box


# run the app
if __name__ == "__main__":
    app.run_server(debug=True)
