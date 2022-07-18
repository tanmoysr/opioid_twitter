import tweepy
import sys
import csv
import datetime
import json
import os

'''
Access token :709847542805061632-shB6hKIdPSy5phvdCSjX9nb1DlFhqSL
Access token secret :3a20PfidarvYfbKOviZP9tWXax6jnGXbNzEZElqgTCiSd
'''
# authorization tokens
consumer_key = "KgetwY2LfPQRbFXg7vsyKdoix"  # Add your API key here
consumer_secret = "y2sS7sjcwwq0c5zWQv7w8CDsmTbjEVAjiRqLlcH2slmyoEjQ48"  # Add your API secret key here
access_key = "709847542805061632-shB6hKIdPSy5phvdCSjX9nb1DlFhqSL"
access_secret = "3a20PfidarvYfbKOviZP9tWXax6jnGXbNzEZElqgTCiSd"


# StreamListener class inherits from tweepy.StreamListener and overrides on_status/on_error methods.
class StreamListener(tweepy.StreamListener):
    def on_status(self, status):
        print(status.id_str)
        # if "retweeted_status" attribute exists, flag this tweet as a retweet.
        is_retweet = hasattr(status, "retweeted_status")

        # check if text has been truncated
        if hasattr(status, "extended_tweet"):
            text = status.extended_tweet["full_text"]
        else:
            text = status.text

        # check if this is a quote tweet.
        is_quote = hasattr(status, "quoted_status")
        quoted_text = ""
        if is_quote:
            # check if quoted tweet's text has been truncated before recording it
            if hasattr(status.quoted_status, "extended_tweet"):
                quoted_text = status.quoted_status.extended_tweet["full_text"]
            else:
                quoted_text = status.quoted_status.text

        # remove characters that might cause problems with csv encoding
        remove_characters = [",", "\n"]
        for c in remove_characters:
            text.replace(c, " ")
            quoted_text.replace(c, " ")

        with open("out.csv", "a", encoding='utf-8') as f:
            f.write("%s,%s,%s,%s,%s,%s\n" % (
            status.created_at, status.user.screen_name, is_retweet, is_quote, text, quoted_text))

    def on_error(self, status_code):
        print("Encountered streaming error (", status_code, ")")
        sys.exit()


if __name__ == "__main__":
    # complete authorization and initialize API endpoint
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_key, access_secret)
    api = tweepy.API(auth)

    # initialize stream
    query = 'TNT'
    year = 2020
    month = 4
    date = 28

    end_year = 2020
    end_month = 12
    end_date = 1

    term_dir = 'data/terms/'
    for filename in os.listdir(term_dir):
        if filename.endswith(".txt"):
            print(os.path.join(term_dir, filename))
            if 'key' not in filename:
                with open(os.path.join(term_dir, filename), 'r') as t_file:
                    for query in t_file.readlines():
                        query = query.strip()
                        start_date = datetime.datetime(year, month, date, 0, 0, 0)
                        # print(query, start_date)
                        # end_date = datetime.datetime(end_year, end_month, end_date, 0, 0, 0)
                        out_name = 'data/' + query + '_' + str(year) + '_' + str(month) + '_' + str(date) + '_' + '.txt'
                        print(out_name)
                        if not os.path.isfile(out_name):
                            with open(out_name, 'w+') as f:
                                print('**************', query, start_date)
                                for tweet in tweepy.Cursor(api.search,
                                                           q=query, # Customized terms for query
                                                           # since=start_date, until=end_date,
                                                           # since=start_date,
                                                           geocode="39.1014537,-84.5124602,206km", # geo location with radius
                                                           lang="en",
                                                           wait_on_rate_limit = True).items():
                                    # print(tweet)
                                    f.write(json.dumps(tweet._json) + '\n')
        else:
            continue



    # csvFile.close()

    # api = tweepy.API(auth)
    # page = 1
    # stop_loop = False
    # while not stop_loop:
    #     tweets = api.user_timeline(username, page=page)
    #     if not tweets:
    #         break
    #     for tweet in tweets:
    #         if datetime.date(YEAR, MONTH, DAY) < tweet.created_at:
    #             stop_loop = True
    #             break
    #         # Do the tweet process here
    #     page += 1
    #     time.sleep(500)
