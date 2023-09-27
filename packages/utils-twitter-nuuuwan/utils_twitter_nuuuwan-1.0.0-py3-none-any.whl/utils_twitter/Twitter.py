from utils_twitter.TwitterActionerMixin import TwitterActionerMixin
from utils_twitter.TwitterBase import TwitterBase
from utils_twitter.TwitterLoaderMixin import TwitterLoaderMixin


class Twitter(TwitterBase, TwitterLoaderMixin, TwitterActionerMixin):
    pass
