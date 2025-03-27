# VoxBot - Voice-Enabled AI Assistant

VoxBot is an intelligent voice-enabled chatbot that combines the power of OpenAI's GPT-3.5 with advanced speech recognition and text-to-speech capabilities. It can operate in both online and offline modes, ensuring continuous functionality even without internet connectivity.

## Features

- **Voice Interaction**: Natural voice input and output using advanced speech recognition and synthesis
- **Dual Mode Operation**:
  - **Online Mode**: Utilizes OpenAI's GPT-3.5 for intelligent responses
  - **Offline Mode**: Falls back to basic responses when internet/API is unavailable
- **Advanced Speech Recognition**:
  - Primary: OpenAI's Whisper model for accurate speech-to-text
  - Fallback: Google Speech Recognition as backup
- **Text-to-Speech**: Natural voice output with customizable settings:
  - Adjustable speech rate
  - Volume control
  - Gender selection for voice
- **Automatic Package Management**: Self-installs required dependencies
- **Error Handling**: Robust error management and graceful fallbacks
- **Conversation History**: Maintains context for more natural interactions

## Requirements

- Python 3.8 or higher
- OpenAI API key (for online mode)
- Internet connection (for online mode)
- Microphone (for voice input)
- Speakers (for voice output)

## Required Packages

```
python-dotenv==1.0.0
openai==1.12.0
SpeechRecognition==3.10.0
pyttsx3==2.90
sounddevice==0.4.6
soundfile==0.12.1
numpy==1.24.3
PyAudio==0.2.14
```

## Setup

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd chatbot
   ```

2. Create a `.env` file in the project root:
   ```
   OPENAI_API_KEY=your_api_key_here
   SPEECH_RATE=150
   SPEECH_VOLUME=0.9
   USE_FEMALE_VOICE=true
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

1. Run the chatbot:
   ```bash
   python voice_chatbot.py
   ```

2. Wait for the initialization message and the welcome prompt

3. Start speaking when you see the "🎤 Listening..." message

4. The chatbot will respond both verbally and with text output

## Features in Detail

### Speech Recognition
- Primary: Uses OpenAI's Whisper model for accurate speech recognition
- Fallback: Utilizes Google Speech Recognition when Whisper is unavailable
- Automatic noise reduction and ambient noise adjustment

### Text-to-Speech
- Customizable voice settings through environment variables
- Support for multiple voices (male/female)
- Adjustable speech rate and volume
- Graceful fallback to text-only output if speech synthesis fails

### AI Response Generation
- Online Mode: 
  - Uses OpenAI's GPT-3.5-turbo model
  - Maintains conversation history for context
  - Intelligent response generation
- Offline Mode:
  - Pre-defined response templates
  - Basic conversation capabilities
  - No internet required

### Error Handling
- Graceful degradation of services
- Automatic recovery from temporary failures
- Clear user feedback for any issues
- Continuous operation even when some features are unavailable

## Troubleshooting

1. **No sound output**:
   - Check your speaker settings
   - Verify text-to-speech engine initialization
   - Ensure no other program is blocking audio output

2. **Microphone issues**:
   - Check microphone permissions
   - Verify microphone is set as default input device
   - Test microphone in system settings

3. **API errors**:
   - Verify OpenAI API key in .env file
   - Check internet connection
   - Confirm API quota availability

4. **Package installation issues**:
   - Run with administrator privileges
   - Check Python version compatibility
   - Verify pip is up to date

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details. 