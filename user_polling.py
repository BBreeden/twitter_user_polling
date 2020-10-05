import tweepy
from pymongo import MongoClient
import dns
import time


def setup_tweepy():
    '''Return the api object for the configured tweepy keys.'''

    print('Tweepy configuration started...', flush=True)
    consumer_key = ''
    consumer_secret = ''
    access_token_key = ''
    access_token_secret = ''

    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token_key, access_token_secret)

    api = tweepy.API(auth)
    print('Tweepy configured successfully')
    return(api)

def mongo_init():
    '''Return a pymongo/mongoDB collection object for the configured client & database configured.'''

    print('Mongo configuration started...', flush=True)
    client = MongoClient('')
    mynewdb = client['']
    mycol = mynewdb['']
    
    print('Mongo configured successfully', flush=True)
    return mycol

if __name__ == "__main__":
    # Setup/Config
    twitter_api = setup_tweepy()
    mongo_collection = mongo_init()
    print('Configuration successful.', flush=True)

    while True:
        for status in tweepy.Cursor(twitter_api.user_timeline,id='25073877').items(25):
            print('Cycle has begun', flush=True)

            # If the id is already in the database, break out of the loop for the next cycle.
            if mongo_collection.count_documents({ 'tweet_id': status.id }, limit = 1) != 0:
                print('Duplicate record found:', status.id, flush=True)
                print('Cycle complete.', flush=True)
                break

            # If the id is new, create a new data dictionary. Then pass the data dictionary into a new MongoDB record.
            else:
                # If the tweet is a reply, save that information. Otherwise, pass None.
                if (status.in_reply_to_screen_name != None):
                    reply_user_id = status.in_reply_to_user_id
                    reply_screen_name = status.in_reply_to_screen_name
                else:
                    reply_user_id = None
                    reply_screen_name = None

                # Handles tweet text length. Fetches the full text if the tweet is long enough. Otherwise, fetch the normal text.
                try:
                    text = status.extended_tweet['full_text']
                except AttributeError as e:
                    print(e, flush=True)
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
                mongo_collection.insert_one(data)
                print('Record saved successfully: ' + str(status.id), flush=True)
        
        time.sleep(60)