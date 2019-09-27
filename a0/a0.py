# coding: utf-8

"""
CS579: Assignment 0
Collecting a political social network

In this assignment, I've given you a list of Twitter accounts of 4
U.S. presedential candidates from the previous election.

The goal is to use the Twitter API to construct a social network of these
accounts. We will then use the [networkx](http://networkx.github.io/) library
to plot these links, as well as print some statistics of the resulting graph.

1. Create an account on [twitter.com](http://twitter.com).
2. Generate authentication tokens by following the instructions [here](https://developer.twitter.com/en/docs/basics/authentication/guides/access-tokens.html).
3. Add your tokens to the key/token variables below. (API Key == Consumer Key)
4. Be sure you've installed the Python modules
[networkx](http://networkx.github.io/) and
[TwitterAPI](https://github.com/geduldig/TwitterAPI). Assuming you've already
installed [pip](http://pip.readthedocs.org/en/latest/installing.html), you can
do this with `pip install networkx TwitterAPI`.

OK, now you're ready to start collecting some data!

I've provided a partial implementation below. Your job is to complete the
code where indicated.  You need to modify the 10 methods indicated by
#TODO.

Your output should match the sample provided in Log.txt.
"""

# Imports you'll need.
from collections import Counter
import matplotlib.pyplot as plt
import networkx as nx
import sys
import time
from TwitterAPI import TwitterAPI
import itertools

consumer_key = ''
consumer_secret = ''
access_token = ''
access_token_secret = ''

# This method is done for you.
def get_twitter():
    """ Construct an instance of TwitterAPI using the tokens you entered above.
    Returns:
      An instance of TwitterAPI.
    """
    return TwitterAPI(consumer_key, consumer_secret, access_token, access_token_secret)


def read_screen_names(filename):
	"""
	Read a text file containing Twitter screen_names, one per line.

	Params:
	    filename....Name of the file to read.
	Returns:
	    A list of strings, one per screen_name, in the order they are listed
	    in the file.

	Here's a doctest to confirm your implementation is correct.
	>>> read_screen_names('candidates.txt')
	['DrJillStein', 'GovGaryJohnson', 'HillaryClinton', 'realDonaldTrump']
	"""
	###TODO
	candidatenames = []
	with open(filename, 'r') as names:
		for line in names:
			candidatenames.append(line.strip())
#		candidatenames = [line.strip() for line in names]
	return candidatenames
	pass
# I've provided the method below to handle Twitter's rate limiting.
# You should call this method whenever you need to access the Twitter API.
def robust_request(twitter, resource, params, max_tries=5):
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


def get_users(twitter, screen_names):
	"""Retrieve the Twitter user objects for each screen_name.
	Params:
	    twitter........The TwitterAPI object.
	    screen_names...A list of strings, one per screen_name
	Returns:
	    A list of dicts, one per user, containing all the user information
	    (e.g., screen_name, id, location, etc)

	See the API documentation here: https://dev.twitter.com/rest/reference/get/users/lookup

	In this example, I test retrieving two users: twitterapi and twitter.

	>>> twitter = get_twitter()
	>>> users = get_users(twitter, ['twitterapi', 'twitter'])
	>>> [u['id'] for u in users]
	[6253282, 783214]
	"""
	###TODO
	userDataResponse = robust_request(twitter,'users/lookup', {'screen_name':screen_names},5)
	#usersDic = [data for data in userDataResponse]
	usersDic = []
	for data in userDataResponse:
		usersDic.append(data)
	#print(usersDic[0])
	return usersDic
	pass	

