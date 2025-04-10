from flask import Flask, jsonify
from flask_cors import CORS
import subprocess
import re
import joblib
import numpy as np
import time
import requests
import urllib3
import pandas as pd
from concurrent.futures import ThreadPoolExecutor
import threading
from colorama import Fore, Style

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

app = Flask(__name__)
CORS(app)

try:
    model = joblib.load("model/model-nb.sav")
    print("✅ Model berhasil dimuat.")
except Exception as e:
    print("❌ Gagal memuat model:", e)
    model = None

latest_results = []
results_lock = threading.Lock()


def get_ping_stats(host, count=3):
    try:
        output = subprocess.check_output(
            f"ping -n {count} {host}", shell=True, text=True, stderr=subprocess.DEVNULL)
        times = re.findall(r'time[=<]\s*(\d+)', output)
        times = list(map(int, times))
        if times:
            delay = np.mean(times)
            jitter = np.std(times)
            packet_loss = 100 - (len(times) / count * 100)
            return delay, jitter, packet_loss
    except:
        pass
    return None, None, 100.0


def get_throughput_manual(host):
    try:
        start = time.time()
        response = requests.get(host, stream=True, timeout=10, verify=False)
        total_bytes = sum(len(chunk)
                          for chunk in response.iter_content(chunk_size=1024))
        end = time.time()
        duration = end - start
        speed_kbps = (total_bytes * 8) / duration / 1000
        return speed_kbps
    except:
        return None


def simulate_throughput(base_throughput, ip):
    try:
        last_octet = int(ip.split('.')[-1])
        noise_factor = 1 + ((last_octet % 10) - 5) * 0.02
        return base_throughput * noise_factor
    except:
        return base_throughput


def scan_device(ip, global_throughput):
    delay, jitter, packet_loss = get_ping_stats(ip)
    if delay is None:
        return None

    throughput = simulate_throughput(global_throughput, ip)

    availability = 100 - packet_loss

    if throughput < 100: 
        availability -= 5

    input_data = pd.DataFrame([{
        'throughput': throughput,
        'delay': delay,
        'jitter': jitter,
        'packet_loss': packet_loss,
        'availability': availability
    }])

    prediction = model.predict(input_data)

    status = "SANGAT MACET" if prediction[0] == 4 else \
             "MACET" if prediction[0] == 3 else \
             "PADAT" if prediction[0] == 2 else \
             "LANCAR" if prediction[0] == 1 else \
             "SANGAT LANCAR"

    return {
        "ip": ip,
        "status": prediction[0],
        "throughput": round(throughput, 2),
        "delay": round(delay, 2),
        "jitter": round(jitter, 2),
        "packet_loss": round(packet_loss, 2),
        "availability": round(availability, 2)
    }


def background_scanner():
    global latest_results
    while True:
        if model is None:
            print("⛔ Model belum tersedia, lewati pemindaian.")
            time.sleep(30)
            continue

        print("\n📡 Memulai pemindaian jaringan...")
        base_ip = "192.168.10."
        ip_range = [f"{base_ip}{i}" for i in range(1, 255)]

        global_throughput = get_throughput_manual(
            "https://speed.hetzner.de/1MB.bin")
        if global_throughput is None:
            print("❌ Gagal mengukur throughput, lewati putaran ini.")
            time.sleep(30)
            continue

        results = []
        with ThreadPoolExecutor(max_workers=50) as executor:
            futures = executor.map(lambda ip: scan_device(
                ip, global_throughput), ip_range)
            results = [res for res in futures if res]

        with results_lock:
            latest_results = results

        print(f"\n✅ Pemindaian selesai. Jumlah hasil: {len(results)}")
        for r in results:
            color = Fore.RED if r["status"] == "SANGAT MACET" else Fore.YELLOW if r[
                "status"] == "MACET" else Fore.CYAN if r["status"] == "PADAT" else Fore.GREEN
            print(
                f"{color} - {r['ip']} => {r['status']} | Delay: {r['delay']}ms | Throughput: {r['throughput']}kbps | Availability: {r['availability']}%{Style.RESET_ALL}")

        time.sleep(60)


@app.route("/api/identifikasi-peforma", methods=["GET"])
def get_latest_results():
    with results_lock:
        if not latest_results:
            return jsonify({"message": "Belum ada hasil pemindaian"}), 503
        return jsonify(latest_results)


if __name__ == "__main__":
    threading.Thread(target=background_scanner, daemon=True).start()
    app.run(debug=True)
