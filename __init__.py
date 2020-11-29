"""
Loan Calculator

@author: Shuhui
"""

import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc 
import navbar
import Helper
import Loan
import LoanPortfolio
import dash_table
import numpy as np
import plotly.graph_objects as go
import calendar
import LoanImpacts


##################################  dashboard page  #################################
bs = "https://stackpath.bootstrapcdn.com/bootswatch/4.5.2/litera/bootstrap.min.css"
app = dash.Dash(__name__, external_stylesheets=[bs])
sercer = app.server
names = ['Payment Number', 'Begin Principal', 'Payment', 'Extra Payment',
         'Applied Principal', 'Applied Interest', 'End Principal']

# input formgroup
loan_amount = dbc.FormGroup([
            dbc.Label("Loan Amount"),
            dbc.Input(id='loan_amount',type='number',min=1000,step=1),
            dbc.FormText("Please type the loan amount no less than $1000")
        ])
payment = dbc.FormGroup([
            dbc.Label("Loan Monthly Payment"),
            dbc.Input(id='payment',type='number',min=1,step=1,disabled=True),
            dbc.Fade(html.P("Invalid loan payment", style={'color':'red','size':1}),
                    id='fade',is_in=False,appear=False)
        ])
interest = dbc.FormGroup([
            dbc.Label("Loan Interest rate %"),
            dbc.Input(id='interest',type='number',min=1,max=99,step=0.1,disabled=True)
        ])
extra_payment = dbc.FormGroup([
            dbc.Label("Extra Payment(monthly)"),
            dbc.Input(id='ext_pay',type='number',disabled=True)
        ])
tab_1 = dbc.Card(dbc.CardBody([
            html.H6("Your Amortization Schedule is here:", className="card-title"),
            html.Div(id='schedule')
        ]),style={'width':'58rem'})
tab_2 = dbc.Card(dbc.CardBody([
            html.H6("Amortization Schedule Plot", className="card-title"),
            html.Div(id='plot')
        ]),style={'width':'58rem'})
tab_3 = dbc.Card(dbc.CardBody([
            html.H6("Estimated Loan End Date", className="card-title"),
            html.P("Please enter your loan start date."),
            html.Div(dcc.DatePickerSingle(id="date",month_format='MMMM,YY',
                                          display_format='MMMM,YY',
                                          placeholder='Month,Year',clearable=True
                                          )),
            html.Br(),
            html.Div(id='end_date')
        ]),style={'width':'58rem'})
tab_4 = dbc.Card(dbc.CardBody([
            html.H6("Extra Payment Contribution", className="card-title"),
            html.P("If you have multi extra payments(one time), please input extra payments: "),
            html.Div(id='ext_input',children=[
                        dcc.Input(id='input1',type='number',
                                  placeholder="Extra Payment 1",
                                  style={'width':'10rem'}),
                        dcc.Input(id='input2',type='number',
                                  placeholder="Extra Payment 2",
                                  style={'width':'10rem'}),
                        dcc.Input(id='input3',type='number',
                                  placeholder="Extra Payment 3",
                                  style={'width':'10rem'}),
                        dcc.Input(id='input4',type='number',
                                  placeholder="Extra Payment 4",
                                  style={'width':'10rem'}),
                        dcc.Input(id='input5',type='number',
                                  placeholder="Extra Payment 5",
                                  style={'width':'10rem'}),
                        dbc.Button("Submit", id='submit',
                                   outline=True, color="success",className="mr-1"),
                    ]),
            
            html.Br(),
            html.Div(id='ext_impact')
        ]))
tabs = dbc.Tabs([dbc.Tab(tab_1,label='Amortization Schedule',
                         style={'height':'200px'}),
                 dbc.Tab(tab_2,label='Amortization Schedule Plot',
                         style={'height':'200px'}),
                 dbc.Tab(tab_3,label='Loan Period',
                         style={'height':'200px'}),
                 dbc.Tab(tab_4,label='Extra Payment Contribution',
                         style={'height':'200px'})]
                 )

