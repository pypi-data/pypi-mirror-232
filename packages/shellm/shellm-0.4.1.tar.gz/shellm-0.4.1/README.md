# shellm

Use OpenAI LLMs from the command line.

# Quick Start

Install
```bash
pip install shellm
```

Export OpenAI key
```bash
export OPENAI_API_KEY=sk-...
```

View commands
```bash
shellm --help
```

## Completions

View completion help
```bash
shellm completion --help
```

Create a simple completion
```bash
shellm completion --prompt "Once upon a time" --max-tokens 128 --stream --echo
```

## Chat

View chat help
```bash
shellm chat --help
```

Create a simple chat completion
```bash
shellm chat --user-message "Tell me a story" --stream --max-tokens 128
```
