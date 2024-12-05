import requests
import time
import logging
import sys
import random
from datetime import datetime
import threading
import signal
from flask import Flask, jsonify

# Flask server setup
app = Flask(__name__)

@app.route("/live", methods=["GET"])
def home():
    return jsonify({"message": "Server is running", "status": 200})

# Setup logging for debugging and error tracking
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Create handlers
console_handler = logging.StreamHandler(sys.stdout)
file_handler = logging.FileHandler('app.log', encoding='utf-8')

# Set log levels
console_handler.setLevel(logging.INFO)
file_handler.setLevel(logging.INFO)

# Formatter for logs
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)
file_handler.setFormatter(formatter)

# Add handlers to logger
logger.addHandler(console_handler)
logger.addHandler(file_handler)

# ANSI escape codes for color formatting
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
CYAN = "\033[96m"
RESET = "\033[0m"

# Headers for the requests
def build_headers(authorization):
    """
    Build headers for making HTTP requests.

    Args:
        authorization (str): The authorization token for the request.

    Returns:
        dict: A dictionary containing headers required for the HTTP request.
    """
    return {
        'accept': '*/*',
        'accept-language': 'en-US,en;q=0.9',
        'authorization': authorization,
        'cache-control': 'max-age=0',
        'content-type': 'application/json',
        'origin': 'https://bot.toncircle.org',
        'pragma': 'no-cache',
        'referer': 'https://bot.toncircle.org/',
        'x-requested-with': 'org.telegram.messenger',
    }

BLOCK_ID = 3852
stop_threads = False

def build_ad_url(tg_id, tg_platform, platform, language, chat_type, chat_instance, top_domain):
    return f"https://api.adsgram.ai/adv?blockId={BLOCK_ID}&tg_id={tg_id}&tg_platform={tg_platform}&platform={platform}&language={language}&chat_type={chat_type}&chat_instance={chat_instance}&top_domain={top_domain}"

def read_multiple_accounts(filename="data.txt"):
    accounts = []
    try:
        with open(filename, "r") as file:
            account_data = {}
            for line in file:
                line = line.strip()
                if not line:
                    if account_data:
                        accounts.append(account_data)
                        account_data = {}
                elif "=" in line:
                    key, value = line.split("=", 1)
                    clean_key = key.rstrip("0123456789")
                    account_data[clean_key.strip()] = value.strip()

            if account_data:
                accounts.append(account_data)

        required_keys = ['tg_id', 'tg_platform', 'language', 'chat_type', 'chat_instance', 'top_domain']
        for account in accounts:
            missing_keys = [key for key in required_keys if key not in account]
            if missing_keys:
                logger.error(f"Missing keys in account: {', '.join(missing_keys)}")
                return None

        return accounts
    except FileNotFoundError:
        logger.error(f"{RED}File {filename} not found.{RESET}")
        return None
    except Exception as e:
        logger.error(f"{RED}Error reading accounts from file: {e}{RESET}")
        return None

def claim_ad(account, headers):
    ad_url = build_ad_url(
        account['tg_id'], account['tg_platform'], 'Win32',
        account['language'], account['chat_type'],
        account['chat_instance'], account['top_domain']
    )
    try:
        response = requests.get(ad_url, headers=headers)

        if response.status_code == 200:
            ad_data = response.json()
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            tracking_urls = [tracking.get("value") for tracking in ad_data.get("banner", {}).get("trackings", [])]
            if not tracking_urls:
                logger.error("No Claim URLs found.")
                return False

            for tracking_url in tracking_urls:
                try:
                    tracking_response = requests.get(tracking_url)
                    if tracking_response.status_code != 200:
                        logger.error(f"Failed tracking request: {tracking_url}")
                        return False
                except Exception as e:
                    logger.error(f"Error during tracking request: {e}")
                    return False

            return True
        else:
            logger.error(f"Failed to claim ad: {ad_url}, Response: {response.text}")
            return False
    except Exception as e:
        logger.error(f"Error claiming ad: {e}")
        return False

def watch_ads_for_account(account):
    global stop_threads
    headers = build_headers(account.get("authorization", ""))

    if not all(key in account for key in ['tg_id', 'tg_platform', 'language', 'chat_type', 'chat_instance', 'top_domain']):
        logger.error("Missing required parameters in account.")
        return

    try:
        while not stop_threads:
            ad_claimed = claim_ad(account, headers)

            if ad_claimed:
                logger.info(f"{GREEN}✨ Ad Reward Claimed for account {account['tg_id']}, added +1000 Sparks!{RESET}")
                break
            else:
                logger.error(f"Retrying for account {account['tg_id']}...")
    except Exception as e:
        logger.error(f"Error in account {account['tg_id']}: {e}")

def wait_between_ads(wait_time):
    global stop_threads
    logger.info(f"⏳ Waiting {wait_time} seconds before the next round...")
    while wait_time > 0 and not stop_threads:
        minutes, seconds = divmod(wait_time, 60)
        sys.stdout.write(f"\r⏳ Next round in: {minutes:02}:{seconds:02}  ")
        sys.stdout.flush()
        time.sleep(1)
        wait_time -= 1
    print()

def watch_ads():
    global stop_threads
    accounts = read_multiple_accounts("data.txt")
    if not accounts:
        return

    while not stop_threads:
        logger.info("Starting a new ad-watching round for all accounts...")
        threads = []
        for account in accounts:
            thread = threading.Thread(target=watch_ads_for_account, args=(account,))
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        logger.info("Completed ad-watching for all accounts in this round.")

        if not stop_threads:
            wait_time = random.randint(150, 180)
            wait_between_ads(wait_time)

def shutdown_handler(signum, frame):
    global stop_threads
    logger.info(f"{RED}Shutting down...{RESET}")
    stop_threads = True

signal.signal(signal.SIGINT, shutdown_handler)

# Run Flask server in a separate thread
flask_thread = threading.Thread(target=app.run, kwargs={"host": "0.0.0.0", "port": 1700})
flask_thread.daemon = True
flask_thread.start()

# Start the ad-watching process
watch_ads()
