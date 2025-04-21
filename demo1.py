import numpy as np
import pandas as pd
from faker import Faker
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report
import matplotlib.pyplot as plt
import seaborn as sns

# Sahte veri üreteci oluştur
fake = Faker()

# Başvuru verilerini üreten fonksiyon
def generate_recruitment_data(num_samples=200):
    data = []
    for _ in range(num_samples):
        # Rastgele tecrübe yılı (0-10 arası)
        tecrube_yili = fake.random.uniform(0, 10)
        # Rastgele teknik sınav puanı (0-100 arası)
        teknik_puan = fake.random.uniform(0, 100)
        
        # İşe alım kriteri:
        # Tecrübesi 2 yıldan az VE sınav puanı 60'tan düşük olanlar işe alınmıyor
        if tecrube_yili < 2 and teknik_puan < 60:
            etiket = 1  # İşe alınmadı
        else:
            etiket = 0  # İşe alındı
            
        data.append({
            'tecrube_yili': tecrube_yili,
            'teknik_puan': teknik_puan,
            'etiket': etiket
        })
    
    return pd.DataFrame(data)

# 200 adet başvuru verisi üret
df = generate_recruitment_data(200)

# Özellikler ve hedef değişkeni ayır
X = df[['tecrube_yili', 'teknik_puan']]
y = df['etiket']

# Veriyi eğitim ve test setlerine ayır (%80 eğitim, %20 test)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Veriyi ölçeklendir (StandardScaler ile)
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# SVM modelini oluştur ve eğit
model = SVC(kernel='linear')
model.fit(X_train_scaled, y_train)

# Test seti üzerinde tahmin yap
y_pred = model.predict(X_test_scaled)

# Model performansını değerlendir
print("Doğruluk Skoru:", accuracy_score(y_test, y_pred))
print("\nKarışıklık Matrisi:")
print(confusion_matrix(y_test, y_pred))
print("\nSınıflandırma Raporu:")
print(classification_report(y_test, y_pred))

# Karar sınırını görselleştiren fonksiyon
def plot_decision_boundary():
    plt.figure(figsize=(10, 6))
    
    # Eğitim verilerini çiz
    plt.scatter(X_train_scaled[y_train == 0][:, 0], X_train_scaled[y_train == 0][:, 1], 
                color='blue', label='İşe Alındı')
    plt.scatter(X_train_scaled[y_train == 1][:, 0], X_train_scaled[y_train == 1][:, 1], 
                color='red', label='İşe Alınmadı')
    
    # Karar sınırını çiz
    ax = plt.gca()
    xlim = ax.get_xlim()
    ylim = ax.get_ylim()
    
    # Karar sınırı için ızgara oluştur
    xx = np.linspace(xlim[0], xlim[1], 30)
    yy = np.linspace(ylim[0], ylim[1], 30)
    YY, XX = np.meshgrid(yy, xx)
    xy = np.vstack([XX.ravel(), YY.ravel()]).T
    Z = model.decision_function(xy).reshape(XX.shape)
    
    # Karar sınırını ve marjini çiz
    ax.contour(XX, YY, Z, colors='k', levels=[-1, 0, 1], 
               alpha=0.5, linestyles=['--', '-', '--'])
    
    plt.xlabel('Tecrübe Yılı (Ölçeklendirilmiş)')
    plt.ylabel('Teknik Puan (Ölçeklendirilmiş)')
    plt.title('SVM Karar Sınırı')
    plt.legend()
    plt.show()

# Görselleştirmeyi göster
plot_decision_boundary()

# Kullanıcıdan girdi alarak tahmin yapan fonksiyon
def predict_candidate():
    print("\nAday Değerlendirme Sistemi")
    print("-------------------------")
    tecrube = float(input("Adayın tecrübe yılını girin (0-10): "))
    puan = float(input("Adayın teknik sınav puanını girin (0-100): "))
    
    # Girdiyi ölçeklendir
    input_data = scaler.transform([[tecrube, puan]])
    
    # Tahmin yap
    prediction = model.predict(input_data)[0]
    
    if prediction == 0:
        print("\nSonuç: Aday İŞE ALINDI!")
    else:
        print("\nSonuç: Aday İŞE ALINMADI!")

# Tahmin fonksiyonunu çağır
predict_candidate() 