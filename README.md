# MyGPT - Local LLM Terminal Chat Interface

![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

MyGPT is a simple yet powerful terminal-based chat interface for local LLM (Large Language Model) interactions using GGUF models with `llama.cpp` Python bindings.

## Features

- 🚀 Simple terminal interface for local LLM chats
- 🔍 Automatic model detection in current directory
- ⚡ Streamed responses for real-time interaction
- 💾 Conversation history saving
- 🛠️ Customizable parameters (context size, temperature, threads)
- 📝 System prompt configuration
- 📂 Supports both single model files and model directories

## Installation

1. **Prerequisites**:
   - Python 3.8 or higher
   - `llama-cpp-python` package installed
   - At least one GGUF model file

2. **Install dependencies**:
   ```bash
   pip install llama-cpp-python sty
   ```

3. **Download a GGUF model** and place it in the same directory as the script or in a dedicated models directory.

## Usage

### Basic Usage
```bash
python mygpt.py
```
This will automatically detect compatible GGUF models in the current directory.

### Advanced Usage
```bash
python mygpt.py --model /path/to/model.gguf --n_ctx 2048 --temperature 0.7 --n_thread 8
```

### Runtime Arguments
| Argument | Description | Default |
|----------|-------------|---------|
| `-m`, `--model` | Path to model file or directory | Current directory |
| `--n_ctx` | Context window size | 500 |
| `--temperature` | Model temperature | 0.8 |
| `--n_thread` | Number of CPU threads | CPU core count |
| `--system-prompt` | Initial system prompt | "you are helpful assistant" |

### Mid-Chat Commands
| Command | Description |
|---------|-------------|
| `/save [filename]` | Save conversation to file |
| `/exit` | Exit the program |
| `/clear` | Clear the terminal |
| `/help` | Show help message |
| `/sysprompt [text]` | View or change system prompt |

## Example Session
```
================================================================================
--> Chat on June 14, 2023 14:30:45 <--
================================================================================

[You]: Hello, how are you today?

‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾
[AI]: Hello! I'm just a computer program, so I don't have feelings, but I'm functioning perfectly and ready to assist you with anything you need. How can I help you today?
________________________________________________________________________________
```

## Tips

- For best performance, use models quantized to match your hardware capabilities
- Adjust `n_ctx` based on your model's maximum context size
- Higher temperature values (e.g., 0.8-1.2) make outputs more creative
- Lower temperature values (e.g., 0.1-0.5) make outputs more focused and deterministic

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any improvements.

---

Enjoy your local AI chatting experience! 🤖💬