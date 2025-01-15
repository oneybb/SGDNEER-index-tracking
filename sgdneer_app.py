import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import pandas as pd
import numpy as np
import statsmodels.api as sm
import plotly.graph_objects as go

app = dash.Dash(__name__)

 
df = pd.read_excel("currency_merged.xlsx")
df['Average for Week Ending'] = pd.to_datetime(df['Average for Week Ending']).dt.date
merged_clean = df.dropna(subset=['Average for Week Ending', 'Deviation CTSGSGD', 'Deviation GSSGSGD'])
df_full = pd.read_excel("df.xlsx")
df_full['Average for Week Ending'] = pd.to_datetime(df_full['Average for Week Ending']).dt.date
#overall tracking errors
tracking_error_cts = round(np.std(merged_clean['Deviation CTSGSGD']), 6)
tracking_error_gss = round(np.std(merged_clean['Deviation GSSGSGD']), 6)


#comparisom plot
 
fig_comparison = go.Figure()

# Official Index line
fig_comparison.add_trace(go.Scatter(
    x=df_full['Average for Week Ending'],
    y=df_full['Official'],
    mode='lines',
    name='Official Index'
))

#GSSGSGD  
fig_comparison.add_trace(go.Scatter(
    x=df_full['Average for Week Ending'],
    y=df_full['GSSGSGD'],
    mode='lines',
    name='GSSGSGD Index'
))

#add CTSGSGD  
fig_comparison.add_trace(go.Scatter(
    x=df_full['Average for Week Ending'],
    y=df_full['CTSGSGD'],
    mode='lines',
    name='CTSGSGD Index'
))

fig_comparison.update_layout(
    title='Comparison of Official Index and Custom Indices (GSSGSGD, CTSGSGD)',
    xaxis_title='Date',
    yaxis_title='Index Value',
    legend_title='Index',
    template='plotly_white',
    xaxis=dict(tickangle=45),
    height=600
)

#OLS
X = df[['USD', 'EUR', 'JPY', 'CNY','MYR','IDR']]
X = sm.add_constant(X)  # Constant for the intercept

#OLS for CT
y_cts = df['Deviation CTSGSGD']
model_cts = sm.OLS(y_cts, X).fit()

#OLS GS
y_gss = df['Deviation GSSGSGD']
model_gss = sm.OLS(y_gss, X).fit()

