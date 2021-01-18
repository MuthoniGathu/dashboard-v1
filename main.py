from datetime import date
import pandas as pd
import plotly.express as px
import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
# Load Data



df = pd.read_csv("Expenses_Input.csv")

df.head()

df_copy=df.copy()

df_copy['Date'] = pd.to_datetime(df_copy['Date'])

df_copy['Month'] = pd.DatetimeIndex(df['Date']).month_name()

df_copy['Week']= pd.to_datetime(df_copy["Date"]).dt.weekofyear

df_copy['Year'] = pd.DatetimeIndex(df['Date']).year

total_df = df_copy['Cost'].groupby(df_copy["Group Description"]).sum().to_frame(name ="Sum").reset_index().sort_values(by='Sum', ascending=False).head(10)

weekly_df= df_copy.groupby(['Week', 'Year'])['Cost'].sum().to_frame(name ="Sum").reset_index()

weekly_df['Week'] = 'W' + weekly_df['Week'].astype(str)

total = sum((df_copy.Cost).astype(int))

# bar chart figure
weekly_chart_figure = px.bar(weekly_df, x="Week", y='Sum', title="Supplier",text='Sum')

#updating bar chart figure
weekly_chart_figure.update_layout(title_font_color="#2cfec1", 
                     legend_font_color="#2cfec1", 
                     legend_font_size=10, 
                     plot_bgcolor= '#1f2630', 
                     paper_bgcolor= '#1f2630',
                     yaxis=dict(
                            zeroline=True,
                            showgrid=True,
                            showline=False,
                            showticklabels=True,
                            gridcolor= "#252e3f",
                            gridwidth= 0.02,
                            zerolinecolor= "#252e3f"
                            # domain=[0, 0.85],
                        ),
                        xaxis=dict(
                            zeroline=True,
                            showline=False,
                            showticklabels=True,
                            showgrid=False,
                            # domain=[0, 0.42],
                        ),
                         font=dict(
                                size=10,
                                color='#2cfec1'
                            ))


def diff_month(end_date, start_date):
    end_date_year= pd.to_numeric(end_date.split('-')[0])
    start_date_year= pd.to_numeric(start_date.split('-')[0])
    
    end_date_month = pd.to_numeric(end_date.split('-')[1])
    start_date_month = pd.to_numeric(start_date.split('-')[1])
    
    return (end_date_year - start_date_year) * 12 + end_date_month - start_date_month


months= diff_month(df_copy['Date'].tail(1).to_string(index=False),df_copy['Date'].head(1).to_string(index=False)) + 1

monthly_average = (total/months).astype(int)

def generate_month_card_content(card_header,card_value):    
    card_body = dbc.CardBody(
        [
            html.H5(f"{(card_header)}", 
                    className="card-title",
                    style={'textAlign':'center','fontSize':'150%'}),
            html.P(f"{int(card_value):,}", 
                   className="card-text",
                   style={'textAlign':'center','fontSize':'200%'}),
        ]
    )
    card = [card_body]
    return card

def generate_card_content(card_header,card_value):    
    card_body = dbc.CardBody(
        [
            html.H5(f"{(card_header)}", 
                    className="card-title",
                    style={'textAlign':'center','fontSize':'120%','color': '#ccc'}),
            html.P(f"{int(card_value):,}", 
                   className="card-text",
                   style={'textAlign':'center','fontSize':'150%','color': '#2cfec1'}),
        ],
    )
    card = [card_body]
    return card

# remove unavailable dates in the list
new_list= []

def trial(start_date, end_date):
    dates_list = pd.date_range(start_date,end_date).strftime('%Y-%m-%d').tolist()
    for date in dates_list:
        try : 
            df_copy['Date'].to_string(index=False).split('\n').index(date)
            res="Element found" 
            new_list.append(date)
        except ValueError :
            res="Element not found"
            
    return new_list


