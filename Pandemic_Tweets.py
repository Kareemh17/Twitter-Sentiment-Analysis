#Created by Kareem Hirani

#imports
import GetOldTweets3 as got
import re
from textblob import TextBlob 
import matplotlib.pyplot as plt
import datetime
import matplotlib.animation as animation

class Leader(object): #Leader Class
    
    def __init__(self, n):  #requires name parameter
        self.name = n
        self.totalsentiment = 0 #no tweets, no sentiment
        self.Tweets = [] #Contains all Tweets, dictionairies containing text,date,sentiment keys
        self.TweetDates = [] #Contains corressponding tweet dates
        self.DailySentiment = [] #Contains total daily sentiment computed in Calc_Daily_Sentiment funcion
    
    def Calc_Daily_Sentiment(self):
        cday = self.Tweets[0]['Date']
        TweetsforDay = 0 #tweets on cday
        SentimentforDay = 0 #no tweets, no sentiment
        for tweet in self.Tweets: #go through list of tweets
            if tweet['Date'] == cday: 
                SentimentforDay += tweet['Sentiment'] #get value of sentiment
                TweetsforDay+=1
            else:
                if(TweetsforDay != 0):
                    self.DailySentiment.append({'Date':cday,'Sentiment':100*(SentimentforDay/TweetsforDay)}) #new day so add 
                    cday = tweet['Date']
                    #reset values
                    TweetsforDay = 0 
                    SentimentforDay = 0
                else:
                    continue
         #last day
        if(TweetsforDay != 0):
             self.DailySentiment.append({'Date':cday,'Sentiment':100*(SentimentforDay/TweetsforDay)})


#Search Queries, change Strings
WorldLeaders = [Leader("Donald Trump"),
                Leader("Angela Merkel"),
                Leader("Emmanuel Macron"),
                Leader("Boris Johnson"),
                Leader("Giuseppe Conte"),
                Leader("Narendra Modi"),
                Leader("Xi Jinping"),
                Leader("Vladmir Putin")]


def GetTweets(query : Leader):

    start_date = datetime.date(2020,3,22)
    end_date = datetime.date.today()
    date_range = (end_date-start_date).days + 1
    dates = [start_date + datetime.timedelta(n) for n in range(date_range)] # range of dates

    with open("Tweets.txt", "a",encoding='utf-8') as ofile:

        with open("Dates.txt", "a") as datefile:

            for date in dates[1:]:
                
                tweetCriteria = got.manager.TweetCriteria().setQuerySearch(query.name).setSince(start_date.strftime('%Y-%m-%d')).setUntil(date.strftime('%Y-%m-%d')).setMaxTweets(50)

                print("Getting Tweets about {0} on {1}: Please Wait".format(query.name,date.strftime('%Y-%m-%d')))

                #get tweets
                tweets = got.manager.TweetManager.getTweets(tweetCriteria) 

                print("Collected {0} tweets. Now Processing".format(len(tweets)))

                if(len(tweets) == 0): #exit function if no valid tweets
                    return

                positiveTweets = []

                NegativeTweets = []

                start_date = start_date + datetime.timedelta(1) #ensures tweets from already seen days are not mined again
                
                for tweet in tweets:

                        sentiment = TweetSentiment(CleanTweets(tweet.text))

                        sentiment > 0 and positiveTweets.append(tweet) or sentiment < 0 and NegativeTweets.append(tweet) #if sentiment > 0 append to positive twweets, else negative tweets, unused in program

                        query.totalsentiment += sentiment

                      #  ofile.write(CleanTweets(tweet.text) + "\n")

                        date_temp = tweet.date.strftime('%Y-%m-%d') #remove minutes, seconds and milliseconds

                        #every tweet has the text, sentiment, and timestamp

                        query.Tweets.append({'Tweet': CleanTweets(tweet.text), 'Sentiment' : sentiment, 'Date' : date_temp}) 

                        query.TweetDates.append(str(tweet.date))

                      #  datefile.write(str(tweet.date) + "\n")
                
            #Average Sentiment
            print("Average Sentiment for tweets about {0}: {1} %".format(query.name, 100*query.totalsentiment/len(query.Tweets)))

            #ensure dates sorted
            query.Tweets = sorted(query.Tweets,key=lambda k:k['Date'])


            query.Calc_Daily_Sentiment()


def CleanTweets(tweet):
      z = lambda x: re.compile('\#').sub('', re.compile('RT @').sub('@', x, count=1).strip()) #remove RT
      text = z(tweet)
      return ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)", " ", text).split())

    

def TweetSentiment(tweet): #adapted from StackOverFlow Tutorial
    ''' 
    Utility function to classify sentiment of passed tweet 
    using textblob's sentiment method 
    '''
        # create TextBlob object of passed tweet text 
    analysis = TextBlob(CleanTweets(tweet)) 
        # set sentiment 
    return analysis.sentiment.polarity

def animate(query : Leader):

    xarr = [element['Date'] for element in query.DailySentiment] # list of all dates, reverse to be in chronological order
    yarr = [element['Sentiment'] for element in query.DailySentiment] # list of all daily sentiments, reverse to be in chronological order

    xarr, yarr = zip(*sorted(zip(xarr, yarr)))

    plt.plot(xarr,yarr)

for leader in WorldLeaders:
    GetTweets(leader)

WorldLeaders = sorted(WorldLeaders, key=lambda x: len(x.DailySentiment), reverse=True) # sort list by length of tweet dates, ensures proper x-axis

for leader in WorldLeaders:
    animate(leader)



#personal style preferences

plt.style.use('bmh')
plt.style.context('ggplot')
plt.xlabel("Time")
plt.ylabel("Popularity")
plt.title("Popularity of World Leaders throughout Pandemic")
plt.legend([leader.name for leader in WorldLeaders])
plt.tight_layout()
plt.rcParams['font.family'] = 'serif'
plt.rcParams['font.serif'] = 'Ubuntu'
plt.rcParams['font.monospace'] = 'Ubuntu Mono'
plt.rcParams['font.size'] = 10
plt.rcParams['axes.labelsize'] = 10
plt.rcParams['axes.labelweight'] = 'bold'
plt.rcParams['axes.titlesize'] = 10
plt.rcParams['xtick.labelsize'] = 8
plt.rcParams['ytick.labelsize'] = 8
plt.rcParams['legend.fontsize'] = 10
plt.rcParams['figure.titlesize'] = 12
plt.xticks(rotation=90)
plt.show()
