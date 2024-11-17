
import pandas as pd
import dash
from dash import dcc, html  # Updated import statements
from dash.dependencies import Input, Output
import plotly.express as px
import plotly.graph_objs as go
import logging

# Initialize the Dash app
app = dash.Dash(__name__, suppress_callback_exceptions=True, assets_folder='assets')
server = app.server  # Expose the server for WSGI

# Enable logging
logging.basicConfig(level=logging.DEBUG)

# Load your CSV dataset
data = pd.read_csv('DASH_ZA11172024.csv')

# Paths for images - make sure your images are placed in the 'assets' folder
logo1_path = '/assets/logo1.png'
logo2_path = '/assets/logo2.png'
logo3_path = '/assets/logo3.png'

# Top bar with logos using correct image paths
top_bar = html.Div([
    html.Img(src=logo1_path, style={'height': '300%', 'width': '300%', 'float': 'left'}),
    html.Img(src=logo3_path, style={'height': '300%', 'width': '300%', 'text-align': 'center'}),
    html.Img(src=logo2_path, style={'height': '300%', 'width': '300%', 'float': 'right'})
], style={'display': 'flex', 'justify-content': 'space-between'})

# Gauge for Total Number of Household Contacted
hh_num_count = data['hh_num'].count()
gauge1 = go.Figure(go.Indicator(
    mode="gauge+number",
    value=hh_num_count,
    title={'text': "Total Number of Household Contacted and had Completed Interviews"},
    gauge={'axis': {'range': [0, 1500]}, 'bar': {'color': '#1E90FF'}},  # Dodger Blue
    number={'valueformat': ','}
))

# Gauge for Total Number of Household who gave Consent
consent_check_count = data['consent_check'].count()
gauge2 = go.Figure(go.Indicator(
    mode="gauge+number",
    value=consent_check_count,
    title={'text': "Total Number of Household who gave Consent to Complete an Interview"},
    gauge={'axis': {'range': [0, 1500]}, 'bar': {'color': '#32CD32'}},  # Lime Green
    number={'valueformat': ','}
))

# Pie chart for Gender Distribution
gender_distribution = data['A2'].map({1: 'Male', 2: 'Female'}).value_counts()
pie_chart_gender = px.pie(gender_distribution, names=gender_distribution.index, values=gender_distribution.values,
                          title='Gender Distribution', color_discrete_sequence=['#FF6347', '#4682B4'])  # Tomato and Steel Blue
pie_chart_gender.update_traces(text=gender_distribution.values, textposition='inside')

if 'A1' in data.columns:
    # Create Age Group Variable and Bar Chart
    bins = [10, 15, 20, 25]
    labels = ['10-14', '15-19', '20-24']
    data['age_group'] = pd.cut(data['A1'], bins=bins, labels=labels, right=False)

    # Count the number of participants in each age group
    age_group_count = data['age_group'].value_counts().sort_index()

    # Create the bar chart with distinct color
    age_group_bar = px.bar(age_group_count,
                           x=age_group_count.index,
                           y=age_group_count.values,
                           title='The Adolescence Participated Age Group',
                           labels={'x': 'Age Group', 'y': 'Frequency'},
                           color_discrete_sequence=['#FFD700'])  # Gold color

    # Add value labels on top of each bar
    age_group_bar.update_traces(text=age_group_count.values, textposition='outside')

    # Increase the size of the graph for better visibility
    age_group_bar.update_layout(width=800, height=500)

# Pie chart for Age Group Distribution
pie_chart_age = px.pie(age_group_count, names=age_group_count.index, values=age_group_count.values,
                       title='Age Group Distribution', color_discrete_sequence=['#FFB6C1', '#FFE4B5', '#98FB98'])  # Light Pink, Lemon Chiffon, and Pale Green
pie_chart_age.update_traces(text=age_group_count.values, textposition='inside')

# Map the gender values
labels = {1: 'Male', 2: 'Female'}
data['gender'] = data['A2'].map(labels)

# Calculate the counts of each gender within each age group
age_gender_distribution = data.groupby(['age_group', 'gender'], observed=False).size().reset_index(name='count')

