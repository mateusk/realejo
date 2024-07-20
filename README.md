# Realejo

This Python program interacts with a locally running LLAMA3 API, processes the streamed JSON response, and converts the output text to speech using the TTS library.

## Features

- Sends a prompt to the LLAMA3 API.
- Parses the streamed JSON response from the API.
- Converts the text response to audio and saves it as `output.wav`.

## Installation

It is recommended to use Anaconda to manage the Python environment and dependencies.

### Step 1: Install LLAMA3

Download and install the LLAMA3 API from the [official website](https://ollama.com/download)

The llama3 server should automatically start after installation. You can test if llama3 is running by opening a terminal and running:

```bash
ollama run llama3
```

You should see a prompt that says "Send a message", you can send a prompt and see the response from the LLM.

### Step 2: Install Anaconda

Download and install Anaconda from the [official website](https://www.anaconda.com/products/individual).

### Step 3: Create a Conda Environment

Create a new Conda environment with Python:

```bash
cd path/to/realejo
conda create --prefix ./env
conda activate ./env
```

### Step 4: Install Dependencies

Install pip in the local environment:

```bash
conda install pip
```

Install the required Python packages:

```bash
pip install -r requirements.txt
```

## Usage

Run the Python program:

```bash
python main.py
# or
python3 main.py
```

The program will prompt you to enter a message. After you enter a message, the program will send the message to the LLAMA3 API, parse the response, and save the audio output as `output.wav`.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
