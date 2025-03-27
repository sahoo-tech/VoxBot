import os
import time
import json
import sys
import subprocess
from importlib import util
import site
import platform
import urllib.request
import tempfile
import wave

def check_internet_connection():
    """Check if we have an active internet connection"""
    try:
        urllib.request.urlopen('https://api.openai.com', timeout=3)
        return True
    except:
        return False

def is_package_installed(package_name):
    """Check if a package is installed"""
    return util.find_spec(package_name) is not None

def install_package(package_name):
    """Install a package using pip in user mode"""
    try:
        # Use --user flag to install in user space and avoid permission issues
        subprocess.check_call([
            sys.executable, 
            "-m", 
            "pip", 
            "install", 
            "--user",
            package_name
        ])
        
        # Add user site-packages to path if not already there
        user_site = site.getusersitepackages()
        if user_site not in sys.path:
            sys.path.append(user_site)
        
        return True
    except Exception as e:
        print(f"Error installing {package_name}: {e}")
        return False

# Required packages with their versions
REQUIRED_PACKAGES = {
    'python-dotenv': '1.0.0',
    'openai': '1.12.0',  # Using the latest stable version
    'SpeechRecognition': '3.10.0',
    'pyttsx3': '2.90',
    'sounddevice': '0.4.6',
    'soundfile': '0.12.1',
    'numpy': '1.24.3',
    'PyAudio': '0.2.14'  # Required for microphone input
}

# Install required packages first
print("Checking and installing required packages...")
for package, version in REQUIRED_PACKAGES.items():
    package_with_version = f"{package}=={version}"
    if not is_package_installed(package.lower()):
        print(f"Installing {package_with_version}...")
        if not install_package(package_with_version):
            print(f"Warning: Failed to install {package}")

# Now try to import the required packages
try:
    from dotenv import load_dotenv
    import speech_recognition as sr
    import pyttsx3
except ImportError as e:
    print(f"Critical import error: {e}")
    print("Please try running the script again, or install the packages manually:")
    print("\n".join(f"pip install {p}=={v}" for p, v in REQUIRED_PACKAGES.items()))
    sys.exit(1)

# Optional imports with fallback
WHISPER_AVAILABLE = False
SOUNDDEVICE_AVAILABLE = False
SOUNDFILE_AVAILABLE = False

# Try importing sounddevice
try:
    import numpy as np
    import sounddevice as sd
    SOUNDDEVICE_AVAILABLE = True
except ImportError as e:
    print(f"Warning: sounddevice import error: {e}")
    print("Advanced audio features will be disabled")

# Try importing soundfile
try:
    import soundfile as sf
    SOUNDFILE_AVAILABLE = True
except ImportError as e:
    print(f"Warning: soundfile import error: {e}")
    print("Advanced audio features will be disabled")

# Try importing whisper (optional)
try:
    if not is_package_installed('whisper'):
        print("Installing whisper...")
        install_package('git+https://github.com/openai/whisper.git')
    import whisper
    WHISPER_AVAILABLE = True
except ImportError as e:
    print(f"Warning: whisper import error: {e}")
    print("Advanced speech recognition will be disabled")

# Load environment variables
load_dotenv()

# Initialize OpenAI client
try:
    import openai
    client = openai.Client(
        api_key=os.getenv('OPENAI_API_KEY', ''),  # Provide empty string as default
        timeout=10.0  # Add timeout for API calls
    )
    
    # Test the connection with proper error handling
    try:
        test_response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "test"}],
            max_tokens=5
        )
        print("✅ OpenAI client initialized successfully")
        is_openai_available = True
    except Exception as api_error:
        if "exceeded your current quota" in str(api_error):
            print("⚠️ OpenAI API quota exceeded. Please check your billing status.")
        elif "Incorrect API key" in str(api_error):
            print("⚠️ Invalid OpenAI API key. Please check your .env file.")
        else:
            print(f"⚠️ OpenAI API error: {api_error}")
        print("The chatbot will operate in offline mode")
        is_openai_available = False
except Exception as e:
    print(f"⚠️ Error initializing OpenAI client: {e}")
    print("The chatbot will operate in offline mode")
    is_openai_available = False

# Initialize Whisper model if available
whisper_model = None
if WHISPER_AVAILABLE:
    try:
        print("Loading Whisper model (this might take a moment)...")
        whisper_model = whisper.load_model("base")
        print("Whisper model loaded successfully!")
    except Exception as e:
        print(f"Warning: Could not load Whisper model: {e}")
        print("Falling back to basic speech recognition")

# Initialize text-to-speech engine with customization
def initialize_text_to_speech():
    """Initialize text-to-speech engine with robust error handling"""
    try:
        engine = pyttsx3.init()
        # Test if the engine works
        engine.say("test")
        engine.runAndWait()
        
        # Configure properties
        voices = engine.getProperty('voices')
        engine.setProperty('rate', 150)    # Speed of speech
        engine.setProperty('volume', 0.9)  # Volume (0.0 to 1.0)
        if len(voices) > 1:
            engine.setProperty('voice', voices[1].id)
        
        print("✅ Text-to-speech initialized successfully")
        return engine
    except Exception as e:
        print(f"⚠️ Error initializing text-to-speech: {e}")
        print("Text-to-speech will be disabled")
        return None

