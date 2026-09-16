"""
Local Ollama LLM Streamlit Chat Interface
-------------------------------------------
A simple, beginner-friendly Streamlit chatbot that talks to a locally
hosted LLM through Ollama's local REST API ("https://football-emperor-pelt.ngrok-free.dev").

Run with:
    streamlit run app.py
"""

import streamlit as st
import requests

# --------------------------------------------------------------------------
# Configuration
# --------------------------------------------------------------------------
OLLAMA_BASE_URL = "https://football-emperor-pelt.ngrok-free.dev"
OLLAMA_CHAT_ENDPOINT = f"{OLLAMA_BASE_URL}/api/chat"
OLLAMA_TAGS_ENDPOINT = f"{OLLAMA_BASE_URL}/api/tags"

# Change this to whichever model you have pulled with `ollama pull <model>`
DEFAULT_MODEL = "llama3.2"

REQUEST_TIMEOUT_SECONDS = 120  # generous timeout for slower local hardware

# --------------------------------------------------------------------------
# Page setup
# --------------------------------------------------------------------------
st.set_page_config(
    page_title="Local Ollama Chat",
    page_icon="🤖",
    layout="centered",
)

# --------------------------------------------------------------------------
# Session state initialization
# --------------------------------------------------------------------------
if "messages" not in st.session_state:
    # Each entry: {"role": "user" | "assistant", "content": str}
    st.session_state.messages = []

if "model_name" not in st.session_state:
    st.session_state.model_name = DEFAULT_MODEL


# --------------------------------------------------------------------------
# Helper functions
# --------------------------------------------------------------------------
def check_ollama_connection() -> tuple[bool, str]:
    """
    Check whether the Ollama server is reachable.
    Returns (is_connected, message).
    """
    try:
        response = requests.get(OLLAMA_TAGS_ENDPOINT, timeout=5)
        if response.status_code == 200:
            return True, "Connected to Ollama."
        return False, f"Ollama responded with status code {response.status_code}."
    except requests.exceptions.ConnectionError:
        return False, "Could not connect to Ollama. Is it running?"
    except requests.exceptions.Timeout:
        return False, "Connection to Ollama timed out."
    except Exception as exc:  # noqa: BLE001 - show any unexpected error to the user
        return False, f"Unexpected error while checking Ollama: {exc}"


def get_available_models() -> list[str]:
    """Fetch the list of models currently pulled in Ollama. Returns [] on failure."""
    try:
        response = requests.get(OLLAMA_TAGS_ENDPOINT, timeout=5)
        if response.status_code == 200:
            data = response.json()
            return [model["name"] for model in data.get("models", [])]
        return []
    except Exception:
        return []


def query_ollama(model: str, conversation: list[dict]) -> tuple[bool, str]:
    """
    Send the full conversation history to Ollama's /api/chat endpoint
    and return (success, response_text_or_error_message).
    """
    payload = {
        "model": model,
        "messages": conversation,
        "stream": False,
    }

    try:
        response = requests.post(
            OLLAMA_CHAT_ENDPOINT,
            json=payload,
            timeout=REQUEST_TIMEOUT_SECONDS,
        )

        if response.status_code == 200:
            data = response.json()
            content = data.get("message", {}).get("content", "").strip()
            if not content:
                return False, "Ollama returned an empty response."
            return True, content

        if response.status_code == 404:
            return False, (
                f"Model '{model}' was not found on this Ollama server.\n\n"
                f"Pull it first with:\n`ollama pull {model}`"
            )

        # Try to surface Ollama's own error message if present
        try:
            error_detail = response.json().get("error", response.text)
        except Exception:
            error_detail = response.text
        return False, f"Ollama API error (status {response.status_code}): {error_detail}"

    except requests.exceptions.ConnectionError:
        return False, (
            "Could not connect to Ollama at "
            f"`{OLLAMA_BASE_URL}`. Make sure Ollama is installed and running "
            "(run `ollama serve` or open the Ollama app)."
        )
    except requests.exceptions.Timeout:
        return False, (
            "The request to Ollama timed out. The model may be too large "
            "for your hardware, or it is still loading — try again."
        )
    except requests.exceptions.RequestException as exc:
        return False, f"A network error occurred while contacting Ollama: {exc}"
    except Exception as exc:  # noqa: BLE001
        return False, f"An unexpected error occurred: {exc}"


def reset_chat():
    st.session_state.messages = []


# --------------------------------------------------------------------------
# Sidebar
# --------------------------------------------------------------------------
with st.sidebar:
    st.header("⚙️ Settings")

    st.text_input(
        "Ollama Model",
        value=st.session_state.model_name,
        key="model_name",
        help="Name of the model pulled in Ollama (e.g. llama3.2, mistral, phi3).",
    )

    st.button("🗑️ Reset / Clear Chat", on_click=reset_chat, use_container_width=True)

    st.divider()

    st.subheader("🔌 Connection Status")
    connected, status_message = check_ollama_connection()
    if connected:
        st.success(status_message)
        available_models = get_available_models()
        if available_models:
            with st.expander("Available models on this server"):
                for m in available_models:
                    st.write(f"- {m}")
    else:
        st.error(status_message)
        st.caption("Start Ollama, then refresh this page.")

    st.divider()

    st.subheader("ℹ️ About")
    st.markdown(
        """
        **Local Ollama LLM Streamlit Chat Interface**

        A simple demo chatbot that runs entirely on your machine:
        - Frontend: **Streamlit**
        - Inference: **Ollama** (local, no cloud API)
        - Endpoint: `http://localhost:11434`

        Built for academic / demo purposes.
        """
    )

# --------------------------------------------------------------------------
# Main chat interface
# --------------------------------------------------------------------------
st.title("🤖 Local Ollama Chat")
st.caption(f"Currently using model: `{st.session_state.model_name}`")

# Render existing conversation history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input box (pinned at the bottom by Streamlit automatically)
user_prompt = st.chat_input("Ask something...")

if user_prompt:
    # 1. Show and store the user's message
    st.session_state.messages.append({"role": "user", "content": user_prompt})
    with st.chat_message("user"):
        st.markdown(user_prompt)

    # 2. Query Ollama with the full conversation so far (for context)
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            success, result = query_ollama(
                model=st.session_state.model_name,
                conversation=st.session_state.messages,
            )

        if success:
            st.markdown(result)
            st.session_state.messages.append({"role": "assistant", "content": result})
        else:
            st.error(result)
            # Don't add failed responses to history, so the user can just retry
