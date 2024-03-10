import pyttsx3
import datetime
import speech_recognition as sr
import pyjokes
import schedule
import time
from plyer import notification
import re
import json

# Initialize pyttsx3 engine
engine = pyttsx3.init()
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[1].id)  # Female voice
rate = engine.getProperty('rate')
engine.setProperty('rate', rate - 50)

REMINDERS_FILE = "reminders.json"

# Function to speak out the given text
def speak(audio):
    engine.say(audio)
    engine.runAndWait()

# Function to get the current time and speak it
def get_current_time():
    return datetime.datetime.now().strftime("%I:%M %p")

# Function to greet the user
def greet():
    speak("Hello user.")
    hour = datetime.datetime.now().hour
    if 6 <= hour < 12:
        speak("It's a nice morning, isn't it?") 
    elif 12 <= hour < 18:
        speak("It sure is one nice afternoon.")
    elif 18 <= hour < 24:
        speak("What a good evening it is.")
    else:
        speak("Good night user.")

    speak("I am your AI assistant. What are your plans?")

# Function to recognize user's speech input
def listen():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)

    try:
        print("Recognizing...")
        query = recognizer.recognize_google(audio, language='en-us')
        print("You said:", query)
        return query.lower()
    except sr.UnknownValueError:
        print("Sorry, I didn't catch that. Can you please repeat?")
    except sr.RequestError as e:
        print("Could not request results from Google Speech Recognition service; {0}".format(e))

# Function to show notification reminders
def remind(title):
    print(f"{title}: Time to {title.lower()}!")
    notification.notify(
        title=title,
        message=f"It's time for {title.lower()}!",
        app_name='My Application',
        timeout=5
    )

# Function to schedule a reminder
def schedule_reminder(title, schedule_time):
    schedule.every().day.at(schedule_time).do(remind, title)

def get_speech_input():
    recognizer = sr.Recognizer()
    microphone = sr.Microphone()

    with microphone as source:
        recognizer.adjust_for_ambient_noise(source)
        print("Listening... Speak your reminder title and time.")
        audio = recognizer.listen(source)

    try:
        user_input = recognizer.recognize_google(audio)
        print("You said:", user_input)
        return user_input
    except sr.UnknownValueError:
        print("Sorry, could not understand audio.")
    except sr.RequestError as e:
        print("Could not request results from Google Speech Recognition service; {0}".format(e))

    return None    

# Function to check and execute overdue reminders
def check_overdue_reminders():
    current_time = datetime.datetime.now().time()
    for reminder in reminders:
        reminder_time = datetime.datetime.strptime(reminder['time'], '%H:%M').time()
        if current_time > reminder_time:
            remind(reminder['title'])
            reminders.remove(reminder)  # Remove the reminder after triggering it

# Function to load reminders from file
def load_reminders():
    try:
        with open(REMINDERS_FILE, 'r') as file:
            reminders = json.load(file)
            return reminders
    except (FileNotFoundError, json.JSONDecodeError):
        return []

# Function to save reminders to file
def save_reminders(reminders):
    with open(REMINDERS_FILE, 'w') as file:
        json.dump(reminders, file)

# Main function to control the assistant
def main():
    global reminders
    reminders = load_reminders()
    greet()
    while True:
        schedule.run_pending()  # Check if any scheduled reminders are due
        query = listen()
        if query:
            if 'time' in query:
                speak(f"The current time is {get_current_time()}.")
            elif 'date' in query:
                today = datetime.datetime.now().strftime("%A, %B %d, %Y")
                speak(f"Today's date is {today}.")
            elif 'thank you' in query:
                speak("You're welcome!")
            elif 'how are you' in query:
                speak("I'm doing just fine. Thank you for asking!")
            elif 'go offline' in query:
                speak("Alright, I'll be here if you need me. Goodbye!")
                save_reminders(reminders)  # Save reminders before quitting
                quit()
                
            elif 'set a reminder' in query:
             speak("What should I remember?")
             title_and_time = get_speech_input()
             if title_and_time:
                try:
                    match = re.search(r'(\d{1,2})[:\.]?(\d{2})\s?(a\.?m\.?|p\.?m\.?)', title_and_time, re.IGNORECASE)
                    if match:
                        hour = int(match.group(1))
                        minute = int(match.group(2))
                        period = match.group(3).lower()
                        if period.startswith('p') and hour < 12:
                            hour += 12
                        elif period.startswith('a') and hour == 12:
                            hour = 0
                        time_str = f'{hour:02d}:{minute:02d}'
                        
                        title = re.sub(r'\s+at\s+' + match.group(0), '', title_and_time, flags=re.IGNORECASE)
                        
                        reminders.append({'title': title.strip(), 'time': time_str})
                        schedule_reminder(title.strip(), time_str)
                        speak(f"Reminder '{title.strip()}' scheduled for {time_str}")
                    else:
                        speak("Sorry, I couldn't recognize the time. Please try again.")
                except Exception as e:
                    speak(f"An error occurred: {e}")
               
            elif 'do i have any reminders' in query:
                if reminders:
                    speak("Here are your reminders:")
                    for reminder in reminders:
                        speak(f"Reminder for {reminder['title']} at {reminder['time']}.")
                else:
                    speak("You don't have any reminders.")
            elif 'joke' in query:
                speak(pyjokes.get_joke())

if __name__ == "__main__":
    main()
