#Assignment-4 
#A20416508 - Parthkumar Patel
#Perform supervised classification to annotate messages and/or users according to some criterion.
"""
Classify data.
"""
import json
from zipfile import ZipFile
from io import BytesIO
from urllib.request import urlopen
import re

def readData():
    """ read the data collected in the 'collect.py' and cleaned tweet data
    Return:
        tweets ... a json object with tweets.
    """
    tweets =  json.loads(open('collectTweetResult.json').read()) #read collected tweet data
    tokens = json.loads(open('cleantweet.json').read()) #read cleaned tweet data for sentiment analysis
    return tweets,tokens

def getAFINN():
    """Download latest AFINN data
    Returns:
        Dictionary of sentimentally rated words
    """

    url = urlopen('http://www2.compute.dtu.dk/~faan/data/AFINN.zip')
    zipfile = ZipFile(BytesIO(url.read()))
    afinn_file = zipfile.open('AFINN/AFINN-111.txt')
    afinn = dict()
    for line in afinn_file:
        parts = line.strip().split()
        if len(parts) == 2:
            afinn[parts[0].decode("utf-8")] = int(parts[1])
    return afinn

def calculatesentimentscore(afinn, feats):
    '''compute afinn score for each tokens
    return:
        sentimentscore ... afinn sentiment score of token
    '''
    sentimentscore = 0
    for f in feats:
        if f in afinn:
            sentimentscore += afinn[f]
    return sentimentscore

def ratingOfTweet(tokens, tweets,afinn):
    '''rate tweets sentiment use afinn sentiment analyze
    return:
        positivetweets ... a list with positive score (tweet, score) tuple
        neutraltweets .... a list with neutral score (tweet, score) tuple
        negativetweets ... a list with negative score (tweet, score) tuple
    '''
    positivetweets = []
    neutraltweets = []
    negativetweets = []
    for token, tweet in zip(tokens,tweets):
        sentimentscore = calculatesentimentscore(afinn, token)
        if sentimentscore > 0:
            positivetweets.append((tweet['text'], sentimentscore))
        elif sentimentscore == 0 :
            neutraltweets.append((tweet['text'], sentimentscore))
        else:
            negativetweets.append((tweet['text'], sentimentscore))
    return positivetweets, neutraltweets, negativetweets

def writeDataToFile(filename, data):
    #print(len(data))
    with open(filename, 'w', encoding = 'utf-8') as outputfile:
        json.dump(data, outputfile,indent=4)

def main():
    tweets,tokens = readData() #read data from json files
    afinn = getAFINN() #get afinn data
    positivetweets, neutraltweets, negativetweets = ratingOfTweet(tokens, tweets, afinn) # rate tweet and divide into positivetweets,neutraltweets and negativetweets
    writeDataToFile('positiveTweet.json', positivetweets)
    writeDataToFile('neutralTweet.json', neutraltweets)
    writeDataToFile('negativeTweet.json', negativetweets)
    print("\nCompleted data classification.\n\nClassified data stored in 'positiveTweet.json', 'neutralTweet.json' and 'negativeTweet.json' according to their sentiment score.\n")

if __name__ == '__main__':
    main()