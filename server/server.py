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
    print("Label yang didukung oleh model:", model.classes_)
except Exception as e:
    print(f"❌ Gagal memuat model: {e}")
    model = None

latest_results = []
results_lock = threading.Lock()


def get_ping_stats(host, count=3):
    try:
        output = subprocess.check_output(
            f"ping -n {count} {host}",
            shell=True,
            text=True,
            stderr=subprocess.DEVNULL
        )
        times = re.findall(r'time[=<]\s*(\d+)', output)
        times = list(map(int, times))
        if times:
            delay = np.mean(times)
            jitter = np.std(times)
            packet_loss = 100 - (len(times) / count * 100)
            return delay, jitter, packet_loss
    except Exception as e:
        print(f"⚠️ Gagal ping {host}: {e}")
    return None, None, 100.0


def get_throughput(url, timeout=10):
    try:
        start_time = time.time()
        response = requests.get(
            url,
            stream=True,
            timeout=timeout,
            verify=False,
            headers={'Cache-Control': 'no-cache'}
        )
        total_bytes = 0

        for chunk in response.iter_content(chunk_size=1024):
            if chunk:  # Filter out keep-alive chunks
                total_bytes += len(chunk)
                if time.time() - start_time > timeout:
                    break

        duration = time.time() - start_time
        if duration == 0:
            return 0.0
        speed_kbps = (total_bytes * 8) / duration / 1000
        return speed_kbps

    except Exception as e:
        print(f"⚠️ Gagal mengukur throughput: {e}")
        return None


def scan_device(ip, reference_throughput):
    delay, jitter, packet_loss = get_ping_stats(ip)
    if delay is None:
        return None

    throughput_kbps = simulate_throughput(reference_throughput, ip)

    availability = 100 - packet_loss
    if throughput_kbps < 100:
        availability -= min(10, max(0, 10 - (throughput_kbps / 10)))

    input_data = pd.DataFrame([{
        'throughput': throughput_kbps,
        'delay': delay,
        'jitter': jitter,
        'packet_loss': packet_loss,
        'availability': availability
    }])

    try:
        predicted_label = model.predict(input_data)[0]
    except Exception as e:
        print(f"⚠️ Gagal prediksi untuk {ip}: {e}")
        return None

    return {
        "ip": ip,
        "status": predicted_label,
        "throughput_kbps": round(throughput_kbps, 2),
        "throughput_mbps": round(throughput_kbps / 1000, 2),
        "delay_ms": round(delay, 2),
        "jitter_ms": round(jitter, 2),
        "packet_loss_percent": round(packet_loss, 2),
        "availability_percent": round(availability, 2)
    }


def simulate_throughput(base_throughput, ip):
    try:
        last_octet = int(ip.split('.')[-1])
        variation = (last_octet % 20) * 0.01
        return base_throughput * (1 + variation)
    except:
        return base_throughput


def background_scanner():
    global latest_results
    while True:
        if model is None:
            print("⏳ Menunggu model...")
            time.sleep(5)
            continue

        print("\n🔍 Memulai pemindaian jaringan...")

        base_ip = "110.0.2."
        ip_range = [f"{base_ip}{i}" for i in range(1, 255)]

        reference_throughput = get_throughput("http://speedtest.tele2.net/10MB.zip") or \
            get_throughput("https://speed.hetzner.de/100MB.bin") or \
            get_throughput("http://speedtest.nyc3.digitalocean.com/10mb.test")

        if reference_throughput is None:
            print("❌ Gagal mendapatkan throughput referensi, coba lagi...")
            time.sleep(10)
            continue

        print(
            f"📊 Throughput referensi: {reference_throughput:.2f} Kbps (~{reference_throughput/1000:.2f} Mbps)")

        results = []
        with ThreadPoolExecutor(max_workers=50) as executor:
            futures = [executor.submit(scan_device, ip, reference_throughput)
                       for ip in ip_range]
            for future in futures:
                result = future.result()
                if result:
                    results.append(result)

        with results_lock:
            latest_results = results

        print(f"\n✅ Pemindaian selesai. Perangkat terdeteksi: {len(results)}")
        for device in results:
            status = device["status"]
            color = (
                Fore.GREEN if status == "Sangat Baik" else
                Fore.CYAN if status == "Baik" else
                Fore.YELLOW if status == "Cukup" else
                Fore.RED if status == "Buruk" else
                Fore.MAGENTA
            )
            print(
                f"{color}IP: {device['ip']} | "
                f"Status: {status} | "
                f"Throughput: {device['throughput_mbps']:.2f} Mbps | "
                f"Delay: {device['delay_ms']} ms{Style.RESET_ALL}"
            )

        time.sleep(60)


@app.route("/api/network-status", methods=["GET"])
def get_network_status():
    with results_lock:
        if not latest_results:
            return jsonify({"error": "Data belum tersedia"}), 503
        return jsonify(latest_results)


if __name__ == "__main__":
    scanner_thread = threading.Thread(target=background_scanner, daemon=True)
    scanner_thread.start()
    app.run(host="0.0.0.0", port=5000, debug=False)
