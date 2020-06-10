import requests
import webbrowser
import json
from twython import Twython
import pandas as pd
import re
import praw
import nltk
import unicodedata
'''
def main():
    #this stuff is all for twitter
    sentenceList1, credibility1 = searchTwitter("how are you", 50, 10, 5, 10)
    print("twitter:")
    print(sentenceList1)
    print(credibility1)
    sentenceList, credibility = searchReddit("how are you",50,100,5,10)
    print("reddit:")
    print(sentenceList)
    print(credibility)
    sentenceList2, credibility2 = searchCorpus("how are you", 10)
    print("corpus:")
    print(sentenceList2)
    print(credibility2)
'''
    #for twitter, cutoff around 10 seems reasonable

def cleanText(text):
    text.replace("’","'")
    text = ''.join(c for c in unicodedata.normalize('NFC', text) if c <= '\uFFFF')
    toRet = ''.join(c for c in text if c <= '\uFFFF')
    toRet = re.sub('(RT )?@(\w)*:?\s','',toRet)
    toRet = re.sub('(\w)*:\w','',toRet)
    toRet = toRet.strip()
    toRet = re.split('[(\.|\?|!)\n]',toRet)
    return list(filter(None, toRet))

def removeWhitespaceAndChars(sentence):
    toRet = re.split('[,@#:\'\:; ?!~_   ]',sentence)
    return list(filter(None, toRet))

def searchTwitter(exactTerm,howManyToQuery,cutoff,ncutoff,dispcutoff):

    creds = json.load(open("credentials.json", "r"))

    python_tweets = Twython(creds['twitter'][0]['CONSUMER_KEY'], creds['twitter'][0]['CONSUMER_SECRET'])
    query = {'q': '"'+exactTerm+'"',
             'count': howManyToQuery,
             'lang': 'en'
             }
    jsonStuff = python_tweets.search(**query)

    sentences = {}
    retweetTotal = 0
    n = 0
    for tweet in jsonStuff['statuses']:
        for sent in cleanText(tweet['text']):
            # print(sent)
            if (exactTerm.lower() in sent.lower()):
                if not sent.strip().lower() == exactTerm.lower():
                    n +=  1
                    # print(tweet['retweet_count'])
                    retweetTotal += tweet['retweet_count'] #go back to fix l8r
                    sentences[sent.strip()] = tweet['retweet_count']
    #
    #now lets turn lists into strings
    sentences = {k: v for k, v in sorted(sentences.items(), key=lambda item: item[1],reverse=True)}
    toRet = {}
    keysToHit = list(sentences.keys())[0:dispcutoff]
    # print(len(keysToHit))
    for key in keysToHit:
        toRet[key] = sentences[key]

    if not n == 0:
        print('retweets avg: ', retweetTotal / n)
        return toRet, determineConfidence(n, retweetTotal/n, cutoff, ncutoff), retweetTotal/n
    return {}, 'No results: extremely unreliable', 'N/A'


def searchReddit(exactTerm,howManyToQuery,cutoff,ncutoff,dispcutoff):
    sentences = {}
    creds = json.load(open("credentials.json", "r"))
    reddit = praw.Reddit(client_id=creds['reddit'][0]['CLIENT_ID'], \
                         client_secret=creds['reddit'][0]['CLIENT_SECRET'], \
                         user_agent='texter', \
                         username = creds['reddit'][0]['USERNAME'], \
                         password = creds['reddit'][0]['PASSWORD'] )
    all = reddit.subreddit('all')
    results = all.search(exactTerm, limit=howManyToQuery)
    upvoteTotal = 0
    n = 0
    for i in results:
        
        for sent in cleanText(i.title):
            if (exactTerm.lower() in sent.lower()):
                n  += 1
                upvoteTotal += i.score
                sentences[sent] = i.score
    print(sentences)
    sentences = {k: v for k, v in sorted(sentences.items(), key=lambda item: item[1], reverse=True)}
    toRet = {}
    keysToHit = list(sentences.keys())[0:dispcutoff]
    # print(len(keysToHit))
    for key in keysToHit:
        toRet[key] = sentences[key]
    if n > 0:
        upvoteAvg = upvoteTotal/ n
        print('upvote avg: ',str(upvoteAvg))
        return toRet, determineConfidence(n,upvoteAvg,cutoff,ncutoff), upvoteTotal/n
    return {}, 'No results: extremely unreliable', 'N/A'

def determineConfidence(n,avg,cutoff,ncutoff):
    if (avg < cutoff or n < ncutoff):
        return 'likely unreliable'
    else:
        return 'likely reliable'

def searchCorpus(exactTerm,cutoff):
    searchingFor = exactTerm.split()
    namesGuten = nltk.corpus.gutenberg.fileids()
    # print(len(nltk.corpus.gutenberg.sents(namesGuten)))
    # print(len(nltk.corpus.gutenberg.sents(namesGuten[0])))
    browncats = nltk.corpus.brown.categories()
    # print(nltk.corpus.brown.sents(categories = browncats))
    reutcats = nltk.corpus.reuters.categories()
    # print(nltk.corpus.reuters.sents(categories = reutcats))

    sentences = []
    n = 0

    #NOTE: may want to drop reuters for speed
    #nltk.corpus.reuters.sents(categories = reutcats),
    
    for corpusActive in [nltk.corpus.gutenberg.sents(namesGuten), \
                         nltk.corpus.brown.sents(categories = browncats)]:
        for sent in corpusActive:
            if set([x.lower() for x in searchingFor]).issubset([x.lower().translate({ord(':'): None, ord(';'): None, ord('-'): None}) for x in sent]):
                for i in range(len(sent)-len(searchingFor)):
                    if [x.lower() for x in sent[i:i+len(searchingFor)]] == [x.lower().translate({ord(':'): None, ord(';'): None, ord('-'): None}) for x in searchingFor]:
                        sentences.append(sent)
                        n += 1
        #print('through an iteration')
        if n >= cutoff:
            break
    # print(n)

    sentList = []
    for sent in sentences:
        compilation = ""
        for word in sent:
            compilation += word + ' '
        sentList.append(compilation.strip())
    print(len(sentList))
    return sentList, determineConfidence(n, 100, 10, 1)
# main()
# print(requests.get('https://api.twitter.com/1.1/search/tweets.json?q=twitterdev%20new%20premium').json())


# this was how the json file was made
# imported from https://stackabuse.com/accessing-the-twitter-api-with-python/
# import json
#
# # Enter your keys/secrets as strings in the following fields
# credentials = {}
# credentials['CONSUMER_KEY'] = '2qD8WeoF60TJhQS'
# credentials['CONSUMER_SECRET'] = 'FOOhA3kikQdj_DD7kO6AFPEq-Is'
# credentials['ACCESS_TOKEN'] = ...
# credentials['ACCESS_SECRET'] = ...
#
# # Save the credentials object to file
# with open("twitter_credentials.json", "w") as file:
#     json.dump(credentials, file)
