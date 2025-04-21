# Kümeleme Analizi API

Bu API, DBSCAN algoritması ve optimize edilmiş parametreler kullanarak ürünler, tedarikçiler ve ülkeler için kümeleme analizi sağlar.

## Kurulum

1. Gerekli paketleri yükleyin:
```bash
pip install -r requirements.txt
```

2. Veritabanı bağlantısı için `.env` dosyası oluşturun:
```
DATABASE_URL=postgresql://kullanici:sifre@localhost:5432/veritabani_adi
```

3. API'yi çalıştırın:
```bash
python main.py
```

## API Endpoint'leri

### 1. Ürün Kümeleme
Endpoint: `GET /product-clusters`

Ürünleri şu kriterlere göre kümeler:
- Ortalama satış fiyatı
- Satış sıklığı
- Sipariş başına ortalama miktar
- Benzersiz müşteri sayısı

### 2. Tedarikçi Kümeleme
Endpoint: `GET /supplier-clusters`

Tedarikçileri şu kriterlere göre kümeler:
- Tedarik edilen ürün sayısı
- Toplam satış miktarı
- Ortalama fiyat
- Benzersiz müşteri sayısı

### 3. Ülke Kümeleme
Endpoint: `GET /country-clusters`

Ülkeleri şu kriterlere göre kümeler:
- Toplam sipariş sayısı
- Ortalama sipariş değeri
- Sipariş başına ortalama ürün sayısı

## Kümeleme Detayları

- DBSCAN algoritması ve optimize edilmiş min_samples parametresi kullanılır
- Özellikler kümeleme öncesinde standardize edilir
- Aykırı değerler (küme -1) alışılmadık desenleri temsil eder
- Kümeleme parametrelerini optimize etmek için siluet skoru kullanılır

## Yanıt Formatı

Her endpoint aşağıdaki formatta kümeleri döndürür:
```json
[
    {
        "cluster": 0,
        "items": ["öğe1", "öğe2", ...],
        "metrics": {
            "metrik1": değer1,
            "metrik2": değer2,
            ...
        }
    },
    ...
]
```

## Notlar

- Küme -1, aykırı değerleri veya alışılmadık desenleri temsil eder
- Daha yüksek küme numaraları daha tipik desenleri gösterir
- Metrikler her küme içinde ortalaması alınır 