import assemblyai as aai
from elevenlabs import generate, stream, play
from openai import OpenAI
from constants import assemblyai_api_key, openai_api_key

class AI_Assistant:
    def __init__(self):
        # Define API Keys
        aai.settings.api_key = assemblyai_api_key
        self.openai_client = OpenAI(api_key=openai_api_key)

        self.transcriber = None

        # Define prompt
        self.full_transcript = [
            {"role": "system", "content": "You are a text-based fortune teller. You will ask questions that follow a light-hearted story-like path, do not repeated yourself. You will ask only 12 questions in total to determine their fortunes. Fortunes should be light-hearted and include descriptive personas and a text"},
        ]

###### Step 2: Real-Time Transcription with AssemblyAI ######

    def start_transcription(self):
        self.transcriber = aai.RealtimeTranscriber(
            sample_rate = 16000,
            on_data = self.on_data,
            on_error = self.on_error,
            on_open = self.on_open,
            on_close = self.on_close,
            end_utterance_silence_threshold = 1000
        )
        
        self.transcriber.connect()
        microphone_stream = aai.extras.MicrophoneStream(sample_rate=16000)
        self.transcriber.stream(microphone_stream)

    def stop_transcription(self):
        if self.transcriber:
            self.transcriber.close()
            self.transcriber = None

    def on_open(self, session_opened: aai.RealtimeSessionOpened):
        #print("Session ID:", session_opened.session_id)
        return

    def on_error(self, error: aai.RealtimeError):
        #print("An error occured:", error)
        return

    def on_close(self):
        #print("Closing Session")
        return

    def on_data(self, transcript: aai.RealtimeTranscript):
        if not transcript.text:
            return
        if isinstance(transcript, aai.RealtimeFinalTranscript):
            self.generate_ai_response(transcript)
        else:
            print(transcript.text, end="\r")

###### Step 3: Pass real-time transcript to OpenAI ######

    def generate_ai_response(self, transcript):

        self.stop_transcription()

        self.full_transcript.append({"role": "user", "content": transcript.text})
        print(f"\nUser: {transcript.text}", end="\r\n")

        response = self.openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=self.full_transcript
        )

        ai_response = response.choices[0].message.content
        print(f"\nFortune-Teller: {ai_response}\n", end="\r\n")
        ai_assistant.full_transcript.append({"role":"assistant", "content": ai_response})
        self.start_transcription()

 

ai_assistant = AI_Assistant()
print(f"\nFortune-Teller: Welcome to AssemblyAI's fortune-teller, what is your name?\n", end="\r\n")
ai_assistant.full_transcript.append({"role":"assistant", "content": "Welcome to AssemblyAI's fortune-teller, what is your name?"})
ai_assistant.start_transcription()