from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
from sqlalchemy import create_engine
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import DBSCAN
import numpy as np
from typing import List, Dict, Any
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Kümeleme Analizi API")

# CORS middleware - Farklı kaynaklardan gelen isteklere izin verir
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Veritabanı bağlantısı
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/dbname")
engine = create_engine(DATABASE_URL)

def optimize_min_samples(data: pd.DataFrame, eps: float = 0.5) -> int:
    """DBSCAN için min_samples parametresini siluet skoru kullanarak optimize eder"""
    from sklearn.metrics import silhouette_score
    
    best_score = -1
    best_min_samples = 2
    
    for min_samples in range(2, 11):
        dbscan = DBSCAN(eps=eps, min_samples=min_samples)
        labels = dbscan.fit_predict(data)
        
        # Birden fazla küme varsa skoru hesapla
        if len(set(labels)) > 1:
            score = silhouette_score(data, labels)
            if score > best_score:
                best_score = score
                best_min_samples = min_samples
    
    return best_min_samples

@app.get("/product-clusters")
async def get_product_clusters():
    """Satış desenlerine göre ürünleri kümeler"""
    try:
        # Ürün özelliklerini almak için sorgu
        query = """
        SELECT 
            p.product_id,
            AVG(od.unit_price) as avg_price,
            COUNT(od.order_id) as sales_frequency,
            AVG(od.quantity) as avg_quantity_per_order,
            COUNT(DISTINCT o.customer_id) as unique_customers
        FROM products p
        LEFT JOIN order_details od ON p.product_id = od.product_id
        LEFT JOIN orders o ON od.order_id = o.order_id
        GROUP BY p.product_id
        """
        
        df = pd.read_sql(query, engine)
        
        # Özellikleri hazırla
        features = df[['avg_price', 'sales_frequency', 'avg_quantity_per_order', 'unique_customers']]
        scaler = StandardScaler()
        scaled_features = scaler.fit_transform(features)
        
        # min_samples parametresini optimize et
        min_samples = optimize_min_samples(scaled_features)
        
        # DBSCAN uygula
        dbscan = DBSCAN(eps=0.5, min_samples=min_samples)
        df['cluster'] = dbscan.fit_predict(scaled_features)
        
        # Yanıtı hazırla
        clusters = df.groupby('cluster').agg({
            'product_id': list,
            'avg_price': 'mean',
            'sales_frequency': 'mean',
            'avg_quantity_per_order': 'mean',
            'unique_customers': 'mean'
        }).reset_index()
        
        return clusters.to_dict(orient='records')
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/supplier-clusters")
async def get_supplier_clusters():
    """Ürün performansına göre tedarikçileri kümeler"""
    try:
        query = """
        SELECT 
            s.supplier_id,
            COUNT(DISTINCT p.product_id) as product_count,
            SUM(od.quantity) as total_sales,
            AVG(od.unit_price) as avg_price,
            COUNT(DISTINCT o.customer_id) as unique_customers
        FROM suppliers s
        LEFT JOIN products p ON s.supplier_id = p.supplier_id
        LEFT JOIN order_details od ON p.product_id = od.product_id
        LEFT JOIN orders o ON od.order_id = o.order_id
        GROUP BY s.supplier_id
        """
        
        df = pd.read_sql(query, engine)
        
        # Özellikleri hazırla
        features = df[['product_count', 'total_sales', 'avg_price', 'unique_customers']]
        scaler = StandardScaler()
        scaled_features = scaler.fit_transform(features)
        
        # min_samples parametresini optimize et
        min_samples = optimize_min_samples(scaled_features)
        
        # DBSCAN uygula
        dbscan = DBSCAN(eps=0.5, min_samples=min_samples)
        df['cluster'] = dbscan.fit_predict(scaled_features)
        
        # Yanıtı hazırla
        clusters = df.groupby('cluster').agg({
            'supplier_id': list,
            'product_count': 'mean',
            'total_sales': 'mean',
            'avg_price': 'mean',
            'unique_customers': 'mean'
        }).reset_index()
        
        return clusters.to_dict(orient='records')
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/country-clusters")
async def get_country_clusters():
    """Sipariş desenlerine göre ülkeleri kümeler"""
    try:
        query = """
        SELECT 
            c.country,
            COUNT(DISTINCT o.order_id) as total_orders,
            AVG(od.unit_price * od.quantity) as avg_order_value,
            AVG(od.quantity) as avg_products_per_order
        FROM customers c
        LEFT JOIN orders o ON c.customer_id = o.customer_id
        LEFT JOIN order_details od ON o.order_id = od.order_id
        GROUP BY c.country
        """
        
        df = pd.read_sql(query, engine)
        
        # Özellikleri hazırla
        features = df[['total_orders', 'avg_order_value', 'avg_products_per_order']]
        scaler = StandardScaler()
        scaled_features = scaler.fit_transform(features)
        
        # min_samples parametresini optimize et
        min_samples = optimize_min_samples(scaled_features)
        
        # DBSCAN uygula
        dbscan = DBSCAN(eps=0.5, min_samples=min_samples)
        df['cluster'] = dbscan.fit_predict(scaled_features)
        
        # Yanıtı hazırla
        clusters = df.groupby('cluster').agg({
            'country': list,
            'total_orders': 'mean',
            'avg_order_value': 'mean',
            'avg_products_per_order': 'mean'
        }).reset_index()
        
        return clusters.to_dict(orient='records')
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 