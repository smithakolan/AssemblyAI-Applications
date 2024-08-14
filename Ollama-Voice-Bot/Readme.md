
# Build an AI Voice Bot with Ollama and AssemblyAI

This guide will help you set up a real-time speech transcription and response system using AssemblyAI for transcription, LLAMA 3 for generating responses, and ElevenLabs for streaming the response as live audio.

## Step 1: Install Python Libraries

You'll need to install several Python libraries and other dependencies to get started. Here are the installation instructions for various components:

### Install Python Libraries
```bash
pip install ollama
pip install "assemblyai[extras]"
pip install elevenlabs
```
Install Additional Dependencies
For Debian/Ubuntu:

```bash
apt install portaudio19-dev
```
For MacOS:

```bash
brew install portaudio
brew install mpv
```

### Download the LLAMA 3 Model Locally
To use LLAMA 3 in your project, you need to pull the model data onto your local machine. Run the following command in your terminal:

```bash
ollama pull llama3
```
