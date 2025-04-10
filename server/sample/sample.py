import pandas as pd
import numpy as np

np.random.seed(42)
data = []

jumlah_per_kelas = 10000

labels = [
    'Sangat Baik',
    'Baik',
    'Cukup',
    'Buruk',
    'Sangat Buruk'
]

for label in labels:
    for _ in range(jumlah_per_kelas):
        if label == 'Sangat Baik':
            throughput = np.random.normal(350, 20)       # ≥ 300
            delay = np.random.normal(15, 3)              # ≤ 20
            jitter = np.random.normal(2, 1)              # ≤ 3
            packet_loss = np.random.normal(0.05, 0.02)   # ≤ 0.1
            availability = np.random.normal(99.95, 0.02)  # ≥ 99.9

        elif label == 'Baik':
            throughput = np.random.normal(250, 20)       # 200 – 299
            delay = np.random.normal(35, 7)              # 21 – 50
            jitter = np.random.normal(5, 1.5)            # 3.1 – 7
            packet_loss = np.random.normal(0.3, 0.1)     # 0.1 – 0.5
            availability = np.random.normal(99.5, 0.2)   # 99.0 – 99.8

        elif label == 'Cukup':
            throughput = np.random.normal(150, 30)       # 100 – 199
            delay = np.random.normal(80, 20)             # 51 – 120
            jitter = np.random.normal(10, 3)             # 7.1 – 15
            packet_loss = np.random.normal(1, 0.4)       # 0.5 – 2
            availability = np.random.normal(98.0, 0.5)   # 97 – 98.9

        elif label == 'Buruk':
            throughput = np.random.normal(75, 15)        # 50 – 99
            delay = np.random.normal(200, 40)            # 121 – 300
            jitter = np.random.normal(20, 5)             # 15.1 – 30
            packet_loss = np.random.normal(3, 0.8)       # 2.1 – 5
            availability = np.random.normal(93.0, 1.5)   # 90 – 96.9

        elif label == 'Sangat Buruk':
            throughput = np.random.normal(30, 10)        # < 50
            delay = np.random.normal(400, 50)            # > 300
            jitter = np.random.normal(40, 8)             # > 30
            packet_loss = np.random.normal(7, 2)         # > 5
            availability = np.random.normal(85.0, 2.5)   # < 90

        # Validasi nilai agar tetap logis
        throughput = max(0, throughput)
        delay = max(0, delay)
        jitter = max(0, jitter)
        packet_loss = min(max(0, packet_loss), 100)
        availability = min(max(0, availability), 100)

        data.append([throughput, delay, jitter,
                     packet_loss, availability, label])

# Simpan ke CSV
df = pd.DataFrame(data, columns=[
    "throughput", "delay", "jitter", "packet_loss", "availability", "label"
])
df.to_csv("qos_dataset_5skala.csv", index=False)

print("✅ Dataset berhasil disimpan sebagai 'qos_dataset_5skala.csv'")
print("📊 Jumlah total data:", len(df))
print(df['label'].value_counts())
