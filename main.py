# Evergreen Tweets
# By @5amwiltshire
# Version 1.0

import datetime
import tweepy
import random
import gspread
from _constant import *
from gdocs import sheet_tweets, sheet_log

auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_KEY, ACCESS_SECRET)
api = tweepy.API(auth, wait_on_rate_limit=True)
user = api.get_user(handle)

# HARDCODED TWEET TIMES
times = [
    [7, 8], # in hours, minutes format without leading 0s 
    [12, 10],
    [17, 43]]

# PUBLISH TWEET - DONE
def tweet(msg, log):
    
    # Twitter variables
    status = api.update_status(msg)
    tweet_id = status.id_str
    timestamp = json_serial(status.created_at)
    text = status.text

    print('tweeting: ' + text)
    logger(tweet_id, text, timestamp, log)

# JSON serializer for objects not serializable by default json code
def json_serial(obj):
    if isinstance(obj, (datetime.datetime, datetime.datetime.date)):
        return obj.isoformat()
    raise TypeError ("Type %s not serializable" % type(obj))

# RANDOMISER - DONE
def randomiser(tweets_list, log):
    next_id = random.randint(0, len(tweets_list) - 1)
    result = tweets_list.pop(next_id)['Tweet']
    return result

# LOGGER
def logger(id, msg, timestamp, log):
    next_row = len(log) + 2

    # for these below, look at why client.update_acell is not working via the gspread package. According the the documentation this is how to update cells
    sheet_log.update_acell('A{}'.format(next_row), id)
    sheet_log.update_acell('B{}'.format(next_row), msg)
    sheet_log.update_acell('C{}'.format(next_row), timestamp)

# CHECKER

# Get tweets from last 7 days

def tweets_in_past_7_days(log, cutoff):
    row_count = len(log)
    n = 0
    
    for x in range(row_count, 0, -1):
        tweet_timestamp = datetime.datetime.strptime(log[x - 1]['Published timestamp'], '%Y-%m-%dT%H:%M:%S')

        if tweet_timestamp > cutoff:
            n += 1
    
    return n

# Log checker

def used_in_prev_7_days(msg, log, cutoff):
    recent_log_count = tweets_in_past_7_days(log, cutoff)
    recent_log = log[recent_log_count*-1:]

    for x in range(recent_log_count):
        if msg == recent_log[x - 1]['Tweet']:
            return True
    
    return False

# SCHEDULER

def scheduler(data, context): # need these arguments as Google Cloud Functions passes these anyway
    now = datetime.datetime.now().replace(microsecond=0)
    cutoff = now - datetime.timedelta(days=7, minutes=5)
    tweets_list = sheet_tweets.get_all_records()
    log = sheet_log.get_all_records()
    msg = get_tweet(tweets_list, log, cutoff)

    for n in times:
        print('Checking ' + str(now.replace(second=0, microsecond=0)) + ' == ' + str(check_time(n[0], n[1])) )
        if now.replace(second=0, microsecond=0) == check_time(n[0], n[1]):
            if msg is not None:
                    tweet(msg, log)
            else:
                print('Posting tweet failed')
        else:
            print('Time ' + str(n) + ' is not now')

def check_time(hr, min, sec=0, micros=0):
    return datetime.datetime.now().replace(hour=hr, minute=min, second=sec, microsecond=micros)

def get_tweet(tweets_list, log, cutoff):
    check = True
    tweet_count = len(tweets_list)

    while check:
        msg = randomiser(tweets_list, log)
        check = used_in_prev_7_days(msg, log, cutoff) # return True or False
        tweet_count -= 1
        if (check == False) or (tweet_count == 0):
            break

    if check == False:
        return msg
    else:
        print('No evergreen tweets left!')
