# Terminal Chatbot with LLaMA.cpp

![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Model Format](https://img.shields.io/badge/model-GGUF-yellow)

A simple yet powerful terminal-based chatbot powered by LLaMA.cpp Python bindings, featuring real-time streaming responses and convenient chat management.

## Features

- 🚀 Real-time streaming responses (text appears as generated)
- 🤖 Supports GGUF format LLaMA models
- 🔍 Automatic GGUF model detection
- 📝 Chat saving functionality
- 🧹 Screen clearing command
- 🎨 Colorful terminal interface
- ⚙️ Interactive model selection

## Installation

1. Ensure you have Python 3.8+ installed
2. Install dependencies:
```bash
pip install llama-cpp-python sty
```
3. Place your GGUF model files in the script directory or specify path

## Usage

```bash
# Auto-detect GGUF models in current directory
python mygpt.py

# Specify model file or directory
python mygpt.py -m /path/to/model.gguf
python mygpt.py -m /path/to/models/
```

## Interactive Commands

Once chat starts:
- Just type to chat normally
- Special commands:
  - `/exit` - Exit (will prompt to save chat)
  - `/save` - Save current conversation
  - `/clear` - Clear the chat screen
  - `/help` - Show available commands

## Example Session

```text
$ python mygpt.py
Found GGUF models:
1. llama-2-7b-chat.Q4_K_M.gguf
2. mistral-7b-instruct-v0.1.Q4_K_M.gguf
Select model (1-2): 1

Initializing model... Done!

You: hello
AI: Hello there! How can I help you today?

You: tell me a fun fact about space
AI: *streams response gradually*
Did you know that a day on Venus is longer than a year on Venus? 
It takes Venus about 243 Earth days to rotate once on its axis, 
but only about 225 Earth days to orbit the Sun!

You: /save
Chat saved to conversation_20230615.txt

You: /exit
Save conversation before exiting? [y/N]: y
Chat saved. Goodbye!
```

## Chat Saving Format

Saved conversations use this human-readable format:

```
=== Conversation 2023-06-15 14:30:22 ===
Model: llama-2-7b-chat.Q4_K_M.gguf

You: hello
AI: Hello there! How can I help you today?

You: tell me a fun fact about space
AI: Did you know that a day on Venus is longer than...
```

## Requirements

- Python 3.8+
- `llama-cpp-python` (with GGUF support)
- `sty` package
- GGUF format model file(s)

## License

MIT License - see [LICENSE](LICENSE) file for details

---

Enjoy natural conversations with your local LLM! The chatbot will stream responses in real-time just like human typing. All special commands work mid-conversation for full control over your chat experience.