# Create the grouped bar chart with accurate count on the bars
bar_chart_age_gender = px.bar(age_gender_distribution, x='age_group', y='count', color='gender',
                              title='Gender Distribution by Age Group',
                              labels={'age_group': 'Age Group', 'count': 'Frequency', 'gender': 'Gender'},
                              barmode='group',
                              color_discrete_map={'Male': '#6495ED', 'Female': '#FF69B4'})  # Cornflower Blue and Hot Pink

# Add the actual count on top of each bar
bar_chart_age_gender.update_traces(texttemplate='%{y}', textposition='outside')

# Increase the width and height of the graph
bar_chart_age_gender.update_layout(
    uniformtext_minsize=8,
    uniformtext_mode='hide',
    width=1000,  # Adjust width as needed (e.g., 1000 pixels)
    height=800   # Adjust height as needed (e.g., 700 pixels)
)

# Progress Line Graph for Household Contacts across different Data Collectors
progress_line_data = data.groupby('dc_name')['hh_num'].count().reset_index()
progress_line = px.line(progress_line_data, x='dc_name', y='hh_num', title='Progress of Household Contacted by Data Collectors',
                        labels={'dc_name': 'Data Collectors Name', 'hh_num': 'Households Contacted'},
                        color_discrete_sequence=['#6A5ACD'])  # Slate Blue
progress_line.update_traces(text=progress_line_data['hh_num'], textposition='top center')

# Bar Graph for HB Test Agreement with corrected x-axis label
hb_test_agreement = data['J3_check'].map({1: 'No', 2: 'Yes'}).value_counts()
hb_test_agreement_df = hb_test_agreement.reset_index()  # Create a DataFrame for the bar graph

# Rename columns for clarity
hb_test_agreement_df.columns = ['HB Agreement', 'Frequency']

bar_graph_hb_test = px.bar(hb_test_agreement_df, x='HB Agreement', y='Frequency',
                            title='The Adolescents that Agreed to Take the HB Test and Those Who Did Not Agree',
                            labels={'HB Agreement': 'HB Agreement', 'Frequency': 'Frequency'},
                            color_discrete_sequence=['#FF4500', '#20B2AA'])  # Orange Red and Light Sea Green
bar_graph_hb_test.update_traces(text=hb_test_agreement_df['Frequency'].values, textposition='outside')

# Adjust the x-axis title and increase the graph size
bar_graph_hb_test.update_layout(
    xaxis_title="HB Agreement: Yes or No",
    width=800,  # Increase the width
    height=700  # Increase the height
)
# Bar Graph for Skipping Rope vs Control
filtered_data = data['lti_sr_group'].value_counts()[['skipping rope', 'control']]

# Create the bar graph using Plotly
bar_graph_sr_control = go.Figure(data=[
    go.Bar(name='Skipping Rope', x=['Skipping Rope'], y=[filtered_data['skipping rope']], marker_color='#90EE90'),  # Light Green
    go.Bar(name='Control', x=['Control'], y=[filtered_data['control']], marker_color='#FFB6C1')  # Light Pink
])

# Update the layout and titles
bar_graph_sr_control.update_layout(
    title="Skipping Rope vs Control Participants",
    yaxis_title='Frequency',
    xaxis_title='Participants',
    width=800,
    height=500
)

# Add the actual counts on top of each bar
for i, count in enumerate(filtered_data):
    bar_graph_sr_control.add_annotation(
        x=['Skipping Rope', 'Control'][i],
        y=count + 0.05,
        text=str(count),
        showarrow=False,
        font=dict(size=14)
    )

# Layout of the Dash App (remains unchanged)
app.layout = html.Div([
    top_bar,
    dcc.Graph(figure=gauge1),
    dcc.Graph(figure=gauge2),
    dcc.Graph(figure=pie_chart_gender),
    dcc.Graph(figure=age_group_bar),
    dcc.Graph(figure=pie_chart_age),
    dcc.Graph(figure=bar_chart_age_gender),
    dcc.Graph(figure=progress_line),
    dcc.Graph(figure=bar_graph_hb_test),
    dcc.Graph(figure=bar_graph_sr_control)  # Added new bar graph for 'skipping rope' vs 'control'
])

# Run the Dash app
if __name__ == '__main__':
    app.run_server(debug=False, port=8050)  # debug=False for production
