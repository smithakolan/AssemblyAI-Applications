
'''
+-------------------+        +-----------------------+        +------------------+        +------------------------+
|   Step 1: Install |        |  Step 2: Real-Time    |        |  Step 3: Pass    |        |  Step 4: Live Audio    |
|   Python Libraries|        |  Transcription with   |        |  Real-Time       |        |  Stream from ElevenLabs|
+-------------------+        |       AssemblyAI      |        |  Transcript to   |        |                        |
|                   |        +-----------------------+        |      LLAMA 3     |        +------------------------+
| - assemblyai      |                    |                    +------------------+                    |
| - ollama          |                    |                             |                              |
| - elevenlabs      |                    v                             v                              v
| - mpv             |        +-----------------------+        +------------------+        +------------------------+
| - portaudio       |        |                       |        |                  |        |                        |
+-------------------+        |  AssemblyAI performs  |--------> LLAMA 3 generates|-------->  ElevenLabs streams   |
                             |  real-time speech-to- |        |  response based  |        |  response as live      |
                             |  text transcription   |        |  on transcription|        |  audio to the user     |
                             |                       |        |                  |        |                        |
                             +-----------------------+        +------------------+        +------------------------+

###### Step 1: Install Python libraries ######
1. pip install ollama
2. Make sure to install `apt install portaudio19-dev` (Debian/Ubuntu) or `brew install portaudio` (MacOS)
3. pip install "assemblyai[extras]"
4. pip install elevenlabs
5. brew install mpv

Also in terminal, you need to run the following command to download the llama3 model locally:
ollama pull llama3
'''

import assemblyai as aai
from elevenlabs.client import ElevenLabs
from elevenlabs import stream
import ollama

class AI_Assistant:
    def __init__(self):
        aai.settings.api_key = "api-key"
        self.client = ElevenLabs(
            api_key = "api-key"
        )

        self.transcriber = None

        self.full_transcript = [
            {"role":"system", "content":"You are a language model called Llama 3 created by Meta, answer the questions being asked in less than 300 characters. Do not bold or asterix anything because this will be passed to a text to speech service."},
        ]

###### Step 2: Real-Time Transcription with AssemblyAI ######
        
    def start_transcription(self):
      print(f"\nReal-time transcription: ", end="\r\n")
      self.transcriber = aai.RealtimeTranscriber(
          sample_rate=16_000,
          on_data=self.on_data,
          on_error=self.on_error,
          on_open=self.on_open,
          on_close=self.on_close,
      )

      self.transcriber.connect()

      microphone_stream = aai.extras.MicrophoneStream(sample_rate=16_000)
      self.transcriber.stream(microphone_stream)

    def stop_transcription(self):
      if self.transcriber:
          self.transcriber.close()
          self.transcriber = None
      

    def on_open(self, session_opened: aai.RealtimeSessionOpened):
        #print("Session ID:", session_opened.session_id)
        return


    def on_data(self, transcript: aai.RealtimeTranscript):
        if not transcript.text:
            return

        if isinstance(transcript, aai.RealtimeFinalTranscript):
            print(transcript.text)
            self.generate_ai_response(transcript)
        else:
            print(transcript.text, end="\r")


    def on_error(self, error: aai.RealtimeError):
        #print("An error occured:", error)
        return


    def on_close(self):
        #print("Closing Session")
        return

    
###### Step 3: Pass real-time transcript to LLAMA 3 ######
    def generate_ai_response(self, transcript):
        self.stop_transcription()

        self.full_transcript.append({"role":"user", "content":transcript.text})
        print(f"\nUser:{transcript.text}", end="\r\n")

        ollama_stream = ollama.chat(
            model="llama3",
            messages=self.full_transcript,
            stream=True,
        )

        print("Llama 3:", end="\r\n")

        text_buffer = ""
        full_text = ""
        for chunk in ollama_stream:
            text_buffer += chunk['message']['content']
            if text_buffer.endswith('.'):
                audio_stream = self.client.generate(text=text_buffer,
                                                    model="eleven_turbo_v2",
                                                    stream=True)
                print(text_buffer, end="\n", flush=True)
                stream(audio_stream)
                full_text += text_buffer
                text_buffer = ""
        
        if text_buffer:
            audio_stream = self.client.generate(text=text_buffer,
                                                    model="eleven_turbo_v2",
                                                    stream=True)
            print(text_buffer, end="\n", flush=True)
            stream(audio_stream)
            full_text += text_buffer

        self.full_transcript.append({"role":"assistant", "content":full_text})

        self.start_transcription()

ai_assistant = AI_Assistant()
ai_assistant.start_transcription()
         
        







        
        
