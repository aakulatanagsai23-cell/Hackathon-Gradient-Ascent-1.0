import os
import requests
from requests import get
import wikipedia
import webbrowser
import pywhatkit
import pyautogui
from sklearn.svm import SVC
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
import nltk
import random
import speech_recognition as sr
import nltk
nltk.download('punkt')
nltk.download('stopwords')
import pyttsx3
import datetime
import cv2
import warnings
import PyPDF2
from time import sleep

warnings.simplefilter('ignore')

engine = pyttsx3.init()
# voices = engine.getProperty('voices')
Id = r'HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech\Voices\Tokens\TTS_MS_EN-US_ZIRA_11.0'
engine.setProperty('voice', Id)

dictapp = {"chrome": "chrome","paint": "mspaint","word": "winword","powerpoint": "powerpnt","calculator": "calc","mail": "outlook","notepad": "notepad","excel": "excel","file explorer": "explorer","photos": "Microsoft.Photos_8wekyb3d8bbwe!App","calendar": "outlookcal:","settings": "ms-settings:","snipping tool": "SnippingTool","Spider":"Spyder"}


context = {"last_opened_app": None, "user_name": None}  # type: dict[str, str | None]
# text to speech
def speak(audio):
    global engine
    try:
        engine.say(audio)
        sleep(len(audio.split())/2) # /2 for 120 wpm
        sleep(len(audio.split('.'))/2) 
        engine.runAndWait()
    except Exception as e:
        print(f"pyttsx3 error: {e}. Reinitializing engine.")
        engine = pyttsx3.init()
        Id = r'HKEY_LOCAL_MACHINE\\SOFTWARE\\Microsoft\\Speech\\Voices\\Tokens\\TTS_MS_EN-US_ZIRA_11.0'
        engine.setProperty('voice', Id)
        engine.say(audio)
        engine.runAndWait()


# convert voice into text
def takecommand():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        r.pause_threshold = 1
        r.energy_threshold = 5
        audio = r.listen(source, 0, 4)

    try:
        print("Recognizing..")
        query = r.recognize_google(audio, language="en-IN")

        return query

    except Exception as e:
        speak("Say that again please")
        return "none"


