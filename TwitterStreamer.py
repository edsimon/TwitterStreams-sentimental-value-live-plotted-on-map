import tweepy, json
from tweepy.api import API
from mpl_toolkits.basemap import Basemap
import matplotlib.pyplot as plt
from textblob import TextBlob
import re

""" Variables 
================"""
searches  = ['trump']    # max 250 input searches in a list of strings
maxTweets = 100000         # max number of tweets to analyse.

# Get the Authentication keys from another file. (Easier to push to git)
with open("/Users/se/Documents/Lek med Python/pyCharmProjects/dataScienceFromScratch/src/twitterKeys.txt","r") as file:
    CONSUMER_KEY        = file.readline().rstrip()
    CONSUMER_SECRET     = file.readline().rstrip()
    ACCESS_TOKEN        = file.readline().rstrip()
    ACCESS_TOKEN_SECRET = file.readline().rstrip()

# Twitter API needs to be validated
auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)

# The class takes in a stream of tweets and filter out some specific properties.
# It is a live streaming so it will be kind of slow and in this purpose i filter
# the Coordinates which only around 3-4% of all tweets have.
class Stream2Screen(tweepy.StreamListener):
    def __init__(self, api=None):
        self.api = api or API()
        self.counter = 0            # Counts amount of tweets already got



    # This is the method that recieves the tweet in the name of data.
    def on_data(self, data):
        datadict = json.loads(data)     # easier to handle in a json file

        # Checks so that the coordinate is in the tweet
        if (datadict.get('place') != None):
            coordinate = calcCenterOfPolygone(datadict['place']['bounding_box']['coordinates'][0])
            tweet = cleanTweets(datadict['text'])
            sentiment = sentimentAnalysis(tweet)
            plotOnMap(coordinate, sentiment.polarity)
            print(tweet)
            print(sentiment, "\n")
            self.counter += 1
            if(self.counter % 100 == 0):
                print(self.counter)

        # if we sent a False as return value we close the "pipeline" of streams
        if self.counter < maxTweets:
            return True
        else:
            return False

    def on_error(self, status_code):
        print(status_code)
        return True

    # Trial to get sentimental value of a tweet using TextBlob
def sentimentAnalysis(tweet):
    tweet = TextBlob(cleanTweets(tweet))
    return tweet.sentiment

def cleanTweets(tweet):
    return ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)", " ", tweet).split())


# Inputs 4 Coordinates in a list and calc the mid point.
def calcCenterOfPolygone(coordinates):
    return [sum([x[0] for x in coordinates]) / 4,
            sum([x[1] for x in coordinates]) / 4]

# Plots the coordinate on the map
def plotOnMap(centerPoint, polarity):
    plt.ion()
    color = 'black'
    if (polarity < 0): color='r'
    elif (polarity > 0): color='g'
    m.plot(centerPoint[0], centerPoint[1], marker='o', markersize=5, color=color)
    draw_map(m)
    plt.pause(0.000001)

# draws the map the first time
def draw_map(m, scale=0.2):
    m.shadedrelief(scale=scale)


fig = plt.figure(figsize=(12, 6))
m = Basemap(projection='cyl', resolution=None,
            llcrnrlat=-90, urcrnrlat=90,
            llcrnrlon=-180, urcrnrlon=180,)

# Starts the twitter feed and searches for the keyword
stream = tweepy.streaming.Stream(auth, Stream2Screen())

while True:
    try:
        stream.filter(track=searches)
    except:
        print("error"*10)
        continue

draw_map(m)
plt.show()
plt.draw()
