from pydantic import BaseModel
from typing import Optional, List

class UserBase(BaseModel):
    email: str
    username: str

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    is_active: bool

    class Config:
        orm_mode = True

class MovieBase(BaseModel):
    title: str
    description: str
    genre: str
    release_year: int
    rating: float

class MovieCreate(MovieBase):
    pass

class Movie(MovieBase):
    id: int

    class Config:
        orm_mode = True

class RatingCreate(BaseModel):
    user_id: int
    movie_id: int
    rating: float

class UserPreferenceBase(BaseModel):
    genre: str
    min_rating: float
    preferred_years: str

class UserPreferenceCreate(UserPreferenceBase):
    user_id: int

class UserPreference(UserPreferenceBase):
    id: int
    user_id: int

    class Config:
        orm_mode = True 