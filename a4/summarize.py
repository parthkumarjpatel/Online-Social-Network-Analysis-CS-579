#Assignment-4 
#A20416508 - Parthkumar Patel
#Analyze the results and summarize your conclusions
"""
Summarize data.
"""
import json

def main():
    #read data from files
    tweets = json.loads(open('collectTweetResult.json').read())
    clusters = json.loads(open('clusteredData.json').read())
    positive = json.loads(open('positiveTweet.json').read())
    neutral = json.loads(open('neutralTweet.json').read())
    negative = json.loads(open('negativeTweet.json').read())

    userscollected = sum(len(n) for n in clusters)

    with open('summary.txt', 'w',encoding = 'utf-8') as outputfile:
        outputfile.write("Number of users collected: %d\n\n" % userscollected)
        outputfile.write("Number of messages collected: %d\n\n" % len(tweets))
        outputfile.write("Number of communities discovered: %d\n\n" % len(clusters))
        outputfile.write("Average number of users per community: %f\n\n" % (userscollected / len(clusters)))
        outputfile.write("Instances of positive class found : %d \n\n" % len(positive))
        outputfile.write("Instances of neutral class found %d : \n\n" % len(neutral))
        outputfile.write("Instances of negative class found %d : \n\n" % len(negative))
        outputfile.write("Example of positive class: \n%s\nscore = %d\n\n" % (positive[0][0],positive[0][1]))
        outputfile.write("Example of neutral class : \n%s\nscore = %d\n\n" % (neutral[0][0], neutral[0][1]))
        outputfile.write("Example of negative class : \n%s\nscore = %d\n\n" % (negative[0][0], negative[0][1]))
    print("\nCompleted summary.\n\nSummarized data stored in 'summary.txt'.\n")



if __name__ == '__main__':
    main()