app.layout = html.Div([
    html.H1("SGDNEER Tracking Analysis", style={'text-align': 'center', 'font-family': 'Arial', 'color': '#003366'}),
    html.P("This dashboard analyzes the performance of custom indices developed by Citi and Goldman in tracking the official Singapore Dollar Nominal Effective Exchange Rate (SGD NEER) published by Monetary Authority of Singapore (MAS). The SGD NEER is a key monetary policy tool that measures the value of the SGD against a basket of currencies. While the official index is published weekly and its weightage is undisclosed, the custom indices are updated daily, providing higher-frequency insights into currency movements and exchange rate trends."
            ,  style={'font-family': 'Arial'}),
    html.P("Accurate tracking thus becomes important as it supports economic analysis, risk management, and decision-making for market participants. Understanding the discrepancies is essential for improving the accuracy and usability of the custom indices."
            ,  style={'font-family': 'Arial'}),
    html.P("This study evaluates the tracking performance of the custom indices using key metrics such as deviation (the difference in returns between the indices) and tracking error (the volatility of these differences over time). It also examines potential factors causing tracking errors, such as weightage differences, policy changes, and data collections. "
            ,  style={'font-family': 'Arial'}),
    # Tracking dataframe 
    html.Div([
        html.H3("Index Tracking:", style={'font-family': 'Arial', 'color': '#003366'}),
        
        # Tracking Table
        html.Div([
            html.Table([
             
                html.Tr([
                    html.Th(col, style={'padding': '10px', 'text-align': 'center'}) 
                    for col in ['Average for Week Ending', 'Official', 'CTSGSGD', 'GSSGSGD']
                ]),  
                
    
                *[html.Tr([
                    html.Td(row[col], style={'padding': '10px', 'text-align': 'center'}) 
                    for col in ['Average for Week Ending', 'Official', 'CTSGSGD', 'GSSGSGD']
                ]) for index, row in df_full.iterrows()]  
            ], style={
                'width': '100%',
                'border': '1px solid #ddd',
                'border-collapse': 'collapse',
                'margin': '20px 0',
                'font-family': 'Arial',
                'overflowY': 'auto',
                'maxHeight': '400px',
                'display': 'block'
            })
        ]),

        #Comparison Plot Section
        html.H3("Comparison of the Official MAS SGD NEER with the GSSGSGD and CTSGSGD indices."),
        dcc.Graph(
            id='comparison-plot',
            figure=fig_comparison
        ),
        html.P("Although this chart shows that the GS index consistently underestimates the actual index values while the Citi index tends to overestimate them most of the time, the nominal difference between the actual index and the tracked indices is less critical. What matters more is tracking the deviation in index returns, as this reflects how accurately the custom indices capture the relative movements or changes in the underlying SGD NEER over time. Focusing on the deviation in returns provides insights into whether the indices are effectively capturing trend alignments and short-term fluctuations, which are crucial for risk management, economic analysis, and decision-making. Even if the absolute level of the indices differs, as long as the custom indices move in tandem with the official index, they remain useful for tracking directional trends and analyzing market dynamics. This aspect of the analysis will be explored in detail below.",style={'font-family': 'Arial'}),
    ], style={'padding': '20px', 'background-color': '#f4f4f9'}),

    #dropdown to select index
    html.Div([
        html.Label('Select Index:', style={'font-family': 'Arial', 'color': '#003366'}),
        dcc.Dropdown(
            id='deviation-dropdown',
            options=[
                {'label': 'CTSGSGD', 'value': 'CTSGSGD'},
                {'label': 'GSSGSGD', 'value': 'GSSGSGD'}
            ],
            value='CTSGSGD',   
            style={'width': '50%', 'margin': '10px'}
        ),
    ], style={'padding': '20px', 'background-color': '#f4f4f9'}),

    #OLS summaries
    html.Div([
        html.H3("Weightage Difference between Indices:", style={'font-family': 'Arial', 'color': '#003366'}),
        html.P("Since the exact weightings of the currencies in both indices are unknown, an OLS regression can help identify whether there are differences in how the indices respond to currency fluctuations. It can reveal if certain currencies play a key role in explaining the discrepancies between the custom and official indices. If there is a mismatch between the weightage of custom index and official index, the difference in indices should be more sensitive to a particular currency and the coefficient for that currency in the regression would likely be larger or more significant. By analyzing the coefficients and statistical significance, currencies that have the most influence on the deviation between the indices can be identified, potentially highlighting differences in how the indices are constructed or updated.."
        , style={'font-family': 'Arial'}),
        html.P("Dependent variable : Deviation between official index returns and Custom index returns"
        , style={'font-family': 'Arial'}),
        html.P("Independent variable: Currency returns (USD, EUR, JPY, CNY, etc.)."
        , style={'font-family': 'Arial'}),
        html.Pre(id='ols-summary', style={'font-family': 'Courier New', 'background-color': '#f9f9f9', 'padding': '15px', 'border': '1px solid #ddd'}),
        html.Div(id='ols-comment', style={'font-family': 'Arial', 'color': '#003366', 'margin-top': '10px', 'white-space': 'pre-line'}),
    ], style={'padding': '20px', 'background-color': '#f4f4f9'}),
    
    # Deviation plot
    html.Div([
        html.H3("Deviation:", style={'font-family': 'Arial', 'color': '#003366'}),
        dcc.Graph(id='interactive-plot'),
        html.Div(id='deviation-comment', style={'font-family': 'Arial', 'color': '#003366', 'margin-top': '10px', 'white-space': 'pre-line'}),
    ], style={'padding': '20px', 'background-color': '#f4f4f9'}),

    
    #Tracking error plot
    html.Div([
        html.H3("Tracking Errors:", style={'font-family': 'Arial', 'color': '#003366'}),
        dcc.Graph(id='monthly-tracking-error-plot'),
        html.P(id='tracking-error', children=f"Tracking Error over the whole period for CTSGSGD: {tracking_error_cts:.6f}", style={'font-family': 'Arial'}),
        html.Div(id='tracking-error-comment', style={'font-family': 'Arial', 'color': '#003366', 'margin-top': '10px', 'white-space': 'pre-line'}),
    ], style={'padding': '20px', 'background-color': '#f4f4f9'}),


    #Conclusion
    html.Div([
        html.H3("Conclusion:", style={'font-family': 'Arial', 'color': '#003366'}),
        html.Div(id='conclusion', style={'font-family': 'Arial', 'color': '#003366', 'margin-top': '10px', 'white-space': 'pre-line'}),
    ], style={'padding': '20px', 'background-color': '#f4f4f9'}),


])

