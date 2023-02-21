import logging
import tweepy
from decouple import config

consumer_key = config("CONSUMER_KEY")
consumer_secret = config("CONSUMER_SECRET")
access_token = config("ACCESS_TOKEN")
access_token_secret = config("ACCESS_TOKEN_SECRET")

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)

api = tweepy.API(auth)

try:
    api.verify_credentials()
    print("Authentication OK")
except:
    print("Error during authentication")


# to create a tweet
async def create_tweet(tweet):
    await api.update_status(tweet)
    return 'created new tweet successfully'


# to update user profile
async def update_profile(description):
    await api.update_profile(description)
    return 'profile updated successfully'


# to like a tweet
async def like_tweet():
    tweets = api.home_timeline(count=1)
    # picking the most recent tweet
    tweet = tweets[0]
    await api.create_favorite(tweet.id)
    return f"{tweet.author.name} has been liked"


# to search for tweets
async def search_tweet(text):
    for tweet in api.search(q=text, lang="en", rpp=10):
        print(f"{tweet.user.name}:{tweet.text}")


# to automatically reply to mentions
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()


async def check_mentions(keywords, since_id):
    logger.info("Retrieving mentions")
    new_since_id = since_id
    for tweet in tweepy.Cursor(api.mentions_timeline, since_id=since_id).items():
        new_since_id = max(tweet.id, new_since_id)
        if tweet.in_reply_to_status_id is not None:
            continue
        if any(keyword in tweet.text.lower() for keyword in keywords):
            logger.info(f"Answering to {tweet.user.name}")

            if not tweet.user.following:
                tweet.user.follow()

            await api.update_status(status="Please reach us via DM", in_reply_to_status_id=tweet.id)
    return new_since_id