# Build App
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# for heroku
server = app.server

# colors being used
colors = {
    'background':'#1f2630',
    'card_color':  '#252e3f',
    'card_text': '#2cfec1',
    'text_color': '#7fafdf',
    'highlight_color':'#2cfec1' 
}
#Initialise month dropdown options
months_unique = df_copy.Month.unique()
months_all_2 = [
    {'label' : i, 'value' : i} for i in months_unique
    ]
months_all_1 = [{'label' : '(Select All)', 'value' : 'All'}]
months_all = months_all_1 + months_all_2

#Initialise month dropdown options
years_unique = df_copy.Year.unique()
years_all_2 = [
    {'label' : i, 'value' : i} for i in years_unique
    ]
years_all_1 = [{'label' : '(Select All)', 'value' : 'All'}]
years_all = years_all_1 + years_all_2

#Initialise Group description dropdown options
gd_group = df_copy["Group Description"].unique()
gd_group_all_2 = [
    {'label' : i, 'value' : i} for i in sorted(gd_group)
    ]
gd_group_all_1 = [{'label' : '(Select All)', 'value' : 'All'}]
gd_group_all = gd_group_all_1 + gd_group_all_2

#Initialise suppliers dropdown options
supplier_group = df_copy.Supplier.unique()
supplier_group_all_2 = [
    {'label' : i, 'value' : i} for i in sorted(supplier_group)
    ]
supplier_group_all_1 = [{'label' : '(Select All)', 'value' : ''}]
supplier_group_all = supplier_group_all_1 + supplier_group_all_2

combined = {}

for group_desc in gd_group:
    category_df = df_copy.loc[(df_copy['Group Description'] == group_desc)]
    supplier = category_df['Supplier'].unique()
    combined[group_desc] = supplier

app.layout = html.Div([
    dbc.Row(
        html.H1('Dashboard',
                    style = { 'color': colors['text_color'], 'fontWeight': '100'}
            ),
        className='d-flex justify-content-center',
        style = {'height' : '1%'}
    ),     
        dbc.Row([
                    html.Div(dcc.Dropdown(
                            id='months-dropdown',
                            options=months_all,
                            value=[],
                            placeholder="Month",
                            multi=True,
                            style= {
                                'background':colors['background'],
                                            }
                                     )),
                    html.Div(dcc.Dropdown(
                            id='years-dropdown',
                            options= years_all,
                            value=[],
                            placeholder="Year",
                            multi=True,                                   
                            style= {
                                 'background':colors['background'], 
                                            }
                                    )),
                    html.Div(dcc.DatePickerRange(
                            id='daterange-picker',
                            min_date_allowed=df_copy['Date'].head(1).to_string(index=False).strip(),
                            max_date_allowed=df_copy['Date'].tail(1).to_string(index=False).strip(),
                            initial_visible_month=df_copy['Date'].tail(1).to_string(index=False),
                            clearable=True,
                            minimum_nights=1,
                            start_date_placeholder_text="Start Date",
                            end_date_placeholder_text="End Date",
                            updatemode='bothdates',
                            style= {
                                    'height': '34px',
                                    'background':colors['background'] 
                                     }
                            ))
                    ],
              className='d-flex justify-content-center pt-3 pb-3',id='filters', style={'height': '1%'}),
        dbc.Row([
            dbc.Col(dbc.Card(generate_card_content("Total Spend", total),
                             style={"backgroundColor":colors['card_color'], 'borderRadius':'16px'},
                             inverse=True),  width=2),
           dbc.Col(dbc.Card(generate_card_content("Monthly Average", monthly_average),
                             style={"backgroundColor":colors['card_color'], 'borderRadius':'16px'},
                             inverse=True),  width=2),
            dbc.Col(id="month_spend", width=2)
        ], className="d-flex justify-content-center mb-3 ", style={'height': '2%'}),
        dbc.Row([ 
            dbc.Col([
                   
              dbc.Card(dbc.CardBody(dcc.Graph(id='graph')), 
                       className="pt-5 mt-5",
                       style={"backgroundColor":'inherit','border':'0'}), 
               ],className='mr-2', style={'backgroundColor':colors['card_color']}, width=5),
              dbc.Col([
                  html.Div([
                        html.Div(
                                    dcc.Dropdown(
                                        id='groupdesc-dropdown',
                                        options=gd_group_all,
                                        value=[],
                                        placeholder="Group Description",
                                        multi=True,
                                        style= {
                                                'background':colors['card_color'], 
                                                }
                                        ), 
                        style = { 'margin-top' : '5px'}   
                        ),
                        html.Div(
                                    dcc.Dropdown(
                                        id='suppliers-dropdown',
                                        options=supplier_group_all,
                                        value=[],
                                        placeholder="Supplier",
                                        multi=True,
                                        style= {
                                                'background':colors['card_color'], 
                                                }
                                        ), 
                        style = { 'margin-top' : '5px'}   
                    )], className='d-flex flex-column ', style = {'height' : '90px'} ),
                    dbc.Card(dbc.CardBody(dcc.Graph(id='suppliers_bar_chart')), 
                       className="pb-5",
                       style={"backgroundColor":'inherit','border':'0'}),
                ],className="ml-2 pt-3", style={'backgroundColor':colors['card_color']}, width=5)
        ], className="d-flex justify-content-center", style={'height': '48%'}),
           dbc.Row(
               dbc.Col(
                        dbc.Card(dbc.CardBody(dcc.Graph(id='weekly_spend_bar_chart', figure = weekly_chart_figure)), 
                        className="pt-5",
                        style={"backgroundColor":'inherit','border':'0'}),
                    className="mt-3 p-3",
                    width=11, 
                    style={'backgroundColor':colors['card_color'],'height': '48%', }
               ),
                # style={ 'width': '960px'},
               className="d-flex justify-content-center ml-5 mr-5"         
                  )
 ], className='wrapper' )
