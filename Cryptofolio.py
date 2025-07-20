import requests
import json
import sys
from datetime import datetime

RISK_KEYWORDS = ['mixer', 'darknet', 'scam', 'fraud', 'gambling', 'ransomware']

def analyze_address(address, blockchain="bitcoin"):
    print(f"[+] Анализ адреса: {address} ({blockchain})")

    # Blockchair API
    meta_url = f"https://api.blockchair.com/{blockchain}/dashboards/address/{address}"
    labels_url = f"https://api.blockchair.com/{blockchain}/addresses/{address}?limit=1"

    try:
        r_meta = requests.get(meta_url).json()
        r_labels = requests.get(labels_url).json()
    except Exception as e:
        print(f"[!] Ошибка запроса: {e}")
        return

    data = r_meta.get("data", {}).get(address, {})
    if not data:
        print("[!] Нет данных по адресу.")
        return

    # Общая статистика
    address_info = data.get("address", {})
    transactions = address_info.get("transaction_count", 0)
    balance = int(address_info.get("balance", 0)) / 1e8

    print(f" - Баланс: {balance:.8f} BTC")
    print(f" - Количество транзакций: {transactions}")
    print(f" - Первая активность: {address_info.get('first_seen_receiving')}")
    print(f" - Последняя активность: {address_info.get('last_seen_spending')}")

    # Проверка на метки (биржи, миксеры и т.п.)
    labels = r_labels.get("data", [{}])[0].get("address", {}).get("annotation", "None")
    print(f" - Метка: {labels}")

    # Эвристический риск-анализ
    risk_score = 0
    risk_factors = []

    if any(kw in str(labels).lower() for kw in RISK_KEYWORDS):
        risk_score += 50
        risk_factors.append("⚠ Метка содержит рискованные ключевые слова")

    if transactions > 1000:
        risk_score += 10
        risk_factors.append("Высокая активность")

    if balance == 0:
        risk_score += 5
        risk_factors.append("Нулевой баланс")

    print(f" - Эвристический риск: {risk_score}/100")
    for rf in risk_factors:
        print(f"   → {rf}")

    print("\n✔️ Анализ завершён.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Использование: python cryptofolio.py <crypto_address> [blockchain]")
    else:
        address = sys.argv[1]
        blockchain = sys.argv[2] if len(sys.argv) > 2 else "bitcoin"
        analyze_address(address, blockchain)
