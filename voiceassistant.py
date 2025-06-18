import datetime
import speech_recognition as sr
import pyttsx3
import threading

def toggle_voice_assistant(app):
    app.voice_assistant_on = not app.voice_assistant_on
    if app.voice_assistant_on:
        speak(app, "Voice Assistant is now ON........please tell me how may I help you")
        threading.Thread(target=listen_for_commands, args=(app,)).start()
    else:
        speak(app, "Voice Assistant is now OFF")

def speak(app, text):
    app.engine.say(text)
    app.engine.runAndWait()
def listen_for_commands(app):
    while app.voice_assistant_on:
        with app.microphone as source:
            app.recognizer.adjust_for_ambient_noise(source)
            print("Listening for commands...")
            audio = app.recognizer.listen(source)
        try:
            command = app.recognizer.recognize_google(audio).lower()
            print("Command recognized:", command)
            execute_command(app, command)
        except sr.UnknownValueError:
            print("Could not understand the command")
        except sr.RequestError:
            print("Could not request results; check your network connection")

def execute_command(app, command):
    if "save file" in command:
        app.save_canvas()
        speak(app, "File saved successfully...")
    elif "open file" in command:
        app.open_canvas()
    elif "clear canvas" in command:
        speak(app, "Clearing canvas...")
        app.clear()
    elif "exit" in command or "close" in command:
        speak(app, "Exiting the application...")
        app.voice_assistant_on = False
        app.root.quit()
    else:
        speak(app, "Command not recognized")