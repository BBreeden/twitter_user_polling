import tweepy
from pymongo import MongoClient
import dns

# Twitter setup
consumer_key = ''
consumer_secret = ''
access_token_key = ''
access_token_secret = ''

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token_key, access_token_secret)

api = tweepy.API(auth)

# MongoDB Setup
client = MongoClient('')
mynewdb = client['']
mycol = mynewdb['']

# User Config
tw_user_id = ''

for status in tweepy.Cursor(api.user_timeline,id = tw_user_id).items(2000):
    print(status.text, flush = True)

    # If the tweet is a reply, save that information. Otherwise, pass None.
    if (status.in_reply_to_screen_name != None):
        reply_user_id = status.in_reply_to_user_id
        reply_screen_name = status.in_reply_to_screen_name
    else:
        reply_user_id = None
        reply_screen_name = None

    # Handles tweet text length. Fetches the full text if the tweet is long enough.
    try:
        text = status.extended_tweet['full_text']
    except AttributeError as e:
        print(e, flush = True)
        text = status.text

    # Compile the data to be inserted into the database.
    data = {
        'author_id' : status.user.id,
        'author_screen_name' : status.user.screen_name,
        'tweet_id' : status.id,
        'timestamp' : status.created_at,
        'text' : text,
        'reply_user_id' : reply_user_id,
        'reply_screen_name' : reply_screen_name                
    }

    # Insert the data into the database and close the client.
    mycol.insert_one(data)
    print('Record saved successfully: ' + str(status.id), flush=True)

print('Process complete.')