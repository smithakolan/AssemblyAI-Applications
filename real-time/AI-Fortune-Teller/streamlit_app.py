import streamlit as st
import websockets
import asyncio
import base64
import json
import pyaudio
from pathlib import Path
from openai import OpenAI


# Prompt
full_transcript = [
	{"role":"system", "content":"""You are an AI Fortune-teller. I have asked 8 questions to a user and gotten answers for each question which I have numbered 1 to 8. Here are the 8 questions:  1. You awaken on a train, you're gliding past rolling hills and tranquil lakes. What thoughts or daydreams do you entertain as you gaze out of the window?
2. As the train slows, you spy an ancient village nestled on the mountainside, a tapestry of colorful rooftops and smoke curling from chimneys. If you were to disembark here, what's the first thing you would do?
3. On your way to the village, a hidden grove reveals a family of foxes playing in the sunlight. Describe your interaction with this enchanting scene.
4. After departing the train to explore the village, you discover a trail leading to an enchanting cave. As you approach, you hear the faint melody of an unseen musician. How do you search for the source of this music?
5. The trail leads you to a bustling market filled with exotic spices and colorful textiles. Amidst the stalls, a fortune teller catches your eye, offering to read your palm. Do you accept, and if so, what question do you eagerly ask about your future?
6. You exit the market with a mysterious trinket in hand. As dusk falls, you find a garden aglow with fireflies. What wish would you make here, in this place where some believe the veil between worlds is thin?
7. As night envelops the village, you accept an invitation to a local celebration. The villagers share stories of their heritage and invite you to partake in a time-honored dance. Describe your experience dancing under the starlit sky.
8. The festivities wind down, and you find yourself back at the train station, the adventure drawing to a close. Reflecting on your journey, what have you learned about yourself, and how has this experience shaped your thoughts about where you'll go next?  I will send you the responses for each of these questions from the user. Everytime I send you a response you need to choose a fortune which closely align with their responses. Choose between these fortunes:  fortune-1: Nomad. Fortune: As a Nomad, the horizon calls to your soul. Unfamiliar lands await your footprint, and your adaptability will be the currency of your travels. Wander with purpose, for your journey is as rich as your destination. Traits: Explorer, Drifter, Trailblazer, Survivor, Adaptable fortune-2: Hermit. Fortune: Solitude is the canvas of the Hermit's soul. In the quiet, find strength and self-reliance. The world's noise fades away, leaving only the truth you seek in the echoes of your heart. Traits: Solitary, Reflective, Thoughtful, Self-Sufficient, Introspective  
You should only respond with the number of their fortunes, so for example, 1 or 2. That’s it, DO NOT response with anything else."""},
]

# Session state
if 'text' not in st.session_state:
	st.session_state['text'] = 'Listening...'
	st.session_state['run'] = False

if 'session_active' not in st.session_state:
    st.session_state.session_active = False

if 'current_question' not in st.session_state:
    st.session_state['current_question'] = 1

if 'responses' not in st.session_state:
    st.session_state['responses'] = []

# Audio parameters 
FRAMES_PER_BUFFER = 3200
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000

# Initialize PyAudio
p = pyaudio.PyAudio()

# Open an audio stream with above parameter settings
stream = p.open(
   format=FORMAT,
   channels=CHANNELS,
   rate=RATE,
   input=True,
   frames_per_buffer=FRAMES_PER_BUFFER
)

def open_page(url):
    open_script= """
        <script type="text/javascript">
            window.open('%s', '_blank').focus();
        </script>
    """ % (url)
    html(open_script)

# Start/stop audio transmission
def start_listening():
	st.session_state['run'] = True
	st.session_state.session_active = True

	

def stop_listening():
	st.session_state['run'] = False

def update_initial_image():
	image_display.image('questions/1.png')
	