app.layout = html.Div([
        navbar.Navbar(),
        dbc.Row(dbc.Col(html.Br())),
        dbc.Row(dbc.Col(html.H2("Loan Calculator"),width={"offset":1})),
        dbc.Row(dbc.Col(html.P("This calculator will help you determine the monthly\
                               payments on a loan. Also, you can add any extra\
                               payments into the calculation."),width={"offset":1})),
        dbc.Row(dbc.Col(html.Hr())),
        dbc.Row([dbc.Col([dbc.Form([loan_amount,payment,interest,extra_payment]),
                          dbc.Button("Apply Extra Payment",
                                     id='ext_button',outline=True,
                                     color="secondary",className="mr-1"),
                          html.Br(),
                          html.Br(),
                          dbc.Button("Get Start",id='button',outline=True,
                                   color="primary",className="mr-1")
                          ],width={"offset":1}),
                 dbc.Col(tabs)]),
        dbc.Row(dbc.Col(html.Br())),
        dbc.Row(dbc.Col(html.Br())),
        dbc.Row(dbc.Col(html.Br()))
  ])




# loan amount invalid
@app.callback(
        [Output("payment","disabled"),
         Output("interest","disabled")],
        [Input("loan_amount","value")]
        )
def valid_change(loan):
    if (loan>=1000)==True & (loan%1==0)==True:
        return False, False
    else:
        return True, True
# loan payment invalid
@app.callback(
        Output("fade","is_in"),
        [Input("payment","value"),
         Input("loan_amount","value")]
        )
def valid_payment(payment,loan):
    if payment > loan:
        return True
    if payment%1 != 0:
        return True

# loan amortization table
@app.callback(
         Output('schedule','children'),
        [Input("button","n_clicks")],
        [State("loan_amount","value"),
         State("payment","value"),
         State("interest","value"),
         State("ext_pay","value")]
        )
def create_table(n_click,principal,payment,rate,ext_pay):
    loans = LoanPortfolio.LoanPortfolio()
    if ext_pay is None:
        loan = Loan.Loan(principal=principal, rate=rate, 
                         payment=payment, extra_payment=0)
    else:
        loan = Loan.Loan(principal=principal, rate=rate, 
                         payment=payment, extra_payment=ext_pay)
    loan.check_loan_parameters()
    loan.compute_schedule()
    
    loans.add_loan(loan)
    helper = Helper.Helper()
    table = helper.print_df(loan)
    
    if loans.get_loan_count() == 3:
        loans.aggregate()
        helper = Helper.Helper()
        table = helper.print_df(loans)

    temp = dash_table.DataTable(
                data=table.to_dict("records"),
                columns=[{'id': c, 'name': c} for c in table.columns],
                style_cell={'textAlign': 'center'},
                style_as_list_view=True,
                style_header={'backgroundColor': '#E9DADA','fontWeight': 'bold'},
                style_table={'height': '400px', 'overflowY': 'auto'}
            )
    
    return temp
        

# enable extra payment
@app.callback(
        Output('ext_pay','disabled'),
        [Input('ext_button','n_clicks')]
        )
def enable_extra(n_click):
    if n_click is None:
        return True
    else:
        return False
    
# create plot
@app.callback(
        Output('plot','children'),
        [Input("button","n_clicks")],
        [State("loan_amount","value"),
         State("payment","value"),
         State("interest","value"),
         State("ext_pay","value")]
        )