#style={'backgroundColor': colors['background']}
# #Define callback to update graph


@app.callback(
    Output('graph', 'figure'),
    [ Input('daterange-picker', 'start_date'),
      Input('daterange-picker', 'end_date'),
      Input('months-dropdown', 'value'),
      Input('years-dropdown', 'value')]
)
    
def update_chart(start_date,end_date,months_value,years_value):
    dff = df_copy
    
    isselect_all_months = 'Start' #Initialize isselect_all
    isselect_all_years = 'Start' #Initialize isselect_all
    
    if start_date and end_date is not None:
        # clearlist
        new_list.clear()
        # find dates not in the date
        trial(start_date,end_date)
 #       filter rows by dates
        initial_df= dff[dff['Date'].isin(new_list)]
      
    else:
        initial_df = dff
        
        
         ## months selection 
    for i in months_value:
        if i == 'All' or i == '':
            isselect_all_months = 'Y'
            break
        elif i != '':
            isselect_all_months = 'N'
        else:
            pass
        
    if isselect_all_months == 'N':
        months_df = initial_df[initial_df['Month'].isin(months_value)]     
    else: 
        months_df = initial_df
        
     ## years selection 
    for i in years_value:
        if i == 'All' or i == '':
            isselect_all_years = 'Y'
            break
        elif i != '':
            isselect_all_years = 'N'
        else:
            pass
        
    if isselect_all_years == 'N':
        years_df = months_df[months_df['Year'].isin(years_value)]     
    else: 
        years_df  = months_df    
    
