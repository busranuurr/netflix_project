from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Float, Table
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

# Film-Kullanıcı ilişki tablosu
user_movie_ratings = Table(
    'user_movie_ratings',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id'), primary_key=True),
    Column('movie_id', Integer, ForeignKey('movies.id'), primary_key=True),
    Column('rating', Float)
)

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    
    # İlişkiler
    ratings = relationship("Movie", secondary=user_movie_ratings, back_populates="users")
    preferences = relationship("UserPreference", back_populates="user")

class Movie(Base):
    __tablename__ = "movies"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String)
    genre = Column(String)
    release_year = Column(Integer)
    rating = Column(Float)
    
    # İlişkiler
    users = relationship("User", secondary=user_movie_ratings, back_populates="ratings")

class UserPreference(Base):
    __tablename__ = "user_preferences"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    genre = Column(String)
    min_rating = Column(Float)
    preferred_years = Column(String)  # JSON formatında yıllar
    
    # İlişkiler
    user = relationship("User", back_populates="preferences") 