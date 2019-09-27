#Assignment-4 
#A20416508 - Parthkumar Patel
#Collect data from online social networking site Twitter

"""
Collect data.
"""
from TwitterAPI import TwitterAPI
import sys
import json
import re

consumer_key = 'YTvgXYr30WANVgMi1dXWYB2n8'
consumer_secret = 'rYNvlb2JAsJupz4Mt59BS4F0BhytdeG4yuRnwMVJxxD7b6saLZ'
access_token = '1650765210-8jfsqI4STC0yJJ5h8VSFkvnyWMzHWjKGWAb5iD6'
access_token_secret = 'PQBy9a7sSeguJORYh9w4arcIq292Rkg1486DTO5XkmpvO'

def gettwitter():
    """ Construct an instance of TwitterAPI using the tokens you entered above.
    Returns:
      An instance of TwitterAPI.
    """
    return TwitterAPI(consumer_key, consumer_secret, access_token, access_token_secret)
    

def robust_request(twitter, resource, params, max_tries = 5):
    """ If a Twitter request fails, sleep for 15 minutes.
    Do this at most max_tries times before quitting.
    Args:
      twitter .... A TwitterAPI object.
      resource ... A resource string to request; e.g., "friends/ids"
      params ..... A parameter dict for the request, e.g., to specify
                   parameters like screen_name or count.
      max_tries .. The maximum number of tries to attempt.
    Returns:
      A TwitterResponse object, or None if failed.
    """
    for i in range(max_tries):
        request = twitter.request(resource, params)
        if request.status_code == 200:
            return request
        else:
            print('Got error %s \nsleeping for 15 minutes.' % request.text)
            sys.stderr.flush()
            time.sleep(61 * 15)

def getMinID(tweets):
    """
        return minimumID of tweet from the Twitter Data
    """
    minimumID = tweets[0]['id']
    for i in range(len(tweets)):
        if minimumID > tweets[i]['id']:
            minimumID = tweets[i]['id']
    return minimumID

def getTweets(twitter, searchData):
    """ Search key words and store the result tweets in a file
    Args:
        twitter:
        twitter ...... A TwitterAPI object.
        searchData ... A parameter dict for the request.
    Returns:
        tweets .... Collected TweetsData.
    """
    tweets = [] #array of tweets 
    count = 1
    for tweetrequest in robust_request(twitter, 'search/tweets', searchData):
        tweets.append(tweetrequest) #appending tweets

    while (count < 10):
        minimumID = getMinID(tweets)
        searchData['max_id'] = minimumID - 1
        for tweetrequest in robust_request(twitter, 'search/tweets', searchData):
            tweets.append(tweetrequest)
        count += 1
    #print(tweets)
    return tweets

def saveTweetData(tweetscollected):
    """
    'collectTweetResult.json' ... A json file contain the tweet search result
    """
    filename = 'collectTweetResult.json' 
    with open(filename, 'w', encoding = 'utf-8') as outputfile:
        json.dump(tweetscollected, outputfile,indent=4) #write data in json file
    print("\nCompleted twitter search data collection.\n\nCollected data stored in 'collectTweetResult.json'.\n")

def tokenize(tweets):
    '''Utility function to clean tweet text by removing links, special characters
    using simple regex statements.
    'cleantweet.json'... A json file contain the clean tweet
    '''
    tokens = []
    for tweet in tweets:
        tweet = ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)", " ", tweet['text']).lower().split())
        tweet = re.sub('((www\.[^\s]+)|(https?://[^\s]+))', ' ', tweet).split()
        tokens.append(tweet)
    with open("cleantweet.json", 'w', encoding = 'utf-8') as outputfile:
        json.dump(tokens, outputfile,indent=4)
    print("Clean tweet data stored in 'cleantweet.json'.\n")

def main():
    twitter = gettwitter() #calling a instance of twitterapi
    collectedTweets = getTweets(twitter, {'q': 'Joe Biden  -filter:retweets', 'count': 100, 'lang': 'en'}) # submitting a query to twitter api, and excluding retweets
    saveTweetData(collectedTweets)
    tokenize(collectedTweets)

if __name__ == '__main__':
    main()