#callback to update the interactive plot, tracking error, and OLS summary based on dropdown selection
@app.callback(
    [Output('interactive-plot', 'figure'),
     Output('tracking-error', 'children'),
     Output('ols-summary', 'children'),
     Output('monthly-tracking-error-plot', 'figure'),
     Output('deviation-comment', 'children'),
     Output('tracking-error-comment', 'children'),
     Output('ols-comment', 'children'),
     Output('conclusion', 'children')],
    [Input('deviation-dropdown', 'value')]
)
def update_content(selected_deviation):
    """
    This function updates the content based on the selected deviation index (CTSGSGD or GSSGSGD).
    The content includes:
    - Deviation Plot for the selected index
    - Tracking Error for the selected index (including monthly tracking error)
    - OLS regression summary for the selected index
    -conclusion of each index
    
    The data used for plotting and regression is cleaned and preprocessed data of currency indices.
    """
    
    if selected_deviation == 'CTSGSGD':
        y_data = merged_clean['Deviation CTSGSGD']
        tracking_error = tracking_error_cts
        ols_summary = model_cts.summary().as_text()
        name = 'CTSGSGD'
        deviation_comment = """
        *Deviation is calculated by the difference between Official index return and Custom index return ,i.e. official index return - custom index return
        This provides an insight into a more spotaneous performance in discrepancy between the two indices on a weekly basis.
        
        Most data points are close to zero, with in the band of +-0.1%, indicating the Citi index generally tracks the MAS NEER well over time. The error fluctuate around zero, implies that Citi index is unbiased in its tracking as it does not systematically deviate in one direction
        The constant small noise could be due to differences in data source, sampling timing etc. Each index may rely on different sources of data or even different methodologies to interpret the data. For example, one index might use spot exchange rates while another might use forward exchange rates or trade-weighted averages. These different approaches to data collection and calculation can contribute to constant discrepancies between the indices
        
        Obervations:
        1. Deviation in May 2022
        Both the Citi and Goldman indices experienced significant deviations in May 2022, suggesting a common external factor or structural shift affecting both indices simultaneously. One possible explanation could be MAS Policy Shift.In April 2022, MAS tightened its monetary policy by increasing the slope of the SGD NEER policy band to allow for a faster appreciation of the SGD, aimed at combating inflation. Such a policy shift could include adjustments in the official SGD NEER, which the custom indices (Citi and Goldman) may have struggled to immediately replicate.
        Another guess would be sensitivity to USD Fluctuations. Since the OLS regression for the Citi index showed that USD returns have a significant positive coefficient (0.1413, p = 0.003), indicating that deviations are highly sensitive to USD movements. In May 2022, the USD was appreciating rapidly due to the Fed’s aggressive rate hikes, causing the SGD NEER to behave differently than expected. If the Citi index underestimated the USD relative to the official index, this could explain the spike in deviations.
        
        2. Sharp Peak and Trough in November 2022
        On November 2, 2022, the Federal Reserve announced its fourth consecutive 75 basis point interest rate increase, raising the federal funds rate to a target range of 3.75% to 4%. USD peaked after a prolonged period of strength, then began to decline as markets anticipated a potential slowdown in Fed rate hikes.The volatility in USD could be contributing to the changes in index

        3. Trough on March 24, 2023
        March 2023 saw significant financial market stress due to the collapse of Silicon Valley Bank (SVB) and concerns about Credit Suisse, which led to heightened risk aversion and safe-haven flows into the USD. The sudden appreciation of the USD likely caused fluctuations
        """

        tracking_error_comment = """
        Tracking error is calculated as the standard deviation of the difference between the official, Tracking Error=std(Official Index Return - Custom Index Return)
        This metric measures the volatility or variability of the differences between the returns of the official index and the custom index, rather than just the direct differences (deviation) at each point in time. 
        A lower tracking error indicates that the custom index closely and consistently tracks the official index, making it a more reliable tool for tracking purposes.
        
        The average tracking error over the period from Jan 2022 to Dec 2024 is relatively low at 0.000632, indicating that the Citi-tracked index generally follows the official MAS SGD NEER index closely with minimal long-term deviation and it could be a reliable tool to use for tracking.
        
        However, there are periods of increased tracking error, the spikes in tracking error in May 2022 and Dec 2022 period suggesting that the custom index may lag in adjusting to changes in the official MAS SGD NEER, following similar reasons in Deviaiton plot
        
        There is a upward trend in tracking error toward the end of 2024, which could signal the need to monitor the index more closely and potentially revise its methodology or rebalancing process to maintain tracking accuracy


        """
        ols_comment = """
        From the OLS summary, it can be seen that coefficient for USD is 0.1413 (p-value = 0.003) and it is significant. It indicates that deviations between the indices are sensitive to fluctuations in the USD. As the coefficient is positive, it means that when that currency’s return increases, the official index return exceeds the custom index return, resulting in positive deviation. This could be an indication that citi index underestimated the weightage of USD
        
        The IDR coefficient (-0.0651), though smaller, is notable due to its marginal significance. This could indicate that the IDR also plays a secondary role in contributing to the deviations.
        
        Other currencies like EUR, JPY, CNY, and MYR do not appear to significantly influence the deviations, suggesting that their weights or impacts are more closely aligned between the two indices.
        
        *Currencies with high correlation due to central bank policies and regional trade linkages are omitted to avoid high multicollinearity: HKD, TWD, KRW, THB, IDR, and PHP
        """

        conclusion = """
        The Citi-tracked index demonstrates strong overall performance in tracking the official MAS SGD NEER index. Most deviations are close to zero and fluctuate around zero, indicating that the Citi index is unbiased in its tracking and the tracking error over the period from January 2022 to December 2024 is relatively low at 0.0632%, reflecting a high degree of consistency and reliability in tracking the official index over the long term.
        
        However, small but consistent noise in the deviations can be attributed to differences in data sources, sampling timing, or data collection methodologies between the indices. The analysis also suggests that the Citi index may have underestimated the weightage of the USD, as spikes in deviation and volatility appear to coincide with periods of heightened USD fluctuations.
        
        To further improve the analysis, it will be more beneficial to have more detailed information about the custom index. For example, knowing the exact weights of the currencies in the custom index would allow a more precise understanding of how currency movements influence the deviations and knowing when and how the index rebalances its weights could also clarify spikes in tracking error

        Another improvement would be to understand how the formula of indices are constructed. The current analysis assumes the index is a linear combination of exchange rates. However, if the index is constructed differently (e.g., as a product of exchange rates or includes non-linear transformations), this assumption may not hold.In such cases, analyzing deviations might require transformations like natural logarithms or other forms of data manipulation to better reflect the relationship between the indices.
        """
        

    else:
        y_data = merged_clean['Deviation GSSGSGD']
        tracking_error = tracking_error_gss
        ols_summary = model_gss.summary().as_text()
        name = 'GSSGSGD'
        deviation_comment = """
        *Deviation is calculated by the difference between Official index return and Custom index return ,i.e. official index return - custom index return
        This provides an insight into a more spotaneous performance in discrepancy between the two indices on a weekly basis.
        
        Most data points are close to zero, with in the band of +-0.1%, indicating the index generally tracks the MAS NEER well over time. The error fluctuate around zero, implies that index is unbiased in its tracking as it does not systematically deviate in one direction
        The constant small noise could be due to differences in data source, sampling timing etc. Each index may rely on different sources of data or even different methodologies to interpret the data. For example, one index might use spot exchange rates while another might use forward exchange rates or trade-weighted averages. These different approaches to data collection and calculation can contribute to constant discrepancies between the indices
        
        Obervations:
        1. Deviation in May 2022
        Both the Citi and Goldman indices experienced significant deviations in May 2022, suggesting a common external factor or structural shift affecting both indices simultaneously. One possible explanation could be MAS Policy Shift.In April 2022, MAS tightened its monetary policy by increasing the slope of the SGD NEER policy band to allow for a faster appreciation of the SGD, aimed at combating inflation. Such a policy shift could include adjustments in the official SGD NEER, which the custom indices (Citi and Goldman) may have struggled to immediately replicate.
        2. Peaks in April and September 2024
        The cause of the deviations observed on April 5-12, 2024, and September 27, 2024, is unclear. However, it is evident that these deviations are not driven by USD fluctuations, as the Citi index, despite also having a significant USD weightage difference, does not exhibit similar fluctuations during these periods.

        """
        tracking_error_comment = """
        Tracking error for GSSGSGD is calculated as the standard deviation of the difference between the official, Tracking Error=std(Official Index Return - Custom Index Return)
        This metric measures the volatility or variability of the differences between the returns of the official index and the custom index, rather than just the direct differences (deviation) at each point in time. 
        A lower tracking error indicates that the custom index closely and consistently tracks the official index, making it a more reliable tool for tracking purposes.
        
        The tracking error chart for GSSGSGD shows that the Goldman index generally tracks the MAS SGD NEER closely, with a low overall tracking error of 0.0578%. This indicates strong alignment between the two indices under normal conditions and coud be a reliable tool to be used for tracking.

        However, notable spikes in tracking error occur in May and Dec 2022 due to similar reasons in Citi index, and in Apr 2024, Sep 2024, and Dec 2024, likely caused by external factors such as methodology rebalancing 
        
        """
        ols_comment = """
        R-squared value of 0.068 means that only 6.8 percent of the variance in the deviations is explained by the currency returns. This suggests that the model captures only a small portion of the factors driving the deviations, and other unmodeled factors (e.g., methodology differences, data sources, or rebalancing frequency) may play a larger role.

        The USD has a negative coefficient (-0.0781) and is marginally significant at the 10 percent level, meaning that when the USD strengthens (i.e., its returns increase), the Goldman index return is likely higher than the official return, implying an overestimation of weighting in USD

        *Currencies with high correlation due to central bank policies and regional trade linkages are omitted to avoid high multicollinearity: HKD, TWD, KRW, THB, IDR, and PHP
        """
        conclusion = """
        The GS index demonstrates strong overall performance in tracking the official MAS SGD NEER index. Most deviations are close to zero and fluctuate around zero, indicating that the GS index is unbiased in its tracking and the tracking error over the period from January 2022 to December 2024 is relatively low at 0.0578% (lower than Citi index), reflecting a high degree of consistency and reliability in tracking the official index over the long term.
        
        However, small but consistent noise in the deviations can be attributed to differences in data sources, sampling timing, or data collection methodologies between the indices. The analysis also suggests that the GS index may have overestimated the weightage of the USD, as spikes in deviation and volatility appear to coincide with periods of heightened USD fluctuations.
        
        To further improve the analysis, it will be more beneficial to have more detailed information about the custom index. For example, knowing the exact weights of the currencies in the custom index would allow a more precise understanding of how currency movements influence the deviations and knowing when and how the index rebalances its weights could also clarify whether spikes in tracking error

        Another improvement would be to understand how the formula of indices are constructed. The current analysis assumes the index is a linear combination of exchange rates. However, if the index is constructed differently (e.g., as a product of exchange rates or includes non-linear transformations), this assumption may not hold.In such cases, analyzing deviations might require transformations like natural logarithms or other forms of data manipulation to better reflect the relationship between the indices.
        """

    #monthly tracking error dynamically based on selected deviation
    merged_clean['Month'] = pd.to_datetime(merged_clean['Average for Week Ending']).dt.to_period('M')
    monthly_error = merged_clean.groupby('Month').apply(lambda x: np.std(x[f'Deviation {name}']))
    monthly_error = monthly_error.reset_index(name=f'Tracking Error - {name}')
    
    #  deviation plot
    deviation_fig = go.Figure()
    deviation_fig.add_trace(go.Scatter(
        x=merged_clean['Average for Week Ending'], 
        y=merged_clean[f'Deviation {name}'], 
        mode='lines', 
        name=f'{name} Deviation'
    ))
    deviation_fig.update_layout(
        title=f'Deviation for {name}',
        xaxis_title='Date',
        yaxis_title='Deviation'
    )
    
    #monthly tracking error plot
    monthly_error_fig = go.Figure()
    monthly_error_fig.add_trace(go.Bar(
        x=monthly_error['Month'].astype(str),
        y=monthly_error[f'Tracking Error - {name}'],
        name=f'Monthly Tracking Error - {name}'
    ))
    monthly_error_fig.update_layout(
        title=f'Monthly Tracking Error for {name}',
        xaxis_title='Month',
        yaxis_title='Tracking Error'
    )

    return deviation_fig, f"Tracking Error from May 2022 - Dec 2024: {tracking_error}", ols_summary, monthly_error_fig, deviation_comment, tracking_error_comment, ols_comment, conclusion


if __name__ == '__main__':
    app.run_server(debug=True, port = '8051')
