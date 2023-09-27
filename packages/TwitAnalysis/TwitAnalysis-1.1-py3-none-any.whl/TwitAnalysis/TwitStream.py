import tweepy
from termcolor import cprint, colored
from textblob import TextBlob

"""
    Custom stream class for streaming live tweet data
"""
class TwitStream(tweepy.StreamingClient):
    def __init__(self, bearer_token, name, volume, live=True):
        #super().__init__(consumer_key, consumer_secret, acces_token, access_token_secret)
        super().__init__(bearer_token)
        self.name = name
        self.volume = volume 
        self.tweets = 0
        self.reg_tweets = 0
        self.retweets = 0
        self.is_live = live
        self.unique_retweets = []
        self.pos = 0
        self.neg = 0
        self.impact_raw = 0

   
    def get_sentiment(self):
        """ Get sentiment of the stream
            
        Returns
        -------
        (float, float) : (%pos, %neg)

        """
        if self.tweets > 0:
            return ( round(self.pos/self.tweets*100,2), round(self.neg/self.tweets*100,2) )
        else:
            return (0,0)

    def get_perc_retweets(self):
        """ Get percent of tweets processed that are retweets
        """
        if self.tweets == 0:
            return 0
        return round((self.retweets/self.tweets)*100,2)

    def get_perc_unique_retweets(self):
        """ Get the percentage of retweets that are unique
        """
        if self.retweets == 0:
            return 0
        return round((self.get_unique_retweets()/self.retweets)*100,2)

    def get_unique_retweets(self):
        """ Get the number of unique retweets from the stream
        """
        return len(self.unique_retweets)

    def _get_impact_raw(self, tweet):
        """ Get the sum of followers of the tweet's author
        """
        followers = tweet.author.followers_count
        # for retweet in tweet.retweets():
        #     followers += retweet.author.followers_count

        self.impact_raw += followers

    def _print_tweet(self, tweet, text, quoted_text, url, quote_url):
        """ Print tweet to the console

        Parameters
        ----------
        Status : tweet 
            Tweet Status object
        string : text
            Text from the tweet
        string : quoted_text
            quoted text from tweet
        string : url
            tweet url
        string : quote_url
            url of the quoted tweet
        """
        # Print header for tweet or retweet
        if hasattr(tweet, 'retweeted_status'):
            print(f"{colored(tweet.author.name,'cyan')} retweeted {colored(tweet.retweeted_status.author.name,'yellow')}")

        else:
            print(f"{colored(tweet.author.name,'cyan')} tweeted")

        # Print location if there
        if tweet.author.location:
            print(f"[{colored(tweet.author.location,'magenta')}] --- [{colored(url,'red')}]")
        else:
            print(f"[{colored('***','magenta')}] --- [{colored(url,'red')}]")


        # Print tweet contents
        print(text)

        # Print quote if there
        if hasattr(tweet, 'quoted_status'):
            print(f"\n=====\n{colored(tweet.quoted_status.author.name,'yellow')} - [{colored(quote_url,'red')}]\n{colored(quoted_text,'blue')}\n=====")

        print("---\n\n")

    def _get_url(self, tweet):
        """ Get the url associated with the given tweet
        """
        return f"https://twitter.com/twitter/statuses/{tweet.id}"

    def _get_text(self, status):
        """ Get text associated with the given tweet
        """
        if hasattr(status, 'extended_tweet'):
            return status.extended_tweet['full_text']
        else:
            return status.text
            
    def _calc_sentiment(self, tweet):
        """ Get sentiment of tweet

            TODO: update to account for varying levels of polarity
        """
        blob = TextBlob(self._get_text(tweet))
        if blob.polarity > 0:
            self.pos += 1
        else:
            self.neg += 1

    def on_tweet(self, status):
        """ Main function that performs processing every time a Tweet status is recieved in the stream
        
        Parameters
        ----------
        Status : status
            Tweet status object

        """
        retweet_text = ""
        retweet_url = ""
        quoted_text = ""
        quote_url = ""
        
        self._calc_sentiment(status)
        self._get_impact_raw(status)
        
        # Get text from retweet
        if hasattr(status, 'retweeted_status'):
            retweet_url = self._get_url(status.retweeted_status)
            retweet_text = self._get_text(status.retweeted_status)
            if status.retweeted_status.id not in self.unique_retweets:
                self.unique_retweets.append(status.retweeted_status.id)

            self.retweets += 1
        else:
            self.reg_tweets += 1
        # Get text from quoted tweet
        if hasattr(status, 'quoted_status'):
            quote_url = self._get_url(status.quoted_status)
            quoted_text = self._get_text(status.quoted_status)

        # Get text from tweet
        url = self._get_url(status)
        text = self._get_text(status)

        if self.is_live:
            if hasattr(status, 'retweeted_status'):
                self._print_tweet(status, retweet_text, quoted_text, retweet_url, quote_url)
            else:
                self._print_tweet(status, text, quoted_text, url, quote_url)

        self.tweets += 1