def process_transcript(transcript):
    # This is where you can integrate with LLM or any other processing
	st.session_state['text'] = f"Processing transcript: {transcript}"
	st.session_state['responses'].append(f"{st.session_state['current_question']}:"+ transcript)
	#st.write(st.session_state['text'])
	if st.session_state['current_question'] < 8:
		st.session_state['current_question'] += 1
		image_display.image(f'/questions/{st.session_state["current_question"]}.png')
	else:
		st.session_state['run'] = False
		print(st.session_state['responses'])
		openai_client = OpenAI(api_key = st.secrets['openai_api_key'])

		full_transcript.append({"role":"user", "content": ''.join(st.session_state['responses'])})

		response = openai_client.chat.completions.create(
            model = "gpt-3.5-turbo",
            messages = full_transcript
        )
		ai_response = response.choices[0].message.content

		image_display.image(f'/results/fortune-{ai_response}.png')
		transcription_display.button('Get fortune by email', on_click=open_page('https://forms.gle/RvTLdKiU5GJkah7U8'))

	
    # Add any additional processing here, for example, sending the transcript to an LLM


# Web user interface
st.image('logo.png')
st.image('title.png')

image_display = st.empty()
image_display.image('home.png')
transcription_display = st.empty()
col1, col2 = st.columns(2)

col1.button('Start', on_click=start_listening)
col2.button('Stop', on_click=stop_listening)

# At the beginning of your Streamlit app, after setting up the UI components


with st.expander('About this App'):
	st.markdown('''
	This Streamlit app uses the AssemblyAI API to perform real-time transcription.
	
	Libraries used:
	''')

async def terminate_session(_ws):
    # Send the termination request
    terminate_message = json.dumps({"terminate_session": True})
    await _ws.send(terminate_message)
    
    # Loop to process all remaining messages until 'SessionTerminated' is received
    while True:
        result_str = await _ws.recv()  # Wait for a message
        result = json.loads(result_str)  # Parse the JSON message

        # Check the message type
        if result.get("message_type") == "SessionTerminated":
            print("Session successfully terminated with response:", result)
            break  # Exit the loop upon receiving 'SessionTerminated'
        


# Send audio (Input) / Receive transcription (Output)
async def send_receive():
	if st.session_state['run']:
		update_initial_image()

	URL = f"wss://api.assemblyai.com/v2/realtime/ws?sample_rate={RATE}"

	print(f'Connecting websocket to url ${URL}')

	async with websockets.connect(
		URL,
		extra_headers=(("Authorization", st.secrets['api_key']),),
		ping_interval=5,
		ping_timeout=20
	) as _ws:

		await asyncio.sleep(0.1)
		print("Receiving messages ...")

		session_begins = await _ws.recv()
		print(session_begins)
		print("Sending messages ...")

		config_message = json.dumps({
            "end_utterance_silence_threshold": 3000
        })
		await _ws.send(config_message)

		async def send():
			while st.session_state['run']:
				try:
					data = stream.read(FRAMES_PER_BUFFER)
					data = base64.b64encode(data).decode("utf-8")
					json_data = json.dumps({"audio_data":str(data)})
					r = await _ws.send(json_data)

				except websockets.exceptions.ConnectionClosedError as e:
					print(e)
					assert e.code == 4008
					break

				except Exception as e:
					print(e)
					assert False, "Not a websocket 4008 error"

				await asyncio.sleep(0.01)


		async def receive():

			while st.session_state['run']:
				try:
					result_str = await _ws.recv()
					result = json.loads(result_str)['text']

					if json.loads(result_str)['message_type']=='FinalTranscript':
						print(result)
						st.session_state['text'] = result
						transcription_display.text(f"Real-time Transcript: {result}")
						#st.write(st.session_state['text'])

						process_transcript(st.session_state['text'])
					else:
						print(result)
						st.session_state['text'] = result
						transcription_display.text(f"Real-time Transcript: {result}")
						#st.write(st.session_state['text'])
						

				except websockets.exceptions.ConnectionClosedError as e:
					print(e)
					assert e.code == 4008
					break

				except Exception as e:
					print(e)
					assert False, "Not a websocket 4008 error"
			
		send_result, receive_result = await asyncio.gather(send(), receive())
		# Inside send_receive, at the very end, just before exiting the `async with` block: 
		if st.session_state['run']==False and st.session_state.session_active==True:     
			# Call the terminate session only if the run state is False, indicating the user clicked "Stop"     
			await terminate_session(_ws)
			st.session_state.session_active=False
		

asyncio.run(send_receive())