intents = {
    "capabilities": {
        "patterns": ["what can you do", "tell me your features", "list your capabilities", "what do you know"],
        "responses": [
                '''I am Leo, your virtual assistant. Here are some things I can do:,
                Open and close applications like Chrome, Paint, Word, etc.
                Provide current time and weather information.
                Fetch the latest news updates.
                Play music and recommend songs.
                Answer general knowledge questions using Wikipedia.
                Open websites and perform web searches.
                Interact with your computer, like opening the camera or checking the IP address.
                And much more! Feel free to ask me anything.'''
        ]
    },
        "greetings": {
            "patterns": ["hello", "hi", "hey", "howdy", "greetings", "good morning", "good afternoon", "good evening",
                        "hi there", "hey there", "what's up", "hello there"],
            "responses": ["Hello! How can I assist you?", "Hi there!", "Hey! What can I do for you?",
                        "Howdy! What brings you here?", "Greetings! How may I help you?",
                        "How can I be of service?", "What do you need assistance with?",
                        "How may I assist you?", "Hey there! How can I help?", "Hi! What's on your mind?",
                        "Hello there! How can I assist you today?"]
    },

        "goodbye": {
            "patterns": ["bye", "see you later", "goodbye", "farewell", "take care", "until next time", "bye bye",
                        "catch you later", "have a good one", "so long"],
            "responses": ["Goodbye!", "See you later!", "Have a great day!", "Farewell! Take care.",
                        "Goodbye! Until next time.", "Take care! Have a wonderful day.", "Bye bye!", "Catch you later!",
                        "Have a good one!", "So long!"]
    },
        "gratitude": {
            "patterns": ["thank you", "thanks", "appreciate it", "thank you so much", "thanks a lot", "much appreciated"],
            "responses": ["You're welcome!", "Happy to help!", "Glad I could assist.", "Anytime!",
                        "You're welcome! Have a great day.", "No problem!"]
        },
        "apologies": {
            "patterns": ["sorry", "my apologies", "apologize", "I'm sorry"],
            "responses": ["No problem at all.", "It's alright.", "No need to apologize.", "That's okay.",
                        "Don't worry about it.", "Apology accepted."]
        },
        "positive_feedback": {
            "patterns": ["great job", "well done", "awesome", "fantastic", "amazing work", "excellent"],
            "responses": ["Thank you! I appreciate your feedback.", "Glad to hear that!", "Thank you for the compliment!",
                        "I'm glad I could meet your expectations.", "Your words motivate me!",
                        "Thank you for your kind words."]
        },
        "negative_feedback": {
            "patterns": ["not good", "disappointed", "unsatisfied", "poor service", "needs improvement", "could be better"],
            "responses": ["I'm sorry to hear that. Can you please provide more details so I can assist you better?",
                        "I apologize for the inconvenience. Let me help resolve the issue.",
                        "I'm sorry you're not satisfied. Please let me know how I can improve.",
                        "Your feedback is valuable. I'll work on improving."]
        },
        "weather": {
            "patterns": ["what's the weather like?", "weather forecast", "is it going to rain today?", "temperature today",
                        "weather report", "tell me the weather", "how's the weather today"],
            "responses": ["Sure, checking the weather for you..."],
            "action": "get_weather"
        },
        "help": {
            "patterns": ["help", "can you help me?", "I need assistance", "support"],
            "responses": ["Sure, I'll do my best to assist you.", "Of course, I'm here to help!", "How can I assist you?",
                        "I'll help you with your query."]
        },
        "time": {
            "patterns": ["what's the time?", "current time", "time please", "what time is it?", "tell me the time"],
            "responses": ["Sure, checking the time for you..."],
            "action": "get_time"
        },
        "jokes": {
            "patterns": ["tell me a joke", "joke please", "got any jokes?", "make me laugh"],
            "responses": ["Why don't we ever tell secrets on a farm? Because the potatoes have eyes and the corn has ears!",
                        "What do you get when you cross a snowman and a vampire? Frostbite!",
                        "Why was the math book sad? Because it had too many problems!"]
        },
        "music": {
            "patterns": ["play music", "music please", "song recommendation", "music suggestion"],
            "responses": ["Sure, playing some music for you!", "Here's a song you might like: [song_name]",
                        "How about some music?"]
        },
        "food": {
            "patterns": ["recommend a restaurant", "food places nearby", "what's good to eat?", "restaurant suggestion"],
            "responses": ["Sure, here are some recommended restaurants: [restaurant_names]",
                        "Hungry? Let me find some good food places for you!",
                        "I can suggest some great places to eat nearby."]
        },
        "news": {
            "patterns": ["latest news", "news updates", "what's happening?", "current events", "tell me the news"],
            "responses": ["Sure, fetching the latest news for you..."],
            "action": "get_news"
        },
        "movies": {
            "patterns": ["movie suggestions", "recommend a movie", "what should I watch?", "best movies"],
            "responses": ["How about watching [movie_name]?", "Here's a movie suggestion for you.",
                        "Let me recommend some great movies!"]
        },
        "sports": {
            "patterns": ["sports news", "score updates", "latest sports events", "upcoming games"],
            "responses": ["I'll get you the latest sports updates.", "Stay updated with the current sports events!",
                        "Let me check the sports scores for you."]
        },
        "gaming": {
            "patterns": ["video game recommendations", "best games to play", "recommend a game", "gaming suggestions"],
            "responses": ["How about trying out [game_name]?", "Here are some gaming suggestions for you!",
                        "Let me recommend some fun games to play!"]
        },
        "tech_support": {
            "patterns": ["technical help", "computer issues", "troubleshooting", "IT support"],
            "responses": ["I can assist with technical issues. What problem are you facing?",
                        "Let's troubleshoot your technical problem together.",
                        "Tell me about the technical issue you're experiencing."]
        },
        "book_recommendation": {
            "patterns": ["recommend a book", "good books to read", "book suggestions", "what should I read?"],
            "responses": ["How about reading [book_title]?", "I've got some great book recommendations for you!",
                        "Let me suggest some interesting books for you to read."]
        },
        "fitness_tips": {
            "patterns": ["fitness advice", "workout tips", "exercise suggestions", "healthy habits"],
            "responses": ["Staying fit is important! Here are some fitness tips: [fitness_tips]",
                        "I can help you with workout suggestions and fitness advice.",
                        "Let me provide some exercise recommendations for you."]
        },
        "travel_recommendation": {
            "patterns": ["travel suggestions", "places to visit", "recommend a destination", "travel ideas"],
            "responses": ["Looking for travel recommendations? Here are some great destinations: [travel_destinations]",
                        "I can suggest some amazing places for your next travel adventure!",
                        "Let me help you with travel destination ideas."]
        },
        "education": {
            "patterns": ["learning resources", "study tips", "education advice", "academic help"],
            "responses": ["I can assist with educational queries. What subject are you studying?",
                        "Let's explore learning resources together.",
                        "Tell me about your educational goals or questions."]
        },
        "pet_advice": {
            "patterns": ["pet care tips", "animal advice", "pet health", "taking care of pets"],
            "responses": ["Pets are wonderful! Here are some pet care tips: [pet_care_tips]",
                        "I can provide advice on pet health and care.", "Let's talk about your pet and their well-being."]
        },
        "shopping": {
            "patterns": ["online shopping", "buying something", "shopping advice", "product recommendations"],
            "responses": ["I can help you with online shopping. What are you looking to buy?",
                        "Let's find the perfect item for you!", "Tell me what you're interested in purchasing."]
        },
        "career_advice": {
            "patterns": ["job search help", "career guidance", "career change advice", "professional development"],
            "responses": ["I can provide career advice. What specific guidance do you need?",
                        "Let's explore career opportunities together.", "Tell me about your career goals or concerns."]
        },
        "relationship_advice": {
            "patterns": ["relationship help", "love advice", "dating tips", "relationship problems"],
            "responses": ["Relationships can be complex. How can I assist you?",
                        "I can offer advice on relationships and dating.", "Tell me about your relationship situation."]
        },
        "mental_health": {
            "patterns": ["mental health support", "coping strategies", "stress relief tips", "emotional well-being"],
            "responses": ["Mental health is important. How can I support you?",
                        "I can provide guidance for managing stress and emotions.",
                        "Let's talk about strategies for maintaining mental well-being."]
        },
        "language_learning": {
            "patterns": ["language learning tips", "language practice", "learning new languages", "language study advice"],
            "responses": ["Learning a new language can be exciting! How can I assist you?",
                        "I can help with language learning tips and practice.",
                        "Tell me which language you're interested in learning."]
        },
        "finance_advice": {
            "patterns": ["financial planning help", "money management tips", "investment advice", "budgeting assistance"],
            "responses": ["I can provide guidance on financial matters. What specific advice do you need?",
                        "Let's discuss your financial goals and plans.",
                        "Tell me about your financial situation or goals."]
        }

}




