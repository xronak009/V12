import telebot
import requests
from bs4 import BeautifulSoup
import os
import time

# Create the bot instance
bot = telebot.TeleBot('7532019270:AAHYj3_VyMkweJw52JRm9REt88V97YR6AYw')

# Replace with your actual API keys
API_KEY_1 = "AIzaSyBUSpLbjLNIqddIuF080dD8TqhOZ0Yvq3k"  # Your first API key
CUSTOM_SEARCH_ENGINE_ID_1 = "22424b52794b345b3"  # Your first Custom Search Engine ID

API_KEY_2 = "AIzaSyDb8d9WaUuK8YM2-3SF0e4slhjb0kHPIg0"  # Your second API key
CUSTOM_SEARCH_ENGINE_ID_2 = "90268fec69abb4116"  # Your second Custom Search Engine ID

# Owner user ID
OWNER_ID = 1192484969  # Replace with your actual user ID

# Database file
DATABASE_FILE = "database.txt"

# Anti-spam cooldown (seconds)
COOLDOWN = 5

# Dictionary to store user last command time
last_command_time = {}

# Check if database file exists, create it if not
if not os.path.exists(DATABASE_FILE):
    with open(DATABASE_FILE, "w") as f:
        pass

@bot.message_handler(commands=['start'])
def start_command(message):
    bot.reply_to(message, "Welcome to the Dork Bot! Use /register to register and then /dork [word] to search.")

@bot.message_handler(commands=['register'])
def register_command(message):
    user_id = message.from_user.id
    # Check if user already registered
    with open(DATABASE_FILE, "r") as f:
        registered_users = [line.strip() for line in f]
    if str(user_id) in registered_users:
        bot.reply_to(message, "You are already registered! ✅✨")
    else:
        # Register user
        with open(DATABASE_FILE, "a") as f:
            f.write(str(user_id) + "\n")
        bot.reply_to(message, "Registration successful! ✅")

@bot.message_handler(commands=['dork'])
def dork_command(message):
    user_id = message.from_user.id
    # Check if user is registered
    with open(DATABASE_FILE, "r") as f:
        registered_users = [line.strip() for line in f]
    if str(user_id) not in registered_users:
        bot.reply_to(message, "Please register first using /register..👾")
        return

    # Anti-spam check
    if user_id in last_command_time:
        if time.time() - last_command_time[user_id] < COOLDOWN and user_id != OWNER_ID:
            bot.reply_to(message, f"Please wait {COOLDOWN} seconds before using the /dork command again.")
            return

    try:
        args = message.text.split()
        if len(args) > 1:
            word = " ".join(args[1:])  # Join all words after '/dork'

            bot.reply_to(message, f"Wait, I'm searching for {word}. This may take a while....")

            # Define the number of results per page for each API
            results_per_page = 5  # Increase this value to fetch more results per API call.
            start_1 = 0
            start_2 = 0
            sites = []

            # Fetch results from API 1
            while True:
                time.sleep(1)  # Wait for 1 second before each API call

                url = f"https://www.googleapis.com/customsearch/v1?key={API_KEY_1}&cx={CUSTOM_SEARCH_ENGINE_ID_1}&q={word}&start={start_1}&num={results_per_page}"
                response = requests.get(url)
                data = response.json()

                if 'items' in data:
                    sites.extend([item['link'] for item in data['items']])
                    start_1 += results_per_page
                    if len(data['items']) < results_per_page:
                        break
                else:
                    break  # Stop if there are no more results

            # Fetch results from API 2
            while True:
                time.sleep(1)  # Wait for 1 second before each API call

                url = f"https://www.googleapis.com/customsearch/v1?key={API_KEY_2}&cx={CUSTOM_SEARCH_ENGINE_ID_2}&q={word}&start={start_2}&num={results_per_page}"
                response = requests.get(url)
                data = response.json()

                if 'items' in data:
                    sites.extend([item['link'] for item in data['items']])
                    start_2 += results_per_page
                    if len(data['items']) < results_per_page:
                        break
                else:
                    break  # Stop if there are no more results

            # Remove duplicate sites
            sites = list(dict.fromkeys(sites))

            if len(sites) > 0:
                with open(f"{word}.txt", "w", encoding="utf-8") as file:
                    for site in sites:
                        file.write(site + "\n")
                bot.send_document(message.chat.id, open(f"{word}.txt", 'rb'),
                                  caption=f"Found {len(sites)} sites.\n\n owner - @xRonak ⛈️")
                os.remove(f"{word}.txt")
            else:
                bot.reply_to(message, "No sites found..🥲")

        else:
            bot.reply_to(message, "Incorrect format. Use /dork [word]")
    except ValueError:
        bot.reply_to(message, "Incorrect format. Use /dork [word]")

    # Update last command time for the user
    last_command_time[user_id] = time.time()

@bot.message_handler(commands=['ping'])
def ping_command(message):
    start_time = time.time()
    bot.send_chat_action(message.chat.id, 'typing')  # Show typing action
    end_time = time.time()
    ping_ms = (end_time - start_time) * 1000
    bot.reply_to(message, f"Pong! 🏓 Bot latency: {ping_ms:.2f} ms")

# Start the bot
bot.polling()