#        get the total costs for the month, sort and get top ten
    final_df_sum= years_df["Cost"].groupby(years_df["Group Description"]).sum().to_frame(name="Sum").reset_index().sort_values(by='Sum', ascending=False).head(10)
    figure= px.pie(
            final_df_sum, 
            values='Sum',
            names='Group Description',
            title='Monthly Spend'
          )
    figure.update_traces(textposition='inside', textinfo='percent+label')
    figure.update_layout(uniformtext_minsize=12, 
                         uniformtext_mode='hide', 
                         title_font_color="#2cfec1", 
                         legend_font_color="#2cfec1", 
                         legend_font_size=10, 
                         margin=dict(t=75, b=75, l=75, r=75),
                         plot_bgcolor= '#1f2630', 
                         paper_bgcolor= '#1f2630',)
    return figure


@app.callback(
    Output('month_spend', 'children'),
    [ Input('months-dropdown', 'value'),
    Input('daterange-picker', 'start_date'),
    Input('daterange-picker', 'end_date')]
)

def update_card(months_value, start_date, end_date):
     dff= df_copy
     
     latest_month = dff['Month'].tail(1).to_string(index=False).strip()
     
     isselect_all_months = 'Start' #Initialize isselect_all
     
     if start_date and end_date is not None:
         # clearlist
        new_list.clear()
         # find dates not in the date
        trial(start_date,end_date)
 #       filter rows by dates
        initial_df= dff[dff['Date'].isin(new_list)]

        total_df= initial_df["Cost"].sum()

    #    return dbc.Card(generate_card_content("Range Spend", total_df), style={"backgroundColor":colors['card_color'], 'borderRadius':'16px'}, inverse=True)
     else: 
         initial_df = dff
         
        
     for i in months_value:
        if i == 'All' or i == '':
            isselect_all_months = 'Y'
            break
        elif i != '':
            isselect_all_months = 'N'
        else:
            pass

     if isselect_all_months == 'N':
        selected_df= initial_df[initial_df['Month'].isin(months_value)] 
        total_df = selected_df["Cost"].sum() 
        return dbc.Card(generate_card_content("Range Spend", total_df), style={"backgroundColor":colors['card_color'], 'borderRadius':'16px'}, inverse=True) 
          
     else: 
        selected_df = initial_df[initial_df['Month'] == latest_month]
        total_df = selected_df["Cost"].sum()
        return dbc.Card(generate_card_content(f"{(latest_month)} Spend", total_df), style={"backgroundColor":colors['card_color'], 'borderRadius':'16px'}, inverse=True)

     
        

 
@app.callback(
    Output('suppliers-dropdown', 'options'),
    [Input('groupdesc-dropdown', 'value')])
 
def suppliers_dropdown(groupdesc_dropdown):
    isselect_all = 'Start' #Initialize isselect_all
        
    #Rembember that the dropdown value is a list !
    for i in groupdesc_dropdown:
        if i == 'All' or i == '':
            isselect_all = 'Y'
            break
        elif i != '':
            isselect_all = 'N'
        else:
            pass
    #Create options for individual selections
    if isselect_all =='N':
        options_0 = []
        for i in groupdesc_dropdown:
            options_0.append(combined[i])
        options_1 = [] # Extract string of string
        for i1 in options_0:
            for i2 in i1:
                options_1.append(i2)
        options_list = [] # Get unique values from the string
        for i in options_1:
            if i not in options_list:
                options_list.append(i)
            else:
                pass
        options_final_1 = [
            {'label' : k, 'value' : k} for k in sorted(options_list)]
        options_final_0 = [{'label' : '(Select All)', 'value' : 'All'}]
        options_final = options_final_0 + options_final_1
    #Create options for select all or none
    else:
        options_final_1 = [
            {'label' : k, 'value' : k} for k in sorted(supplier_group)]
        options_final_0 = [{'label' : '(Select All)', 'value' : 'All'}]
        options_final = options_final_0 + options_final_1

    return options_final
       
@app.callback(
    Output('suppliers_bar_chart', 'figure'),
    [ Input('groupdesc-dropdown', 'value'),
      Input('suppliers-dropdown', 'value'),
      Input('months-dropdown', 'value'),
      Input('years-dropdown', 'value'),
       Input('daterange-picker', 'start_date'),
      Input('daterange-picker', 'end_date')]
)


