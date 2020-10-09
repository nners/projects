import base64
import requests
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt  
import tweepy
import time
import datetime
from google.colab import drive
from wordcloud import WordCloud, STOPWORDS, ImageColorGenerator
from matplotlib.ticker import StrMethodFormatter

tw_client_key = <client_key>
tw_client_secret = <client_secret>
access_token_key = <token_key>
access_token_secret = <token_secret>

auth = tweepy.OAuthHandler(tw_client_key, tw_client_secret)
auth.set_access_token(access_token_key, access_token_secret)

keyword_list = [<LIST OF HASHTAGS>]

api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)

# Saving each report for each of the hashtags

def generate_hashtag_user_info(keywords, start_date, end_date, table_size_limit):
  for keyword in keywords:

    id = []
    name = []
    timestamp = []
    followers = []
    hashtags = []
    text = []
    count = 0
    pages = tweepy.Cursor(api.search, keyword, since = start_date, until = end_date,
                          result_type = 'recent').pages()

    for page in pages:
      for tweet in page:
        id.append(tweet.id)
        name.append(tweet.user.screen_name)
        text.append(tweet.text)
        timestamp.append(tweet.created_at)
        followers.append(tweet.user.followers_count)
        hashtags.append([i['text'] for i in tweet.entities["hashtags"]])
        count += 1
      if count >= table_size_limit:
        break
    
    with open('/gdrive/My Drive/' + keyword, 'w+') as f:
      keyword_table = pd.DataFrame.from_dict(data = {'name': name, 'timestamp': timestamp, 'followers': followers,
                                          'id': id, 'text': text, 'hashtags': hashtags})
      keyword_table.to_csv(f)
      
# Accessing to botometer

rapidapi_key = '<key>'
twitter_app_auth = {
    'consumer_key': '<consumer key>',
    'consumer_secret': '<consumer secret>',
    'access_token': '<access token>',
    'access_token_secret': '<token secret>',
  }
bom = Botometer(wait_on_ratelimit=True,
                          rapidapi_key=rapidapi_key,
                          **twitter_app_auth)

reported_count = 0

tweets = 100000

# Reporting bots 

for keyword in keywords:
    for page in tweepy.Cursor(api.search, keyword).pages():
      for tweet in page:
        if bom.check_account(tweet.user.id)['display_scores']['universal']['spammer'] > 0.5:
            api.report_spam(tweet.user.id)
            
            
Visualizing trends 

# SAMPLE FILTER FOR DATE 
datestamp_filter = '2020-09-25'

#SAMPLE FILTER FOR WORD - MULTIPLE WORDS CAN BE INCLUDED 
word_filter = ['']

word_counts = word_counts.where( (word_counts['datestamp'] >
                                        datestamp_filter) & 
                                        (word_counts['text_split'].isin(word_filter))).dropna()
            reported_count += 1
            time.sleep(1) 
            
 try:
  word_counts.groupby([word_counts["text_split"], word_counts["date"]]).count().plot(kind="bar")
except:
  print('No Data')
