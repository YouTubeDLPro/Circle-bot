# Circle-bot

## Overview
This project, **Circle-bot**, automates the process of watching ads and claiming rewards in a Telegram airdrop project called "Circle." The bot processes multiple accounts, makes HTTP requests to the Circle platform, and logs results efficiently. Additionally, it includes a Flask server to provide a basic health check endpoint.

## Repository Structure
```
README.md          - Documentation for the project.
app.log            - Log file for recording application events and errors.
circle.py          - Main script for automating ad watching and claiming rewards.
data.txt           - Input file containing account details.
requirements.txt   - Python dependencies required to run the script.
```

## Features
- **Ad Reward Automation**: Automatically claims ad rewards for multiple accounts registered in the Circle project.
- **Logging**: Logs important events and errors to both the console and a log file.
- **Multithreading**: Simultaneously processes multiple accounts for faster execution.
- **Flask Server**: Provides a `/live` endpoint to check server status and confirm the bot is running.

## Installation

### Prerequisites
- Python 3.12
- pip (Python package installer)

### Steps
1. Clone this repository:
   ```bash
   git clone https://github.com/YouTubeDLPro/Circle-bot.git
   cd Circle-bot
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Prepare the `data.txt` file with your account details (see **Input File Format**).

## Input File Format
`data.txt` should contain account details in the following format:

```
tg_id=YOUR_TG_ID
tg_platform=YOUR_TG_PLATFORM
language=en
chat_type=sender
chat_instance=YOUR_CHAT_INSTANCE
top_domain=bot.toncircle.org

tg_id1=YOUR_TG_ID1
tg_platform1=YOUR_TG_PLATFORM1
language1=en
chat_type1=sender
chat_instance1=YOUR_CHAT_INSTANCE1
top_domain1=bot.toncircle.org

tg_id2=YOUR_TG_ID2
tg_platform2=YOUR_TG_PLATFORM2
language2=en
chat_type2=sender
chat_instance2=YOUR_CHAT_INSTANCE2
top_domain2=bot.toncircle.org
```

- If you want to add more accounts, follow the above format.
- If you only want to use one account, delete all other account configurations and leave only the main one.

## Usage

### Running the Script
Start the script by running:
```bash
python circle.py
```

### Flask Server
The script starts a Flask server to make the bot hostable on a hosting service provider. The server runs on port `1700` by default. If port `1700` is already in use, you will need to adjust the port number manually in the code to an available one. Note that ports `3000`, `9000`, and `7000` are also in use and cannot be used for this script. Ensure that the chosen port is not occupied by other services.

You can check the server status by visiting:
```
http://localhost:<port_number>/live
```

Response:
```json
{
  "message": "Server is running",
  "status": 200
}
```

## Logging
Logs are stored in `app.log` and provide details about:
- Errors
- Ad rewards claimed
- Missing account parameters

## Stopping the Script
You can stop the script gracefully by pressing `Ctrl+C`. This triggers the shutdown handler and stops all active threads.

## Notes
- Ensure all required keys (e.g., `tg_id`, `tg_platform`, etc.) are included in each account in `data.txt`. Missing keys will result in errors.
- Leave the `BLOCK_ID` as it is.
- Adjust the Flask server port in the code if `1700` is already in use, as ports `3000`, `9000`, `7000`, are already occupied.

## Dependencies
See `requirements.txt` for a list of Python libraries required to run the script. Install them using:
```bash
pip install -r requirements.txt
```

## License
This project is licensed under the MIT License. See `LICENSE` for more details.