def get_friends(twitter, screen_name):
    """ Return a list of Twitter IDs for users that this person follows, up to 5000.
    See https://dev.twitter.com/rest/reference/get/friends/ids

    Note, because of rate limits, it's best to test this method for one candidate before trying
    on all candidates.

    Args:
        twitter.......The TwitterAPI object
        screen_name... a string of a Twitter screen name
    Returns:
        A list of ints, one per friend ID, sorted in ascending order.

    Note: If a user follows more than 5000 accounts, we will limit ourselves to
    the first 5000 accounts returned.

    In this test case, I return the first 5 accounts that I follow.
    >>> twitter = get_twitter()
    >>> get_friends(twitter, 'aronwc')[:5]
    [695023, 1697081, 8381682, 10204352, 11669522]
    """
    ###TODO
    usersFriends = []
    friendsDataResponse = robust_request(twitter,"friends/ids",{'screen_name':screen_name,'count':5000,'cursor':-1},5)
    for friendID in friendsDataResponse:
    	usersFriends.append(friendID)
    usersFriends = sorted(usersFriends)
    #print(usersFriends)
    return(usersFriends)
    pass


def add_all_friends(twitter, users):
    """ Get the list of accounts each user follows.
    I.e., call the get_friends method for all 4 candidates.

    Store the result in each user's dict using a new key called 'friends'.

    Args:
        twitter...The TwitterAPI object.
        users.....The list of user dicts.
    Returns:
        Nothing

    >>> twitter = get_twitter()
    >>> users = [{'screen_name': 'aronwc'}]
    >>> add_all_friends(twitter, users)
    >>> users[0]['friends'][:5]
    [695023, 1697081, 8381682, 10204352, 11669522]
    """
    ###TODO
    for eachuser in range(len(users)):
    	friendsOfUser = get_friends(twitter,users[eachuser]['screen_name'])
    	users[eachuser]['friends']=friendsOfUser
    pass


def print_num_friends(users):
    """Print the number of friends per candidate, sorted by candidate name.
    See Log.txt for an example.
    Args:
        users....The list of user dicts.
    Returns:
        Nothing
    """
    ###TODO
    #print(len(users[0]['friends']))
    for indexOfUser in range(len(users)):
        print(users[indexOfUser]['screen_name'] , len(users[indexOfUser]['friends']))
    pass



def count_friends(users):
    """ Count how often each friend is followed.
    Args:
        users: a list of user dicts
    Returns:
        a Counter object mapping each friend to the number of candidates who follow them.
        Counter documentation: https://docs.python.org/dev/library/collections.html#collections.Counter

    In this example, friend '2' is followed by three different users.
    >>> c = count_friends([{'friends': [1,2]}, {'friends': [2,3]}, {'friends': [2,3]}])
    >>> c.most_common()
    [(2, 3), (3, 2), (1, 1)]
    """
    ###TODO
    countFriendsOfUsers = Counter()
    for eachuser in users:
        countFriendsOfUsers.update(eachuser['friends'])
    return countFriendsOfUsers
    pass


def friend_overlap(users):
    """
    Compute the number of shared accounts followed by each pair of users.

    Args:
        users...The list of user dicts.

    Return: A list of tuple scontaining (user1, user2, N), where N is the
        number of accounts that both user1 and user2 follow.  This list should
        be sorted in descending order of N. Ties are broken first by user1's
        screen_name, then by user2's screen_name (sorted in ascending
        alphabetical order). See Python's builtin sorted method.

    In this example, users 'a' and 'c' follow the same 3 accounts:
    >>> friend_overlap([
    ...     {'screen_name': 'a', 'friends': ['1', '2', '3']},
    ...     {'screen_name': 'b', 'friends': ['2', '3', '4']},
    ...     {'screen_name': 'c', 'friends': ['1', '2', '3']},
    ...     ])
    [('a', 'c', 3), ('a', 'b', 2), ('b', 'c', 2)]
    """
    ###TODO
    friendsOverlapOfUsers = []
    for user1, user2 in itertools.combinations(users, 2):
        countFriendsOfUsers=Counter()
        countFriendsOfUsers.update(user1['friends'])
        countFriendsOfUsers.update(user2['friends'])
        commonFriendsBetweenTwoUser = [friend for friend in user1['friends'] if countFriendsOfUsers[friend]==2]
        friendsOverlapOfUsers.append((user1['screen_name'],user2['screen_name'],len(commonFriendsBetweenTwoUser)))

    friendsOverlapOfUsers=sorted(friendsOverlapOfUsers, key=lambda x:(x[2]),reverse=True)
    return friendsOverlapOfUsers
    pass


