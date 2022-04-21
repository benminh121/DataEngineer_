import tweepy
from kafka import KafkaProducer
import logging

"""API ACCESS KEYS"""

consumer_key = ""
consumer_secret = ""
access_token = ""
access_secret = ""

producer = KafkaProducer(bootstrap_servers='localhost:9092')
search_term = 'Bitcoin'
topic_name = 'twitterS'

def twitterAuth():
    # create the authentication object
    authenticate = tweepy.OAuthHandler(consumer_key, consumer_secret)
    # set the access token and the access token secret
    authenticate.set_access_token(access_token, access_secret)
    # create the API object
    api = tweepy.API(authenticate, wait_on_rate_limit=True)
    return api

class TweetListener(tweepy.Stream):

    def on_data(self, raw_data):
        logging.info(raw_data)
        producer.send(topic_name, value=raw_data)
        return True

    def on_error(self, status_code):
        if status_code == 420:
            # returning False in on_data disconnects the stream
            return False

    def start_streaming_tweets(self, search_term):
        self.filter(track=search_term, stall_warnings=True, languages=["en"])

if __name__ == '__main__':
    twitter_stream = TweetListener(consumer_key, consumer_secret, access_token, access_secret)
    twitter_stream.start_streaming_tweets(search_term)
