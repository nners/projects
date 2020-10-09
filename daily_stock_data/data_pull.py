# Data Extraction 
from datetime import datetime
from os import environ
import pandas as pd
import requests
import pickle
import time
import sys


# list of S&P 500 companies 
url = r'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
tables = pd.read_html(url) # Returns list of all tables on page
sp500_table = tables[0] # Select table of interest

companies = list(sp500_table[0][1:])
keys = ["time", "dopen", "dclose", "daclose", "dhigh", "dlow", "dvolume"]
portfolio = {c: {k: [] for k in keys} for c in companies}

# API data
api_root = "https://www.alphavantage.co/query"
api_delay = 13 # api time restriction in seconds
API_KEYS = environ["ALPHA_API_KEY"].split(",")
payload = {'function': 'TIME_SERIES_DAILY_ADJUSTED', 
           'outputsize': 'full'}

for i, company in enumerate(portfolio):
    
    print("processing {} ({} of {})".format(company, i+1, len(portfolio)))
    
    # setting request params
    api_key = API_KEYS[1] if i < 250 else API_KEYS[0]
    payload["apikey"] = api_key
    payload["symbol"] = company
    
    # collecting the data
    start_time = time.time()
    response_dict = requests.get(api_root.format(company), params=payload).json()
    if "Error Message" in response_dict and "Invalid API call" in response_dict["Error Message"]:
        response_dict = requests.get(api_root.format(company.replace(".", "-")), params=payload).json()
    
    # converting into suitable format
    try:
        data = response_dict["Time Series (Daily)"]
        portfolio[company]["time"], portfolio[company]["dopen"], \
        portfolio[company]["dclose"], portfolio[company]["daclose"], \
        portfolio[company]["dhigh"], portfolio[company]["dlow"], \
        portfolio[company]["dvolume"] = zip(*[(datetime.strptime(day, '%Y-%m-%d'),
                                               float(data[day]['1. open']),
                                               float(data[day]['4. close']),
                                               float(data[day]['5. adjusted close']),
                                               float(data[day]['2. high']),
                                               float(data[day]['3. low']),
                                               int(data[day]['6. volume'])) for day in data])
    except Exception as ex:
        if "Note" in response_dict:
            print(response_dict["Note"])
        else:
            print(ex)
        
    # make sure 5 requests per minute limitation is satisfied (1 request in 12 seconds)
    elapsed_time = time.time() - start_time
    if elapsed_time < api_delay:
        print("waiting for {:.2f} seconds to satisfy API restrictions ...".format(api_delay - elapsed_time))
        time.sleep(api_delay - elapsed_time)
        
  
with open('s_p_500_historical_{}.pkl'.format(datetime.today().strftime("%B %d, %Y")), 'wb') as f:
    pickle.dump(portfolio, f)

with open('s_p_500_table_{}.pkl'.format(datetime.today().strftime("%B %d, %Y")), 'wb') as f:
    pickle.dump(sp500_table, f)
    
    
    
## Financial Ratios 


#Stock Prices and Volume 
import timeit
start_time = timeit.default_timer()
# code you want to evaluate
elapsed = timeit.default_timer() - start_time
company_list = list(sp500_table[0].drop(0)) #Get the list of companies from the wiki page
df = []
for i in company_list[0:5]: 
    yahoo_url = "https://finance.yahoo.com/quote/%s/history/" % i  # Request the stock history for each company
    request = pd.read_html(yahoo_url)[0]
    request['Company Symbol'] = i
    df.append(pd.DataFrame(request))  #Append it all to one list 
SP_list = pd.concat(df)
SP_list.where(SP_list['Company Symbol'] != "MMM")


# Important Company Ratios - must be updated daily. Note that the PE ratio and EPS ratio are valid for 12 months 
company_list = list(sp500_table[0].drop(0)) #Get the list of companies from the wiki page
df = []
for i in company_list[0:5]: 
    yahoo_url_ratio = "https://finance.yahoo.com/quote/%s/" % str(i)  # Request the stock history for each company
    request = pd.read_html(yahoo_url_ratio)[1]
    request['Company Symbol'] = i
    df.append(pd.DataFrame(request))  #Append it all to one list 
SP_list_ratios = pd.concat(df)
SP_list_ratios
