import pymongo
import json
from dateutil import parser
import gzip
import shutil
import os


def read_json(file):
    with open(file, 'r') as inp:
        tweets_dict = []
        num_of_tweets = 0
        for line in nonblank_lines(inp):
            num_of_tweets += 1

            try:
                tweet = json.loads(line)
                if tweet['id'] not in tweet_ids:
                    tweet_ids.add(tweet['id'])
                    tweets_dict.append(parse_date(tweet))
            except ValueError:
                print('Decoding JSON has failed - value error')
            except TypeError:
                print('Decoding JSON has failed - type error')

            # Insert tweets into db for every 10000 tweets
            if len(tweets_dict) == 10000:
                insert_tweets(tweets_dict)
                del tweets_dict[:]

    insert_tweets(tweets_dict)
    return num_of_tweets


def nonblank_lines(f):
    for x in f:
        line = x.rstrip()
        if line:
            yield line


def parse_date(tweets_dict):
    tweets_dict['created_at'] = parser.parse(tweets_dict['created_at'])

    return tweets_dict


def insert_tweets(tweets_to_mongo):
    collection.insert_many(tweets_to_mongo)


def index_creation():
    collection.create_index([('created_at', 1)])


def helper(comp_file, file):
    with gzip.open(comp_file, 'rb') as f_in:
        with open(file, 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)
    num = read_json(file)
    os.remove(file)
    return num


def print_stats(file, num, num_of_tweets):
    print("{}\n------------------\nNumber of tweets(file): {}".format(file, num))
    print("Total Number of tweets: {}".format(num_of_tweets))
    print("Total Number of unique tweets: {}".format(len(tweet_ids)))


def main():
    num_of_tweets = 0
    print("Number of unique tweets: {}".format(len(tweet_ids)))

    for i in reversed(range(1, 11)):
        comp_file = 'ht_coronavirus_' + str(i) + '.gz'
        file = 'ht_coronavirus_' + str(i) + '.json'
        num = helper(comp_file, file)
        num_of_tweets += num
        print_stats(file, num, num_of_tweets)

        comp_file = 'ht_COVID19_' + str(i) + '.gz'
        file = 'ht_COVID19_' + str(i) + '.json'
        num = helper(comp_file, file)
        num_of_tweets += num
        print_stats(file, num, num_of_tweets)

    print('=======================================')
    print("Total Number of tweets: {}".format(num_of_tweets))
    print("Total Number of unique tweets: {}".format(len(tweet_ids)))
    index_creation()


if __name__ == '__main__':
    
    client = pymongo.MongoClient("mongodb://localhost:27017/")
    db = client['covidTweetsDB']
    collection = db['tweets']
    
    tweet_ids = set([item["id"] for item in  collection.find({}, {"_id": 0, "id": 1})])
    
    main()
