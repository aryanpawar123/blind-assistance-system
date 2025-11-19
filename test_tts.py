import pyttsx3

engine = pyttsx3.init('sapi5')

engine.setProperty('rate', 150)
engine.setProperty('volume', 1.0)

voices = engine.getProperty('voices')
engine.setProperty('voice', voices[0].id)

engine.say("Hello, your audio system is working correctly.")
engine.runAndWait()