def listen_with_speech_recognition():
    """Fallback method using speech_recognition"""
    recognizer = sr.Recognizer()
    try:
        with sr.Microphone() as source:
            print("\n🎤 Listening... (Speak now)")
            recognizer.adjust_for_ambient_noise(source, duration=0.5)
            audio = recognizer.listen(source, timeout=10, phrase_time_limit=15)
            print("🔍 Processing your speech...")
            
            text = recognizer.recognize_google(audio)
            print(f"👤 You: {text}")
            return text
    except sr.UnknownValueError:
        print("❌ Sorry, I couldn't understand that.")
    except sr.RequestError:
        print("❌ Sorry, there was an error with the speech recognition service.")
    except Exception as e:
        print(f"❌ An error occurred: {e}")
    return None

def listen_with_advanced_methods():
    """Advanced listening method using sounddevice and whisper"""
    temp_file = None
    try:
        # Record audio
        duration = 5
        sample_rate = 16000
        print("\n🎤 Listening... (Speak now)")
        audio_data = sd.rec(int(duration * sample_rate),
                          samplerate=sample_rate,
                          channels=1,
                          dtype=np.int16)
        sd.wait()
        
        # Create a temporary file using tempfile module
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp:
            temp_file = temp.name
            # Save audio file using wave module
            with wave.open(temp_file, 'wb') as wf:
                wf.setnchannels(1)
                wf.setsampwidth(2)  # 2 bytes for int16
                wf.setframerate(sample_rate)
                wf.writeframes(audio_data.tobytes())
        
        # Transcribe with whisper
        result = whisper_model.transcribe(temp_file)
        text = result["text"].strip()
        
        if text:
            print(f"👤 You: {text}")
            return text
            
    except Exception as e:
        print(f"❌ Error in advanced listening: {e}")
        return None
    finally:
        # Cleanup temporary file
        if temp_file and os.path.exists(temp_file):
            try:
                os.unlink(temp_file)
            except Exception as e:
                print(f"Warning: Could not delete temporary file: {e}")

def listen():
    """Smart listen function that uses the best available method and checks connectivity"""
    # Check internet connection first
    online_mode = check_internet_connection()
    if not online_mode:
        print("⚠️ Operating in offline mode - using basic speech recognition")
    
    if online_mode and WHISPER_AVAILABLE and SOUNDDEVICE_AVAILABLE and SOUNDFILE_AVAILABLE:
        result = listen_with_advanced_methods()
        if result:
            return result
    
    # Fallback to basic speech recognition
    return listen_with_speech_recognition()

# Initialize engines
engine = initialize_text_to_speech()

def speak(text):
    """Convert text to speech with error handling"""
    if not engine:
        print(f"🤖 Assistant: {text}")
        return
        
    try:
        print(f"🤖 Assistant: {text}")
        engine.say(text)
        engine.runAndWait()
    except Exception as e:
        print(f"⚠️ Error in text-to-speech: {e}")
        print("Falling back to text-only output")
        print(f"Text output: {text}")

# Keep conversation context
conversation_history = [
    {"role": "system", "content": "You are a helpful and friendly AI assistant named Sayantan's Assistant. You provide clear, concise, and accurate responses."}
]

def get_ai_response(prompt):
    """Get response from OpenAI API with conversation history"""
    try:
        # Check internet connection before making API call
        if not check_internet_connection():
            print("⚠️ No internet connection - using offline responses")
            return generate_fallback_response(prompt)
            
        if not is_openai_available:
            return generate_fallback_response(prompt)

        conversation_history.append({"role": "user", "content": prompt})
        
        if len(conversation_history) > 11:
            conversation_history.pop(1)
        
        try:
            # Use the client object for API calls
            completion = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=conversation_history,
                max_tokens=150,
                temperature=0.7
            )
            ai_response = completion.choices[0].message.content
        except Exception as openai_error:
            print(f"OpenAI API error: {openai_error}")
            ai_response = generate_fallback_response(prompt)
        
        conversation_history.append({"role": "assistant", "content": ai_response})
        return ai_response
    except Exception as e:
        print(f"❌ Error getting AI response: {e}")
        return generate_fallback_response(prompt)

def generate_fallback_response(prompt):
    """Generate a fallback response when API is not available"""
    prompt_lower = prompt.lower()
    
    responses = {
        "hello": "Hello! How can I help you today?",
        "hi": "Hi there! What can I do for you?",
        "how are you": "I'm functioning well, thank you for asking!",
        "bye": "Goodbye! Have a great day!",
        "thank": "You're welcome!",
        "help": "I'm here to help! What do you need assistance with?",
        "weather": "I'm sorry, I can't check the weather right now.",
        "time": f"The current time is {time.strftime('%H:%M')}",
        "name": "I'm Sayantan's Assistant, a voice-enabled chatbot.",
        "default": "I'm currently operating in offline mode. I can only provide basic responses right now."
    }
    
    for key in responses:
        if key in prompt_lower:
            return responses[key]
    
    return responses["default"]

def main():
    # Check internet connection at startup
    if check_internet_connection():
        print("✅ Online mode - Connected to internet")
    else:
        print("⚠️ Offline mode - No internet connection")
    
    # Welcome message
    welcome_message = "Hello! I'm Sayantan's Assistant, your voice-enabled AI companion. How can I help you today?"
    speak(welcome_message)
    
    while True:
        user_input = listen()
        
        if user_input:
            if user_input.lower() in ['quit', 'exit', 'bye', 'goodbye', 'stop']:
                speak("Thank you for chatting with me. Goodbye and have a great day!")
                break
            
            response = get_ai_response(user_input)
            speak(response)
        else:
            speak("Could you please repeat that?")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nProgram terminated by user.")
        speak("Goodbye!")
    except Exception as e:
        print(f"\n❌ An unexpected error occurred: {e}")
        speak("I encountered an error and need to shut down. Please restart me.") 