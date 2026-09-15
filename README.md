# Local Ollama LLM Streamlit Chat Interface

A simple, beginner-friendly Streamlit web app that lets you chat with a
locally hosted LLM through [Ollama](https://ollama.com). No cloud API,
no API keys — everything runs on your own computer.

## Project Structure

```text
ollama-streamlit-chat/
│
├── app.py
├── requirements.txt
└── README.md
```

## Features

- Chat-style interface using `st.chat_input()` and `st.chat_message()`
- Full conversation history stored in `st.session_state`
- Reset / Clear Chat button
- Sidebar with model name, connection status, and app info
- Graceful error handling for:
  - Ollama not running
  - Model not found / not pulled
  - Unreachable API / network errors
  - Unexpected API errors
- Loading spinner while the model generates a response

---

## Step-by-Step Setup Instructions (Windows)

These steps assume you are using **Windows** with **PowerShell** or
**Command Prompt (CMD)**.

### 1. Install / Check Python

Check if Python is already installed:

```powershell
python --version
```

If it's not installed (or the version is below 3.9), download and install
it from [python.org/downloads](https://www.python.org/downloads/).
**During installation, check the box "Add Python to PATH."**

### 2. Install Ollama

Download and install Ollama for Windows from:
[https://ollama.com/download](https://ollama.com/download)

Run the installer and follow the prompts. This installs the Ollama app
and the `ollama` command-line tool.

Verify the installation:

```powershell
ollama --version
```

### 3. Start Ollama

Ollama usually starts automatically after installation and runs in the
background (look for its icon in the system tray). If it's not running,
start it manually:

```powershell
ollama serve
```

Leave this window open if you started it manually — it needs to keep
running while you use the chatbot. By default, Ollama listens on:

```text
http://localhost:11434
```

### 4. Download / Pull the Required Model

In a new terminal window, pull the model you want to use. This example
uses `llama3.2`, but you can substitute any model supported by Ollama
(e.g. `mistral`, `phi3`, `gemma2`):

```powershell
ollama pull llama3.2
```

This downloads the model to your machine (only needs to be done once).
You can confirm it's available with:

```powershell
ollama list
```

### 5. Install Python Dependencies

Navigate to the project folder:

```powershell
cd path\to\ollama-streamlit-chat
```

(Optional but recommended) create and activate a virtual environment:

```powershell
python -m venv venv
venv\Scripts\activate
```

Install the required packages:

```powershell
pip install -r requirements.txt
```

### 6. Run the Streamlit Application

Make sure Ollama is still running (Step 3), then start the app:

```powershell
streamlit run app.py
```

### 7. Open the Localhost URL

Streamlit will automatically open your browser. If it doesn't, open it
manually and go to:

```text
http://localhost:8501
```

### 8. Test the Chatbot

- Type a question into the chat box at the bottom (e.g. "What is Python?")
- Press Enter and watch the response stream in after a short "Thinking..." spinner
- Ask a follow-up question — the app sends prior messages as context
- Click **"Reset / Clear Chat"** in the sidebar to start a new conversation
- Check the sidebar's **Connection Status** section to confirm Ollama is reachable

### 9. Troubleshoot Common Errors

| Problem | Likely Cause | Fix |
|---|---|---|
| "Could not connect to Ollama" | Ollama isn't running | Run `ollama serve` or open the Ollama app, then refresh the page |
| "Model 'X' was not found" | Model hasn't been pulled | Run `ollama pull <model_name>` |
| App opens but sidebar shows a red connection error | Ollama running on a different port, or blocked by firewall | Confirm Ollama is on port `11434`; check Windows Firewall settings |
| `streamlit: command not found` | Dependencies not installed / venv not activated | Run `pip install -r requirements.txt`, and make sure your virtual environment is activated |
| Response takes a long time or times out | Model is large for your hardware | Try a smaller model (e.g. `llama3.2:1b`, `phi3`) or wait — the first response after loading a model is often slower |
| `python` not recognized | Python not added to PATH | Reinstall Python and check "Add Python to PATH," or use `py` instead of `python` |

---

## Changing the Default Model

You can change the model directly in the sidebar's **"Ollama Model"**
text box at runtime — no code changes needed, as long as the model has
been pulled via `ollama pull <model_name>`.

To change the default model permanently, edit this line near the top of
`app.py`:

```python
DEFAULT_MODEL = "llama3.2"
```

## Notes

- This app uses Ollama's `/api/chat` endpoint, which accepts the full
  message history so the model has conversational context.
- No data leaves your machine — everything runs locally through Ollama.
