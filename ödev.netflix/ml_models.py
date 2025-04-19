import numpy as np
import pandas as pd
from sklearn.neighbors import KNeighborsClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

class RecommendationSystem:
    def __init__(self):
        self.models = {
            'knn': KNeighborsClassifier(n_neighbors=5),
            'random_forest': RandomForestClassifier(n_estimators=100),
            'svm': SVC(kernel='rbf')
        }
        self.scaler = StandardScaler()
        self.best_model = None
        self.best_model_name = None

    def prepare_data(self, user_ratings, movie_features):
        # Kullanıcı-film matrisini oluştur
        X = []
        y = []
        
        for user_id, ratings in user_ratings.items():
            for movie_id, rating in ratings.items():
                if movie_id in movie_features:
                    X.append(movie_features[movie_id])
                    y.append(rating)
        
        return np.array(X), np.array(y)

    def train_and_evaluate(self, X, y):
        # Veriyi eğitim ve test setlerine ayır
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Verileri ölçeklendir
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        best_score = 0
        results = {}
        
        # Her modeli eğit ve değerlendir
        for name, model in self.models.items():
            model.fit(X_train_scaled, y_train)
            y_pred = model.predict(X_test_scaled)
            
            # Model performansını hesapla
            accuracy = accuracy_score(y_test, y_pred)
            precision = precision_score(y_test, y_pred, average='weighted')
            recall = recall_score(y_test, y_pred, average='weighted')
            f1 = f1_score(y_test, y_pred, average='weighted')
            
            results[name] = {
                'accuracy': accuracy,
                'precision': precision,
                'recall': recall,
                'f1': f1
            }
            
            # En iyi modeli güncelle
            if f1 > best_score:
                best_score = f1
                self.best_model = model
                self.best_model_name = name
        
        return results

    def get_recommendations(self, user_features, movie_features, n_recommendations=5):
        if self.best_model is None:
            raise Exception("Model henüz eğitilmemiş!")
        
        # Kullanıcı özelliklerini ölçeklendir
        user_features_scaled = self.scaler.transform([user_features])
        
        # Tüm filmler için tahmin yap
        predictions = []
        for movie_id, features in movie_features.items():
            movie_features_scaled = self.scaler.transform([features])
            combined_features = np.concatenate([user_features_scaled, movie_features_scaled], axis=1)
            prediction = self.best_model.predict(combined_features)
            predictions.append((movie_id, prediction[0]))
        
        # En yüksek tahmin değerine sahip filmleri seç
        recommendations = sorted(predictions, key=lambda x: x[1], reverse=True)[:n_recommendations]
        return [movie_id for movie_id, _ in recommendations]

class MovieClustering:
    def __init__(self, n_clusters=5):
        self.kmeans = KMeans(n_clusters=n_clusters)
        self.scaler = StandardScaler()

    def fit(self, movie_features):
        # Film özelliklerini ölçeklendir
        features_scaled = self.scaler.fit_transform(list(movie_features.values()))
        self.kmeans.fit(features_scaled)
        return self.kmeans.labels_

    def get_similar_movies(self, movie_id, movie_features, n_similar=5):
        if movie_id not in movie_features:
            raise Exception("Film bulunamadı!")
        
        # Hedef filmi ölçeklendir
        target_movie = self.scaler.transform([movie_features[movie_id]])
        target_cluster = self.kmeans.predict(target_movie)[0]
        
        # Aynı kümedeki diğer filmleri bul
        similar_movies = []
        for other_id, features in movie_features.items():
            if other_id != movie_id:
                other_movie = self.scaler.transform([features])
                if self.kmeans.predict(other_movie)[0] == target_cluster:
                    # Benzerlik hesapla (Euclidean distance)
                    distance = np.linalg.norm(target_movie - other_movie)
                    similar_movies.append((other_id, distance))
        
        # En benzer filmleri döndür
        return [movie_id for movie_id, _ in sorted(similar_movies, key=lambda x: x[1])[:n_similar]] 