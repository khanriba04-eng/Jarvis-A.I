import pyttsx3
import speech_recognition as sr
import webbrowser
import datetime
import requests

#-------------greet user-------------------------------
def greet_user():
    hour = datetime.datetime.now().hour
    if 5 <= hour < 12:
        greeting = "Good morning!"
    elif 12 <= hour < 17:
        greeting = "Good afternoon!"
    else:
        greeting = "Good evening!"
    say(f"{greeting} I am Jarvis AI. How can I assist you today?")


# ------------------- Text-to-Speech ------------------

engine = pyttsx3.init()
engine.setProperty('rate', 150)
engine.setProperty('volume', 1.0)

def say(text):
    print(f"Jarvis says: {text}")
    engine.say(text)
    engine.runAndWait()
# ------------------- Voice Command -------------------
def takeCommand():
    r = sr.Recognizer()
    try:
        with sr.Microphone() as source:
            print("Listening...")
            r.adjust_for_ambient_noise(source, duration=1)
            audio = r.listen(source)
            query = r.recognize_google(audio, language="en-in")
            print("Recognized:", query)
            return query.lower()
    except OSError:
        say("No microphone detected. Please connect a microphone.")
        return ""
    except sr.UnknownValueError:
        print("Could not understand audio")
        return ""
    except sr.RequestError:
        print("Speech service error")
        return ""


# ------------------- Weather Function -------------------
def get_weather_by_address(address):
    api_key = "79147b3119253ca16547282c888e102e"
    url = f"http://api.openweathermap.org/data/2.5/weather?q={address}&appid={api_key}&units=metric"

    try:
        response = requests.get(url)
        data = response.json()
        if data.get("cod") != 200:
            return "Sorry, I couldn't find the weather for that place."

        city = data["name"]
        weather = data["weather"][0]["description"]
        temp = data["main"]["temp"]
        humidity = data["main"]["humidity"]

        weather_report = (
            f"Location: {city}. "
            f"Weather: {weather}. "
            f"Temperature: {temp} degree Celsius. "
            f"Humidity: {humidity} percent."
        )
        return weather_report
    except requests.exceptions.RequestException:
        return "Sorry, there was an error connecting to the weather service."

# ---------------- Parse time helper ----------------
def parse_time(reminder_time):
    reminder_time = reminder_time.lower().strip()

    # Handle AM/PM formats
    if "am" in reminder_time or "pm" in reminder_time:
        parts = reminder_time.replace("am", "").replace("pm", "").strip()

        if ":" in parts:
            hour, minute = map(int, parts.split(":"))
        else:
            # If user says just "5 pm" or "5 am"
            hour = int(parts)
            minute = 0

        if "pm" in reminder_time and hour != 12:
            hour += 12
        if "am" in reminder_time and hour == 12:
            hour = 0
        return hour, minute

    # Handle 24-hour format (HH:MM)
    if ":" in reminder_time:
        return map(int, reminder_time.split(":"))

    # Handle 4-digit format (HHMM)
    if len(reminder_time) == 4 and reminder_time.isdigit():
        return int(reminder_time[:2]), int(reminder_time[2:])

    raise ValueError("Invalid time format")


# ---------------- Reminder storage ----------------
reminders = []


# ---------------- Set reminder ----------------
def set_reminder():
    say("What should I remind you about?")
    reminder_text = takeCommand()
    if not reminder_text:
        say("I didn't catch that. Reminder not set.")
        return

    say("At what time should I remind you? You can say things like '5:30 PM', '1730', or '17:30'.")
    reminder_time = takeCommand()

    try:
        reminder_hour, reminder_minute = parse_time(reminder_time)

        reminder_datetime = datetime.datetime.now().replace(
            hour=reminder_hour, minute=reminder_minute, second=0, microsecond=0
        )
        if reminder_datetime < datetime.datetime.now():
            reminder_datetime += datetime.timedelta(days=1)

        reminders.append((reminder_datetime, reminder_text))
        say(f"Reminder set for {reminder_hour:02d}:{reminder_minute:02d} to {reminder_text}")
    except:
        say("Invalid time format. Please try again with HH:MM, HHMM, or AM/PM format.")


# ---------------- Check reminders ----------------
def check_reminders():
    now = datetime.datetime.now()
    for reminder in reminders[:]:
        reminder_time, reminder_text = reminder
        if now >= reminder_time:
            say(f"Reminder: {reminder_text}")
            reminders.remove(reminder)
#----------------reading news---------------------------
import time

def read_news():
    api_key = "19b6d88810f64e129530a1a23080e798"
    url = f"https://newsapi.org/v2/top-headlines?country=us&apiKey={api_key}"
    response = requests.get(url)
    news_data = response.json()

    if news_data["status"] == "ok" and news_data["articles"]:
        for i, article in enumerate(news_data["articles"][:5], start=1):
            headline = article.get("title", "No headline available")
            source = article.get("source", {}).get("name", "Unknown source")
            say(f"News {i}: {headline} — from {source}")
            time.sleep(5)  # Pause between headlines
    else:
        say("No news headlines available right now. Please try again later.")


# ------------------- Main Program -------------------
def main():
    greet_user()
    site_list = [
        ["youtube", "https://youtube.com"],
        ["google", "https://google.com"],
        ["wikipedia", "https://wikipedia.com"]
    ]

    while True:
        query = takeCommand()
        if query == "":
            continue

        # --- Open websites ---
        opened_site = False
        for s in site_list:
            if f"open {s[0]}" in query:
                say(f"Opening {s[0]}")
                webbrowser.open(s[1])
                opened_site = True
                break
        if opened_site:
            continue

        # --- Tell time ---
        if "the time" in query:
            now = datetime.datetime.now()
            say(f"The time is {now.hour} hours {now.minute} minutes and {now.second} seconds")
            continue

        # --- Weather ---
        if "weather" in query:
            say("Please tell me the location")
            address = takeCommand()
            if address:
                report = get_weather_by_address(address)
                print(report)
                say(report)
            continue
        #----------reminder------
        if "reminder" in query or "remind me" in query:
            set_reminder()
            continue
        if "news" in query or "read news" in query:
            read_news()
            continue
        # --- Exit Jarvis ---
        if "exit" in query or "sleep" in query or "stop" in query:
            say("Goodbye!")
            break

        # --- Fallback ---
        say("I didn't understand that. Please try again.")


# ------------------- Run -------------------
if __name__ == "__main__":
    main()
