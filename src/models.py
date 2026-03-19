
from typing import List, Union

from sqlalchemy import Integer, String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase, relationship


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = 'user'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    api_key: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)

    followers: Mapped[List] = relationship(
        "Subs",
        foreign_keys="Subs.follower_id",
        back_populates="follower",
        lazy="joined",
        cascade="all, delete-orphan",
    )

    followings: Mapped[List] = relationship(
        "Subs",
        foreign_keys="Subs.following_id",
        back_populates="following",
        lazy="joined",
        cascade="all, delete-orphan",
    )
    tweets: Mapped[List["Tweet"]] = relationship(
        "Tweet", back_populates="author", lazy="joined", cascade="all, delete-orphan"
    )
    likes: Mapped[List["Like"]] = relationship(
        "Like", back_populates="author", lazy="joined", cascade="all, delete-orphan"
    )


class Subs(Base):
    __tablename__ = "subs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    follower_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("user.id", ondelete="cascade"))
    following_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("user.id", ondelete="cascade")
    )

    follower: Mapped["User"] = relationship(
        "User",
        foreign_keys=following_id,
        lazy="joined",
        back_populates="followers",
        # overlaps="followers",
    )

    following: Mapped["User"] = relationship(
        "User",
        foreign_keys=follower_id,
        lazy="joined",
        back_populates="followings",
        # overlaps="followers",
    )


class Tweet(Base):
    __tablename__ = "tweet"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    content: Mapped[str] = mapped_column(String(300), nullable=False)
    attachments: Mapped[List["Media"]] = relationship("Media", back_populates="tweet")

    author_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("user.id", ondelete="cascade")
    )
    author: Mapped["User"] = relationship(
        "User", back_populates="tweets", lazy="joined"
    )
    likes: Mapped[List["Like"]] = relationship(
        "Like", back_populates="tweet", lazy="joined"
    )


class Media(Base):
    __tablename__ = "media"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)

    tweet_id: Mapped[Union[int, None]] = mapped_column(
        Integer, ForeignKey("tweet.id", ondelete="cascade")
    )
    tweet: Mapped["Tweet"] = relationship(
        "Tweet",
        lazy="joined",
        back_populates="attachments"
    )


class Like(Base):
    __tablename__ = "like"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    tweet_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("tweet.id", ondelete="cascade")
    )
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("user.id", ondelete="cascade")
    )

    author: Mapped["User"] = relationship(
        "User",
        back_populates="likes",
        lazy="joined",
        foreign_keys=user_id
    )
    tweet: Mapped["Tweet"] = relationship(
        "Tweet",
        back_populates="likes",
        lazy="joined",
        foreign_keys=tweet_id
    )