def update_graph(groupdesc_value, suppliers_value, months_value, years_value,start_date,end_date):
    dff= df_copy
    
     # Filter based on the dropdowns
    isselect_all_groupdesc = 'Start' #Initialize isselect_all
    isselect_all_suppliers = 'Start' #Initialize isselect_all
    isselect_all_months = 'Start' #Initialize isselect_all
    isselect_all_years = 'Start' #Initialize isselect_all
    
    if start_date and end_date is not None:
         # clearlist
        new_list.clear()
         # find dates not in the date
        trial(start_date,end_date)
        #  filter rows by dates
        initial_df= dff[dff['Date'].isin(new_list)]

    else: 
        initial_df = dff
    
    
    # L1 selection 
    for i in groupdesc_value:
        if i == 'All' or i == '':
            isselect_all_groupdesc = 'Y'
            break
        elif i != '':
            isselect_all_groupdesc = 'N'
        else:
            pass
    
     # Filter df according to selection
    if isselect_all_groupdesc == 'N':
        new_df_category =  initial_df[initial_df['Group Description'].isin(groupdesc_value)]
       
    else:
         new_df_category = initial_df
            
     ## supplier selection (dropdown value is a list!)
    for i in suppliers_value:
        if i == 'All' or i == '':
            isselect_all_suppliers = 'Y'
            break
        elif i != '':
            isselect_all_suppliers = 'N'
        else:
            pass
        
    if isselect_all_suppliers == 'N':
        new_df_2 = new_df_category[new_df_category['Supplier'].isin(suppliers_value)]     
    else: 
        new_df_2 = new_df_category
        
     ## months selection 
    for i in months_value:
        if i == 'All' or i == '':
            isselect_all_months = 'Y'
            break
        elif i != '':
            isselect_all_months = 'N'
        else:
            pass
        
    if isselect_all_months == 'N':
        months_df = new_df_2[new_df_2['Month'].isin(months_value)]     
    else: 
        months_df = new_df_2
        
     ## years selection 
    for i in years_value:
        if i == 'All' or i == '':
            isselect_all_years = 'Y'
            break
        elif i != '':
            isselect_all_years = 'N'
        else:
            pass
        
    if isselect_all_years == 'N':
        years_df = months_df[months_df['Year'].isin(years_value)]     
    else: 
        years_df  = months_df    
    

        
    final_df_sum = years_df['Cost'].groupby(years_df['Supplier']).sum().to_frame(name ="Sum").reset_index().sort_values(by='Sum', ascending=False).head(15)
   
    figure = px.bar(
             final_df_sum, 
            x='Sum',
            y='Supplier',
            title="Supplier",
            orientation= 'h',
            barmode="group",
            text='Sum'
            )
    
    figure.update_layout(
                            plot_bgcolor= '#1f2630', 
                            paper_bgcolor= '#1f2630',
                            yaxis=dict(
                            autorange="reversed",
                            showgrid=False,
                            showline=False,
                            zeroline=True,
                            showticklabels=True,
                            # domain=[0, 0.85],
                        ),
                        xaxis=dict(
                            dtick= 5000,
                            zeroline=True,
                            showline=False,
                            showticklabels=True,
                            showgrid=True,
                            gridcolor= "#252e3f",
                            gridwidth= 0.02,
                            zerolinecolor= "#252e3f"
                            # domain=[0, 0.42],
                        ),
                        font=dict(
                                size=10,
                                color='#2cfec1'
                            ),
                        legend=dict(x=0.029, y=1.038, font_size=10),
                        margin=dict(l=100, r=20, t=70, b=70),
    )
    return figure


    
# Run app and display result inline in the notebook 
if __name__ == '__main__':
     app.run_server(debug=True)
    
