from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import models
from database import SessionLocal, engine
from ml_models import RecommendationSystem, MovieClustering
import schemas
from fastapi.middleware.cors import CORSMiddleware

# Veritabanı tablolarını oluştur
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Film Öneri Sistemi")

# CORS ayarları
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Veritabanı bağlantısı için dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Öneri sistemi ve kümeleme modellerini oluştur
recommendation_system = RecommendationSystem()
movie_clustering = MovieClustering()

@app.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = models.User(
        email=user.email,
        username=user.username,
        hashed_password=user.password  # Gerçek uygulamada hash'lenmiş olmalı
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@app.post("/movies/", response_model=schemas.Movie)
def create_movie(movie: schemas.MovieCreate, db: Session = Depends(get_db)):
    db_movie = models.Movie(**movie.dict())
    db.add(db_movie)
    db.commit()
    db.refresh(db_movie)
    return db_movie

@app.post("/ratings/")
def create_rating(rating: schemas.RatingCreate, db: Session = Depends(get_db)):
    db_rating = models.user_movie_ratings.insert().values(
        user_id=rating.user_id,
        movie_id=rating.movie_id,
        rating=rating.rating
    )
    db.execute(db_rating)
    db.commit()
    return {"message": "Rating created successfully"}

@app.get("/recommendations/{user_id}", response_model=List[schemas.Movie])
def get_recommendations(user_id: int, db: Session = Depends(get_db)):
    # Kullanıcının izleme geçmişini al
    user_ratings = db.query(models.user_movie_ratings).filter(
        models.user_movie_ratings.c.user_id == user_id
    ).all()
    
    # Film özelliklerini al
    movies = db.query(models.Movie).all()
    movie_features = {
        movie.id: [
            float(movie.rating),
            len(movie.description.split()),
            movie.release_year
        ] for movie in movies
    }
    
    # Modeli eğit ve önerileri al
    X, y = recommendation_system.prepare_data(
        {user_id: {r.movie_id: r.rating for r in user_ratings}},
        movie_features
    )
    results = recommendation_system.train_and_evaluate(X, y)
    
    # En iyi modeli kullanarak önerileri al
    user_features = [0] * len(next(iter(movie_features.values())))  # Basit özellik vektörü
    recommended_movie_ids = recommendation_system.get_recommendations(
        user_features,
        movie_features
    )
    
    # Önerilen filmleri döndür
    recommended_movies = db.query(models.Movie).filter(
        models.Movie.id.in_(recommended_movie_ids)
    ).all()
    
    return recommended_movies

@app.get("/similar-movies/{movie_id}", response_model=List[schemas.Movie])
def get_similar_movies(movie_id: int, db: Session = Depends(get_db)):
    # Tüm filmleri al
    movies = db.query(models.Movie).all()
    movie_features = {
        movie.id: [
            float(movie.rating),
            len(movie.description.split()),
            movie.release_year
        ] for movie in movies
    }
    
    # Kümeleme modelini eğit
    movie_clustering.fit(movie_features)
    
    # Benzer filmleri bul
    similar_movie_ids = movie_clustering.get_similar_movies(movie_id, movie_features)
    
    # Benzer filmleri döndür
    similar_movies = db.query(models.Movie).filter(
        models.Movie.id.in_(similar_movie_ids)
    ).all()
    
    return similar_movies

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 