def followed_by_hillary_and_donald(users, twitter):
	"""
	Find and return the screen_names of the Twitter users followed by both Hillary
	Clinton and Donald Trump. You will need to use the TwitterAPI to convert
	the Twitter ID to a screen_name. See:
	https://dev.twitter.com/rest/reference/get/users/lookup

	Params:
	    users.....The list of user dicts
	    twitter...The Twitter API object
	Returns:
	    A list of strings containing the Twitter screen_names of the users
	    that are followed by both Hillary Clinton and Donald Trump.
	"""
	###TODO
	for fu in users:
		if fu['screen_name']=="HillaryClinton":          
		    for su in users:             
		        if su['screen_name']=="realDonaldTrump":                 
		            c=Counter()
		            c.update(fu['friends'])
		            c.update(su['friends'])
		            commonFriendOfHillaryAndDonald=[k for k in fu['friends'] if c[k]==2]
		            break
	name = robust_request(twitter,"users/lookup",{'user_id':commonFriendOfHillaryAndDonald},5)
	listofcommanfriend = [r for r in name]
	userfollowedbyhillaryanddonald = [listofcommanfriend[0]['screen_name'],listofcommanfriend[1]['screen_name']]
	return userfollowedbyhillaryanddonald
	pass


def create_graph(users, friend_counts):
    """ Create a networkx undirected Graph, adding each candidate and friend
        as a node.  Note: while all candidates should be added to the graph,
        only add friends to the graph if they are followed by more than one
        candidate. (This is to reduce clutter.)

        Each candidate in the Graph will be represented by their screen_name,
        while each friend will be represented by their user id.

    Args:
      users...........The list of user dicts.
      friend_counts...The Counter dict mapping each friend to the number of candidates that follow them.
    Returns:
      A networkx Graph
    """
    ###TODO
    graph = nx.Graph()
    for user in users:
        candidate_name= user['screen_name']
        for usersFriend in user['friends']:
            for key in friend_counts:
                if (usersFriend == key and friend_counts[key]>1):                 
                    graph.add_edge(user['screen_name'],usersFriend)
                    break
    return graph
    pass



def draw_network(graph, users, filename):
    """
    Draw the network to a file. Only label the candidate nodes; the friend
    nodes should have no labels (to reduce clutter).

    Methods you'll need include networkx.draw_networkx, plt.figure, and plt.savefig.

    Your figure does not have to look exactly the same as mine, but try to
    make it look presentable.
    """
    ###TODO
    typeOfGraph=nx.spring_layout(graph)
    labels={}
    for user in users:
        labels[user['screen_name']]=user['screen_name']
    plt.figure(figsize=(12,12))
    nx.draw_networkx(graph,labels=labels,with_labels=True,node_color='blue',alpha=.5, width=.2,edge_color='r')
    plt.axis('off')
    plt.savefig(filename,format="PNG",frameon=None,dpi=500)
    plt.show()
    pass


def main():
	""" Main method. You should not modify this. """
	twitter = get_twitter()
	screen_names = read_screen_names('candidates.txt')
	print('Established Twitter connection.')
	print('Read screen names: %s' % screen_names)
	users = sorted(get_users(twitter, screen_names), key=lambda x: x['screen_name'])
	print('found %d users with screen_names %s' %
	      (len(users), str([u['screen_name'] for u in users])))
	#get_friends(twitter,users)
	add_all_friends(twitter, users)
	print('Friends per candidate:')
	print_num_friends(users)
	friend_counts = count_friends(users)
	print('Most common friends:\n%s' % str(friend_counts.most_common(5)))
	print('Friend Overlap:\n%s' % str(friend_overlap(users)))
	print('User followed by Hillary and Donald: %s' % str(followed_by_hillary_and_donald(users, twitter)))

	graph = create_graph(users, friend_counts)
	print('graph has %s nodes and %s edges' % (len(graph.nodes()), len(graph.edges())))
	draw_network(graph, users, 'network.png')
	print('network drawn to network.png')


if __name__ == '__main__':
    main()

# That's it for now! This should give you an introduction to some of the data we'll study in this course.