training_data = []
labels = []

for intent, data in intents.items():
    for pattern in data['patterns']:
        training_data.append(pattern.lower())
        labels.append(intent)

# print(training_data)
# print(labels)

Vectorizer = TfidfVectorizer(tokenizer=nltk.word_tokenize, stop_words="english", max_df=0.8, min_df=1)
X_train = Vectorizer.fit_transform(training_data)
X_train, X_test, Y_train, Y_test = train_test_split(X_train, labels, test_size=0.4, random_state=42, stratify=labels)

model = SVC(kernel='linear', probability=True, C=1.0)
model.fit(X_train, Y_train)


NEWS_API_KEY = "insert api key here"

def get_news():
    try:
        news_url = f"https://newsapi.org/v2/top-headlines?country=in&apiKey={NEWS_API_KEY}"
        response = requests.get(news_url)
        data = response.json()

        if response.status_code == 200:
            articles = data.get("articles", [])
            if articles:
                headlines = [article["title"] for article in articles[:5]]  # Displaying the top 5 headlines
                response_text = "Here are the top headlines:\n" + "\n".join(headlines)
            else:
                response_text = "No news articles available at the moment."
        else:
            response_text = "Sorry, I couldn't retrieve the news at the moment."

    except requests.RequestException as e:
        response_text = "There was an error while fetching the news."

    return response_text

def predict_intent(user_input):
    user_input = user_input.lower()

    # Check for opening or closing apps and update context
    if "open" in user_input or "launch" in user_input:
        context["last_opened_app"] = None  # Reset context for opening apps
    elif "close" in user_input:
        context["last_opened_app"] = None  # Reset context for closing apps

    input_vector = Vectorizer.transform([user_input])
    intent = model.predict(input_vector)[0]
    return intent



# To wish
def wish():
    hour = int(datetime.datetime.now().hour)
    if hour >= 0 and hour <= 12:
        speak("Good Morning Sir")
    elif hour > 12 and hour < 16:
        speak("Good Afternoon Sir")
    else:
        speak("Good Evening Sir")


def openappweb(query):
    speak("Launching Sir...")
    if ".com" in query or ".co.in" in query or ".org" in query:
        query = query.replace("open", "")
        query = query.replace("Leo", "")
        query = query.replace("launch", "")
        query = query.strip()
        webbrowser.open(f"https://www.{query}")
    else:
        app_found = False
        for app, executable in dictapp.items():
            if app in query:
                os.system(f"start {executable}")
                app_found = True
                # Update context
                context["last_opened_app"] = app
                break
        if not app_found:
            speak("App not found Sir")

def close_app(app_name):
    try:
        os.system(f"pkill {app_name}")
        speak(f"Closed {app_name} Sir")
    except Exception as e:
        speak(f"Error closing {app_name}: {str(e)}")

def get_time():
    current_time = datetime.datetime.now().strftime("%H:%M:%S")
    response_text = f"It's currently {current_time}."
    return response_text


OPENWEATHER_API_KEY = "insert api key here"