def plot(n_click,principal,payment,rate,ext_pay):
    if ext_pay is None:
        loan = Loan.Loan(principal=principal, rate=rate, 
                         payment=payment, extra_payment=0)
    else:
        loan = Loan.Loan(principal=principal, rate=rate, 
                         payment=payment, extra_payment=ext_pay)
        
    loan.check_loan_parameters()
    loan.compute_schedule()
    
    payment_number, applied_ext, applied_principal, applied_interest, end_principal = [], [], [], [], []

    for pay in loan.schedule.values():
        payment_number.append(pay[0])
        applied_ext.append(pay[3])
        applied_principal.append(pay[4])
        applied_interest.append(pay[5])
        end_principal.append(pay[6])
    
    ind = np.arange(1,len(payment_number)+1)
    
    fig = go.Figure(data=[
            go.Bar(name="Principal",x=ind,y=applied_principal,
                   hovertemplate="Principal:%{y:$.2f}",marker_color="#92A8D1"),
            go.Bar(name="Extra Payment",x=ind,y=applied_ext,
                   hovertemplate="Extra Payment:%{y:$.2f}",marker_color="#8FBC8F"),
            go.Bar(name="Interest",x=ind,y=applied_interest,
                   hovertemplate="Interest:%{y:$.2f}",marker_color="#DEB887")
            ])
    fig.update_layout(barmode='stack',
                  yaxis=dict(title='$ USD',titlefont_size=16,tickfont_size=14),
                  xaxis=dict(title='Payment Period'))
    fig.update_layout(barmode='stack',
                      yaxis=dict(title='$ USD',titlefont_size=16,tickfont_size=14),
                      xaxis=dict(title='Payment Period'))
    return dcc.Graph(figure=fig)

# date estimation
@app.callback(
        Output('end_date','children'),
        [Input("loan_amount","value"),
         Input("payment","value"),
         Input("interest","value"),
         Input("ext_pay","value"),
         Input("date","date")]
        )
def end_date(principal,payment,rate,ext_pay,date_value):
    
    loans = LoanPortfolio.LoanPortfolio()
    if ext_pay is None:
        loan = Loan.Loan(principal=principal, rate=rate, 
                         payment=payment, extra_payment=0)
    else:
        loan = Loan.Loan(principal=principal, rate=rate, 
                         payment=payment, extra_payment=ext_pay)
    loan.check_loan_parameters()
    loan.compute_schedule()
    
    loans.add_loan(loan)
    helper = Helper.Helper()
    table = helper.print_df(loan)
    
    if loans.get_loan_count() == 3:
        loans.aggregate()
        helper = Helper.Helper()
        table = helper.print_df(loans)
        
    period = table.shape[0]
    year = int(date_value[:4])
    month = int(date_value[5:7])
    for i in range(period):
        if month == 12:
            year += 1
            month = 1
        else:
            month += 1
            
    month = calendar.month_name[month]
    end_date = "Your estimated loan end date is {},{}".format(month,year)
    
    return end_date

# number of extra payments
@app.callback(
        Output('ext_impact','children'),
        [Input('submit','n_clicks')],
        [State('input1','value'),
         State('input2','value'),
         State('input3','value'),
         State('input4','value'),
         State('input5','value'),
         State("loan_amount","value"),
         State("payment","value"),
         State("interest","value"),
         State("ext_pay","value"),
         ]
        )
def ext_impact(n_clicks,input1,input2,input3,input4,input5,
               principal,payment,rate,ext_pay):
    list = []
    if input1 is not None:
        list.append(input1)
    if input2 is not None:
        list.append(input2)
    if input3 is not None:
        list.append(input3)
    if input4 is not None:
        list.append(input4)
    if input5 is not None:
        list.append(input5)
    
    if ext_pay is None:
        loan = LoanImpacts.LoanImpacts(principal=principal, rate=rate, payment=payment,
                                       extra_payment=0,contributions=list)
    else:
        loan = LoanImpacts.LoanImpacts(principal=principal, rate=rate, payment=payment,
                                       extra_payment=ext_pay,contributions=list)
    
    table = loan.compute_impacts()
    
    temp = dash_table.DataTable(
                data=table.to_dict("records"),
                columns=[{'id': c, 'name': c} for c in table.columns],
                style_cell={'textAlign': 'center'},
                style_as_list_view=True,
                style_header={'backgroundColor': '#9AC39A','fontWeight': 'bold'},
                style_table={'height': '400px', 'overflowY': 'auto'}
            )
    
    return temp



if __name__ =='__main__':
    app.run_server(debug=False)