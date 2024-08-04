import speech_recognition as sr

# Initialize the recognizer
recognizer = sr.Recognizer()

# Keywords to listen for
keywords = ["meta","metta", "Meadow", "llama", "lama"]

def listen_for_keywords():
    with sr.Microphone() as source:
        print("Listening for keywords...")
        while True:
            try:
                # Adjust for ambient noise and record audio
                recognizer.adjust_for_ambient_noise(source)
                audio = recognizer.listen(source)

                # Recognize the speech
                speech_text = recognizer.recognize_google(audio)
                print(f"Recognized speech: {speech_text}")

                # Check if any keyword is in the recognized speech
                for keyword in keywords:
                    if keyword in speech_text.lower():
                        question = extract_question(speech_text.lower(), keyword)
                        print(f"Keyword '{keyword}' detected. Recorded question: {question}")
                        break

            except sr.UnknownValueError:
                print("Could not understand the audio")
            except sr.RequestError as e:
                print(f"Could not request results; {e}")

def extract_question(speech_text, keyword):
    # Extract the part of the speech text that comes after the keyword
    return speech_text.split(keyword, 1)[1].strip()

if __name__ == "__main__":
    listen_for_keywords()
