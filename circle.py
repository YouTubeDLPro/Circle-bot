import os  # Added for extracting file name from path
import requests
import time
import logging
import sys
import random
from datetime import datetime
import threading
import signal
import os

# Clear terminal before starting
os.system('cls' if os.name == 'nt' else 'clear')

# Global flag to stop threads
stop_threads = False

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

def display_banner(filename, account_count):
    """
    Display the ASCII banner with file details.

    Args:
        filename (str): Name of the file used for retrieving accounts.
        account_count (int): Number of accounts in the file.
    """
    banner = f"""
{CYAN}
 ██████╗██╗██████╗  ██████╗██╗     ███████╗    ██████╗  ██████╗ ████████╗
██╔════╝██║██╔══██╗██╔════╝██║     ██╔════╝    ██╔══██╗██╔═══██╗╚══██╔══╝
██║     ██║██████╔╝██║     ██║     █████╗      ██████╔╝██║   ██║   ██║   
██║     ██║██╔══██╗██║     ██║     ██╔══╝      ██╔══██╗██║   ██║   ██║   
╚██████╗██║██║  ██║╚██████╗███████╗███████╗    ██████╔╝╚██████╔╝   ██║   
 ╚═════╝╚═╝╚═╝  ╚═╝ ╚═════╝╚══════╝╚══════╝    ╚═════╝  ╚═════╝    ╚═╝   

{RESET}    File: {YELLOW}{filename}{RESET}
    Accounts Loaded: {GREEN}{account_count}{RESET}
    Always use 'git pull' to update the script to the latest version..!
    """
    print(banner)

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
    """
    Reads and parses account details from the specified file.
    Includes only accounts with numerical suffixes in keys and excludes placeholders.

    Args:
        filename (str): Path to the file containing account details.

    Returns:
        list: A list of valid accounts.
    """
    accounts = []
    placeholder_values = ["YOUR_TG_ID", "YOUR_TG_PLATFORM", "YOUR_CHAT_INSTANCE"]
    numerical_suffix_accounts = {}

    try:
        with open(filename, "r") as file:
            for line in file:
                line = line.strip()
                if not line:
                    # Add completed account data and reset
                    if numerical_suffix_accounts:
                        if all(numerical_suffix_accounts.values()) and not any(value in placeholder_values for value in numerical_suffix_accounts.values()):
                            accounts.append(numerical_suffix_accounts)
                        numerical_suffix_accounts = {}
                elif "=" in line:
                    key, value = line.split("=", 1)
                    # Check if key ends with a number
                    if key[-1].isdigit():
                        clean_key = key.rstrip("0123456789")
                        numerical_suffix_accounts[clean_key.strip()] = value.strip()

            # Add the last account if it's valid
            if numerical_suffix_accounts and all(numerical_suffix_accounts.values()) and not any(value in placeholder_values for value in numerical_suffix_accounts.values()):
                accounts.append(numerical_suffix_accounts)

        # Display banner with valid account count
        file_name_only = os.path.basename(filename)
        display_banner(file_name_only, len(accounts))
        return accounts

    except FileNotFoundError:
        logger.error(f"{RED}File {filename} not found.{RESET}")
        file_name_only = os.path.basename(filename)
        display_banner(file_name_only, 0)  # Show banner even if the file is missing
        return None
    except Exception as e:
        logger.error(f"{RED}Error reading accounts from file: {e}{RESET}")
        file_name_only = os.path.basename(filename)
        display_banner(file_name_only, 0)  # Show banner even if there's an error
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
    print()
    logger.info(f"{RED}Thank you for using me. Goodbye...{RESET}")
    stop_threads = True

signal.signal(signal.SIGINT, shutdown_handler)

# Start the ad-watching process
watch_ads()
