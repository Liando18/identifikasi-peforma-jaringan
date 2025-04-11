import pandas as pd
import numpy as np


def generate_data(label, n=10000):
    if label == "Sangat Baik":
        throughput = np.random.uniform(10001, 20000, n)
        delay = np.random.uniform(1, 49, n)
        jitter = np.random.uniform(0, 9, n)
        packet_loss = np.random.uniform(0.0, 0.4, n)
        availability = np.random.uniform(99.99, 100, n)
    elif label == "Baik":
        throughput = np.random.uniform(5000, 10000, n)
        delay = np.random.uniform(50, 100, n)
        jitter = np.random.uniform(10, 20, n)
        packet_loss = np.random.uniform(0.5, 1.0, n)
        availability = np.random.uniform(99.0, 99.98, n)
    elif label == "Cukup":
        throughput = np.random.uniform(2000, 4999, n)
        delay = np.random.uniform(100, 200, n)
        jitter = np.random.uniform(20, 40, n)
        packet_loss = np.random.uniform(1.0, 2.0, n)
        availability = np.random.uniform(97.0, 98.99, n)
    elif label == "Buruk":
        throughput = np.random.uniform(1000, 1999, n)
        delay = np.random.uniform(200, 300, n)
        jitter = np.random.uniform(40, 60, n)
        packet_loss = np.random.uniform(2.0, 5.0, n)
        availability = np.random.uniform(95.0, 96.99, n)
    elif label == "Sangat Buruk":
        throughput = np.random.uniform(0, 999, n)
        delay = np.random.uniform(301, 600, n)
        jitter = np.random.uniform(61, 100, n)
        packet_loss = np.random.uniform(5.0, 10.0, n)
        availability = np.random.uniform(50.0, 94.99, n)

    data = pd.DataFrame({
        "throughput": throughput,
        "delay": delay,
        "jitter": jitter,
        "packet_loss": packet_loss,
        "availability": availability,
        "label": label
    })
    return data


labels = ["Sangat Baik", "Baik", "Cukup", "Buruk", "Sangat Buruk"]
full_data = pd.concat([generate_data(label)
                      for label in labels], ignore_index=True)

full_data.to_csv("sample-fix.csv", index=False)