def get_weather(city="Vidyaranyapura"):
    base_url = "http://api.openweathermap.org/data/2.5/weather"

    try:
        params = {
            'q': city,
            'appid': OPENWEATHER_API_KEY,
            'units': 'metric'
        }

        response = requests.get(base_url, params=params)
        data = response.json()

        if response.status_code == 200:
            temperature = data['main']['temp']
            description = data['weather'][0]['description']
            response_text = f"The weather in {city.capitalize()} is currently {description} with a temperature of {temperature}°C."
        else:
            response_text = "Sorry, I couldn't retrieve the weather information at the moment."

    except Exception as e:
        response_text = "There was an error while fetching the weather information."

    return response_text

def handle_exam_prep():
    pdf_path = "sample.pdf"  # <-- Replace with uploaded file path
    text = extract_text_from_pdf(pdf_path)

    flashcards = generate_flashcards(text)
    quiz = generate_quiz(text)

    print("\n--- Flashcards ---")
    for q, a in flashcards:
        print(f"Q: {q}\nA: {a}\n")

    print("\n--- Quiz ---")
    for q, opts, ans_idx in quiz:
        print(q)
        for j, opt in enumerate(opts):
            print(f"{j+1}. {opt}")
        print(f"Answer: {opts[ans_idx]}\n")

    speak("Flashcards and quiz generated. Check console for details.")

if __name__ == "__main__":
    print("Say 'WAKE UP' to start AI assistant")
    talk = takecommand().lower()
    if talk == 'wake up':
        wish()
        speak('I am Luna, your personal AI assistant. How can I help you today?')
        while True:
            query = takecommand().lower()

            if "exit" in query:
                speak("Goodbye, have a nice day")
                break

            if not query.strip():
                continue

            intent = predict_intent(query)

            # ---- Intent Handling ---- #
            if intent == "news":
                speak(intents[intent]["responses"][0])
                news_response = get_news()
                speak(news_response)

            elif intent == "time":
                speak(intents[intent]["responses"][0])
                time_response = get_time()
                speak(time_response)

            elif intent == "weather":
                speak(intents[intent]["responses"][0])
                weather_response = get_weather(city="Vidyaranyapura")
                speak(weather_response)

            elif "open command prompt" in query:
                os.system("start cmd")
                context["last_opened_app"] = "Command Prompt"

            elif "open chrome" in query:
                os.system("start chrome")
                context["last_opened_app"] = "Google Chrome"

            elif "close app" in query:
                if context["last_opened_app"] is not None:
                    app_to_close = dictapp.get(context["last_opened_app"])
                    if app_to_close:
                        close_app(app_to_close)
                        context["last_opened_app"] = None
                    else:
                        speak("No corresponding application found.")
                else:
                    speak("No application is open to close.")

            elif "my name is" in query:
                name = query.split("my name is")[-1].strip()
                context["user_name"] = name
                speak(f"Nice to meet you, {name}!")

            elif "what's my name" in query:
                if context["user_name"] is not None:
                    speak(f"Your name is {context['user_name']}.")
                else:
                    speak("I don't know your name. You can tell me by saying, 'My name is ...'.")

            elif "ip address" in query:
                ip = get("https://api.ipify.org").text
                speak(f"Your IP address is {ip}")

            elif "wikipedia" in query:
                speak("Searching Wikipedia...")
                topic = query.replace("wikipedia", "").strip()
                if not topic:
                    speak("Please specify a topic to search on Wikipedia.")
                else:
                    try:
                        results = wikipedia.summary(topic, sentences=2)
                        speak(results)
                    except wikipedia.exceptions.DisambiguationError:
                        speak("Multiple results found. Please be more specific.")
                    except wikipedia.exceptions.PageError:
                        speak("No Wikipedia page found for that query.")

            elif "open google" in query:
                while True:
                    speak("What should I search on Google?")
                    ms = takecommand().lower()
                    if ms == "none":
                        speak("I didn't catch that. Please tell again.")
                        continue
                    webbrowser.open(f"https://www.google.com/search?q={ms}")
                    break

            elif "open youtube" in query:
                while True:
                    speak("Of course, which video would you like me to open?")
                    video_name = takecommand().lower()
                    if video_name == "none":
                        speak("I didn't catch that. Please tell again.")
                        continue

                    speak(f"Now opening '{video_name}'")
                    pywhatkit.playonyt(video_name)
                    break

            elif "open" in query or "launch" in query:
                speak("What would you like me to open?")
                op = takecommand().lower()
                openappweb(op)

            elif intent in intents:
                # Default: pick a random response
                responses = intents[intent]['responses']
                response = random.choice(responses)
                speak(response)

            

            else:
                speak("I didn't understand that. Can you please rephrase or ask a different question?")

