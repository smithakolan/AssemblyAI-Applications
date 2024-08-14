import streamlit as st
import websockets
import asyncio
import base64
import json
import pyaudio
from openai import OpenAI
import webbrowser
import random


# Prompt
full_transcript = [
	{"role":"system", "content":"""You are an AI Fortune-teller. I have asked 7 questions to a user and gotten answers for each question which I have numbered 1 to 7. Here are the 7 questions:Q1. You awaken on a train, you're gliding past rolling hills and tranquil lakes. Describe your initial feelings. What's the first thing you'd do?
2. As the train slows, you spy an ancient village nestled in the mountainside. Tell me what you feel compelled to explore. What draws your attention?
3. On your way to the village, a hidden grove reveals a family of deer playing in the sunlight. What would you do?
4. Next, you discover a trail leading to an enchanting cave. As you approach, you hear the faint melody of an unseen musician. What kind of music do you hear?
5. At last, you’ve reached the village and its bustling market filled with trinkets and colorful textiles. Amidst the stalls, a fortune teller catches your eye, offering to read your palm. Do you ask a question about your past, present or future?
6. As night envelops the village, you accept an invitation to a local celebration. The villagers share stories of their heritage and invite you to partake in a time-honored dance. Do you accept the invitation or do you move on in your journey?
7. On the way back to the train, you come to a crossroads of two paths, one going left and one going right. Which one do you take instinctively?
  ------------------------------------------------------------------
Based on their answers to the above questions, you need to decide their fortunes from these following 8 fortunes:
1. Nomad - Free-Spirited, Independent, Wanderlust, Flexible, Adventurous. Traits: Explorer, Drifter, Trailblazer, Survivor, Adaptable.
2. Hermit - Solitary, Reflective, Thoughtful, Self-Sufficient, Introspective. Traits: Sage, Loner, Philosopher, Contemplative, Independent.
3. Sovereign - Decisive, Commanding, Structured, Ambitious, Resolute. Traits: Leader, Pioneer, Strategist, Regal, Authoritative.

4. Dynamo - Energetic, Forceful, Competitive, Dynamic, Driven.
Traits: Mover, Shaker, Achiever, Motivator, Warrior.

5. Harmony - Balanced, Peaceful, Diplomatic, Cooperative, Understanding.
Traits: Mediator, Peacemaker, Consensus-Builder, Tranquil, Listener.

6. Sentinel - Protective, Loyal, Dependable, Observant, Conscientious.
Traits: Guardian, Watcher, Defender, Stalwart, Reliable.

7. Rebel - Unconventional, Questioning, Nonconforming, Bold, Free.
Traits: Renegade, Anarchist, Maverick, Reformer, Revolutionary.

8. Mystic - Mysterious, Spiritual, Contemplative, Introspective, Peaceful.
Traits: Sage, Seer, Healer, Philosopher, Mediator.

You should only respond with the number of their fortunes, so for example, either 1 or 2 or 3 or 4 or 5 or 6 or 7 or 8. That’s it, DO NOT response with anything else."""},
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
	if st.session_state['current_question'] < 7:
		st.session_state['current_question'] += 1
		image_display.image(f'questions/{st.session_state["current_question"]}.png')
	else:
		st.session_state['run'] = False
		#print(st.session_state['responses'])
		# openai_client = OpenAI(api_key = st.secrets['openai_api_key'])

		# full_transcript.append({"role":"user", "content": ''.join(st.session_state['responses'])})

		# response = openai_client.chat.completions.create(
        #     model = "gpt-3.5-turbo",
        #     messages = full_transcript
        # )
		# ai_response = response.choices[0].message.content

		ai_response = random.randint(1, 8)

		transcription_display.empty()

		image_display.image(f'results/{ai_response}.png')
		webbrowser.open_new_tab(f'https://docs.google.com/forms/d/e/1FAIpQLSeTOg8m-Wd4rnG5WKVPnQ6dbuEM8oCDSbAvbNVsD0KWWv7z0A/viewform?usp=pp_url&entry.1826277827={ai_response}')
		
	
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
						#print(result)
						st.session_state['text'] = result
						transcription_display.markdown(f'<p style="font-size: 20px;">Real-time Transcript: {result}</p>', unsafe_allow_html=True)
						#st.write(st.session_state['text'])

						process_transcript(st.session_state['text'])
					else:
						#print(result)
						st.session_state['text'] = result
						transcription_display.markdown(f'<p style="font-size: 20px;">Real-time Transcript: {result}</p>', unsafe_allow_html=True)
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

