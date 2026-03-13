from sqlalchemy import Column, Integer, String, ForeignKey, Text
from sqlalchemy.dialects.postgresql import ARRAY

from database import Base


class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    api_key = Column(String(50), unique=True, nullable=False)
    name = Column(Text, nullable=False)
    tweets = Column(ARRAY(Integer))
    following = Column(ARRAY(Integer))
    followers = Column(ARRAY(Integer))


class Tweets(Base):
    __tablename__ = "tweets"

    tweet_id = Column(Integer, primary_key=True)
    author_id = Column(Integer, ForeignKey('user.id'))
    likes = Column(ARRAY(Integer))
    content = Column(Text)
    attachments = Column(ARRAY(String))




