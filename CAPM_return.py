import datetime
import streamlit as st
import pandas as pd
import appdirs as ad
ad.user_cache_dir = lambda *args: "/tmp"
import yfinance as yf
import pandas_datareader.data as web
import CAPM_functions

st.set_page_config(page_title = "CAPM",
                   page_icon = "chart_with_upwards_trend",
                   layout = 'wide')

st.title("Capital Asset Pricing Model")

#getting input from user:
col1,col2 = st.columns([1,1])
with col1:
    stocks_list = st.multiselect("Choose 4 stocks", ('TSLA','AAPL','NFLX','MSFT','NVDA','AMZN','GOOGL','MGM','KNSA'),['TSLA','AAPL','NVDA','GOOGL'])
with col2:
    year = st.number_input('Number of Years',1,15)

#getting data of S&P500
try:
    
    end = datetime.date.today()
    start = datetime.date(datetime.date.today().year - year, datetime.date.today().month, datetime.date.today().day)

    SP500 = web.DataReader(['sp500'],'fred',start,end)

    stocks_df = pd.DataFrame()

    for stock in stocks_list:
        data = yf.download(stock,period=f'{year}y')
        stocks_df[f'{stock}'] = data['Close']

    stocks_df.reset_index(inplace=True)
    SP500.reset_index(inplace=True)
    SP500.columns = ['Date','sp500']
    stocks_df['Date'] = pd.to_datetime(stocks_df['Date'])
    stocks_df = pd.merge(stocks_df,SP500, on='Date', how='inner')

    col1,col2 = st.columns([1,1])
    with col1:
        st.markdown('### Dataframe head')
        st.dataframe(stocks_df.head(),use_container_width=True)

    with col2:
        st.markdown('### Dataframe tail')
        st.dataframe(stocks_df.tail(),use_container_width=True)


    col1,col2 = st.columns([1,1])
    with col1:
        st.markdown('### Price of all Stocks')
        st.plotly_chart(CAPM_functions.interactive_plot(stocks_df))

    with col2:
        st.markdown('### Price of all Stocks After Normalization')
        st.plotly_chart(CAPM_functions.interactive_plot(CAPM_functions.normalize(stocks_df)))

    stocks_daily_return = CAPM_functions.daily_return(stocks_df)
    print(stocks_daily_return.head())

    beta = {}
    alpha = {}

    for i in stocks_daily_return.columns:
        if i != 'Date' and i != 'SP500':
            b,a = CAPM_functions.calculate_beta(stocks_daily_return,i)
            beta[i] = b
            alpha[i] = a
    print(beta,alpha)

    beta_df = pd.DataFrame(columns = ['Stock','Beta value'])
    beta_df['Stock'] = beta.keys()
    beta_df['Beta value'] = [str(round(i,2)) for i in beta.values()]

    with col1:
        st.markdown('### calculated Beta Value')
        st.dataframe(beta_df, use_container_width=True)

    rf = 4.28
    rm = stocks_daily_return['sp500'].mean()*252
    print(rm)
    return_df = pd.DataFrame()
    return_value = []
    for stock, value in beta.items():
        return_value.append(str(round(rf+(value*(rm-rf)),2)))
    return_df['Stock'] = stocks_list

    return_df['Return Value'] = pd.Series(return_value)

    with col2:
        st.markdown('### Calculated Return using CAPM')
        st.dataframe(return_df,use_container_width=True)

except:
    st.write('Please Select Valid Input!')