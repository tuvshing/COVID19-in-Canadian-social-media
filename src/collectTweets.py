import json
import argparse
import tweepy
import sys
import pandas as pd

# main class
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-o", help="location of the output file")
    parser.add_argument("-n", help="number of tweets to collect")
    args = parser.parse_args()
    outputFile = args.o
    num = int(args.n)
    
    # using twitter api v1.1
    stream = tweetFilter(
        "vRXi9ix5gXRnFFDmZqYzid2ra",
        "HhsU6NK3bDmPf6eYRvJ21HoAGrhQU6dgBKEGy8ePJkWp5zbDqG",
        "3275137423-KNPAMIfyR0rPBMaBzzWlQZD8Mwysff2TvD5IRW1",
        "SjzjfEs7O5miX7L4BSgpPhOhDQN5ecJ0h7uF7HC60v6PT",
    )

    # set the output file and the amount of tweets to collect
    stream.setParameters(outputFile, num)
    
    # filters
    stream.filter(
        track=["covid", "AstraZeneca", "vaccination", "Pfizer", "Moderna"],
        languages=["en"],
        # filter_level='medium',
        locations=[-140.99778, 41.6751050889, -52.6480987209, 83.23324]
    )
    
# collects and saves tweets concerning Covid in Canada.  
class tweetFilter(tweepy.Stream):
    track=["covid", "AstraZeneca", "vaccination", "Pfizer", "Moderna"]
    dic = []
    collected = 0
    streamed = 0
    outputFile = 'default.json'
    stopAt = 10
    def setParameters(self, out, num):
        self.outputFile = out
        self.stopAt = num

    def on_status(self, status):
        return True

    def on_data(self, data):
        self.streamed += 1
        sys.stdout.write(
            "\rCollected Tweets: {0}\t Streamed Tweets: {1}".format(
                self.collected, self.streamed
            )
        )
        sys.stdout.flush()
        tweet = json.loads(data)
        # to remove retweets 
        if not tweet['retweeted'] and not tweet['text'].startswith('RT'):
            if any(x in tweet['text'] for x in self.track):
                self.dic.append([tweet["created_at"], tweet["id"], tweet["text"]])
                self.collected += 1

        sys.stdout.write(
            "\rCollected Tweets: {0}\t Streamed Tweets: {1}".format(
                self.collected, self.streamed
            )
        )
        sys.stdout.flush()
        if self.collected >= self.stopAt:
            print("\Finished!")
            df = pd.DataFrame(self.dic, columns=["created_at", "id", "text"])
            
            dic = df.to_dict("records")
            with open(self.outputFile, "w", encoding="utf-8") as f:
                json.dump(dic, f, ensure_ascii=False, indent=4)
            # disconnect stream
            # self.disconnect()
            exit(0)
        else:
            return True

    def on_error(self, status):
        print(status)
        if status == 420:
            return False 
        return True 
    


if __name__ == "__main__":
    main()