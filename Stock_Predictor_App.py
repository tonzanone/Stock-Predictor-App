import streamlit as st
import yfinance as yf
from stocksymbol import StockSymbol
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
import pandas as pd

# This is API Key of stocksymbol API. Use your own key.
api_key = 'daf2adb4-22db-4ded-becd-b7c7aeddc75a'
ss = StockSymbol(api_key)

# This is title
st.title("StockSage - Stock Predictor ")
# Image used
st.image("stock_img.jpg")
st.caption("Credit to Unsplash")

# Different sections for different things such as view , predict and search
sec_one = st.container()
sec_two = st.container()
sec_three = st.container()
sec_four = st.container()


# The function works to get all the stocks available in us and india
@st.cache_data
def Starting_sys(_ss):
    symbol_list_us = ss.get_symbol_list(market="US")
    symbol_stock_us = []
    for i in range(0,len(symbol_list_us)):
        a = symbol_list_us[i]['symbol']
        symbol_stock_us.append(a)
    symbol_list_india = ss.get_symbol_list(market="india")
    symbol_stock_india = []
    for i in range(0,len(symbol_list_india)):
        a = symbol_list_india[i]['symbol']
        symbol_stock_india.append(a)
    
    total_ss= symbol_stock_india + symbol_stock_us
    total_ss.sort()
    return list(total_ss)

total_ss = Starting_sys(ss)

# searches for stocks starting with search_key
def search(list_ss,search_key):
    search_key = search_key.upper()
    t = []
    if search_key == "":
        return t
    for i in list_ss:
        if i.startswith(search_key):
            t.append(i)
    if len(t) == 0:
        return "No"
    else:
        return t

# returns data of stock for 60 days max
def stock_x_days(list_ss, stock, x=10):
    if stock not in list_ss:
        print("No such stock available")
        return None
    else:
        if x >= 60:
            x = 60
        xdays = str(x) + 'd'
        stock_var = yf.Ticker(stock)
        stock_hist = stock_var.history(period=xdays)
        stock_data = pd.DataFrame(stock_hist)
        stock_data = stock_data.reset_index()
        stock_data['Date'] = pd.to_datetime(stock_data['Date']).dt.date
        return stock_data

# return data of stock for unlimited days as much as you desire
def stock_x_days_unlimited(list_ss, stock, x=10):
    if stock not in list_ss:
        print("No such stock available")
    else:
        xdays = str(x) + 'd'
        stock_var = yf.Ticker(stock)
        stock_hist = stock_var.history(period=xdays)
        stock_data = pd.DataFrame(stock_hist)
        stock_data = stock_data.reset_index()
        stock_data['Date'] = pd.to_datetime(stock_data['Date']).dt.date
        return stock_data

# Prediction part
def real_production(train_data,model_name,start,end,start2,d):
    if model_name == 'model_lr':
        X = train_data[start].values.reshape(-1, 1)
        y = train_data[end].values
        model_lr = LinearRegression()
        model_lr.fit(X, y)
        
        train_data2 = train_data.copy()
        train_data2[start2] = train_data2[start].shift(-1)
        train_data2.drop(columns=start)
        train_data2.dropna(inplace=True)
        X2 = train_data2[end].values.reshape(-1,1)
        y2 = train_data2[start2].values
        model_lr2 = LinearRegression()
        model_lr2.fit(X2,y2)
        tclose = y[-1]
        l = []
        l2 = []
        for i in range(0,d):
            predicted_c_o = model_lr2.predict([[tclose]])
            l.append(round(predicted_c_o[0],2))
            predict_o_c = model_lr2.predict([[l[-1]]])
            l2.append(round(predict_o_c[0],2))
            tclose = l2[-1]
        print_df = pd.DataFrame({'Open':l,'Close':l2})
        return print_df
    


with sec_one:
    st.markdown("# Introduction to StockSage Tool")
    st.write(" Introducing a powerful stock prediction tool with an array of functionalities! Track stock performance over custom timeframes, make accurate stock value predictions, and effortlessly visualize stock trends. Explore additional metrics to enhance your analysis. This all-in-one solution empowers users with comprehensive insights for informed decision-making. Stay ahead in the stock market with our cutting-edge tool.")
    
with sec_two:
    st.title("Search Your Stock")
    st.write("Discover all market stocks in one click with our powerful search bar.")
    stock_name_search = st.text_input("Search your stock")
    if search(total_ss,stock_name_search) == "No":
        t = []
    else:
        t = search(total_ss,stock_name_search)
    
    stock_name = st.selectbox(
        'Select Stock Name',
        ['Select'] + t
    )

with sec_three:
    st.title("View your Stock")
    st.markdown("### Select the Number of Days of data you want to see : ")
    days = st.slider("Select Number of Days",10,60)
    view_data = stock_x_days(total_ss, stock_name, days)
    if view_data is not None:
        st.dataframe(view_data[['Date', 'Open', 'Close', 'High', 'Low']].style.highlight_max(axis=0), use_container_width=True)
        if len(view_data) > 5:
            st.title("Graph of the above stock")
            chart_data = view_data[['Open','Close']]
            st.line_chart(chart_data,use_container_width=True)
        if len(stock_x_days_unlimited(total_ss,stock_name,120)) > 30:
            view_data_metrics = stock_x_days(total_ss,stock_name,120)
            current_day_data = view_data_metrics.iloc[-1]
            current_ten_days_data = view_data_metrics.iloc[-10]
            last_month_data = view_data_metrics.iloc[-30]
            change_in_open_10 = round(((current_day_data['Open']-current_ten_days_data['Open'])/current_ten_days_data['Open'])*100)
            change_in_open_30 = round(((current_day_data['Open']-last_month_data['Open'])/last_month_data['Open'])*100)
            change_in_close_10 = round(((current_day_data['Close']-current_ten_days_data['Close'])/current_ten_days_data['Close'])*100)
            change_in_close_30 = round(((current_day_data['Close']-last_month_data['Close'])/last_month_data['Close'])*100)
            st.title("Open Values for Stock")
            col1, col2 = st.columns(2)
            col1.metric('Current and change in last 10 days',str(round(current_day_data['Open'],2)),str(change_in_open_10) + " % ")
            col2.metric('Current and change in last 30 days',str(round(current_day_data['Open'],2)),str(change_in_open_30) + " % ")
            st.title("Close Values for Stock")
            col1, col2 = st.columns(2)
            col1.metric('Current and change in last 10 days',str(round(current_day_data['Close'],2)),str(change_in_close_10) + " % ")
            col2.metric('Current and change in last 30 days',str(round(current_day_data['Close'],2)),str(change_in_close_30) + " % ")   
    else:
        st.write("Please select a valid stock from the list.")

with sec_four:
    st.title("Prediction of Stocks")
    if stock_name != 'Select':
        if len(stock_x_days_unlimited(total_ss,stock_name,120)) > 30:
            days_p = st.slider("Select Number of Days",2,5)
            data = stock_x_days_unlimited(total_ss, stock_name, 120)
            predict_df = real_production(data,'model_lr','Open','Close','Open2',days_p)
            open = predict_df['Open']
            close = predict_df['Close']
            col1,col2 = st.columns(2)
            col1.title("Predicted Open")
            for i in range(len(open)):
                col1.metric("Day {0}".format(i+1),str(open[i]))
            col2.title("Predicted Close")
            for i in range(len(close)):
                col2.metric("Day {0}".format(i+1),str(close[i]))
        else:
            st.write("Please select some other stock from the list which has more data available.")
    else:
        st.write("Please select a valid stock from the list.")



    


    
    
    