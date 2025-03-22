# ✅ VisionWorks AI Code Reviewer

Automated code review powered by **Google Gemini**, **OpenAI**, and **Claude** – triggered by PR comments.

---

## 🚀 Overview

VisionWorks AI Code Reviewer is a reusable GitHub Action that performs automated, AI-powered code reviews. When you comment on a pull request (e.g. `/openai-review`, `/gemini-review`, `/claude-review`), it uses the selected model to analyze the code diff and provide line-by-line feedback.

---

## ✨ Features

- 🔍 Analyzes pull request diffs
- 💡 AI-generated, line-level review comments
- 🧠 Supports multiple AI providers:
  - ✅ Google Gemini
  - ✅ OpenAI GPT
  - ✅ Claude by Anthropic
- 🎯 Exclude specific file types with glob patterns
- 🔐 Secure – requires each user to define their own secrets
- Automatic code review on pull requests
- Detection of bugs, security issues, and performance problems
- Line-specific comments posted directly to GitHub PRs
- Support for file exclusion patterns
- Modular design supporting multiple AI models:
  - Google Gemini
  - OpenAI (GPT-4, etc.)
  - Anthropic Claude (Claude 3 Opus/Sonnet/Haiku)

---

## ⚙️ Installation (in your repo)

1. Create a workflow file in `.github/workflows/ai-review.yml`:

```yaml
name: AI Code Review

on:
  issue_comment:
    types: [created]

permissions: write-all

jobs:
  ai-review:
    runs-on: self-hosted  # or ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Run AI Reviewer
        uses: visionworksai/ai-code-reviewer@main
        with:
          GEMINI_API_KEY: ${{ secrets.GEMINI_API_KEY }}
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
          CLAUDE_API_KEY: ${{ secrets.CLAUDE_API_KEY }}
          INPUT_EXCLUDE: "*.md, docs/**"
```

2. Add **secrets** to your GitHub repo settings:
   - `GEMINI_API_KEY` – required for Gemini reviews
   - `OPENAI_API_KEY` – required for OpenAI reviews
   - `CLAUDE_API_KEY` – required for Claude reviews

---

## 🧑‍💻 Usage

1. Open a pull request
2. Comment one of the following:

```
/gemini-review
/openai-review
/claude-review
```

3. The action will detect the model, run the review, and add comments.

To override a specific model version:

```yaml
with:
  CLAUDE_MODEL: claude-3-haiku-20240307
  OPENAI_MODEL: gpt-4
  GEMINI_MODEL: gemini-1.5-flash-001
```

---

## 🔧 Configuration

| Variable           | Description                                                  |
|--------------------|--------------------------------------------------------------|
| `INPUT_EXCLUDE`    | Comma-separated list of file globs to ignore                 |
| `AI_MODEL_TYPE`    | Auto-detected from PR comment (no need to set manually)      |
| `GEMINI_API_KEY`   | Required for Gemini reviews                                  |
| `GEMINI_MODEL`     | Optional: override Gemini model name                         |
| `OPENAI_API_KEY`   | Required for OpenAI reviews                                  |
| `OPENAI_MODEL`     | Optional: override OpenAI model name                         |
| `CLAUDE_API_KEY`   | Required for Claude reviews                                  |
| `CLAUDE_MODEL`     | Optional: override Claude model name                         |

---

## 🧱 Project Structure

```
visionworks_code_reviewer.py     # Main entry point
models/
  ├── __init__.py                # Model factory
  ├── base_model.py              # Base class
  ├── gemini_model.py            # Gemini implementation
  ├── openai_model.py            # OpenAI implementation
  └── claude_model.py            # Claude implementation
github_utils.py                  # GitHub API helpers
diff_utils.py                    # Diff parsing + filtering
```

---

## ➕ Adding New Models

1. Create a new file under `models/` (e.g. `models/my_model.py`)
2. Implement `BaseAIModel`
3. Register your model in `models/__init__.py`

---

## 🧪 Requirements

- Python 3.7+
- `PyGithub`, `github3.py`, `openai>=1.0.0`
- `google-generativeai`, `google-ai-generativelanguage`
- `requests`, `unidiff`

---

## 🤖 Model Comparison

| Model                    | Strengths                          | Notes                              |
|--------------------------|------------------------------------|------------------------------------|
| **Gemini** (Google)      | Fast + Cost-efficient              | Great default; free tier available |
| **OpenAI GPT**           | High-quality (GPT-4 etc.)          | Higher cost                        |
| **Claude 3 Sonnet**      | Balanced performance & speed       | Good general-purpose               |
| **Claude 3 Haiku**       | Fastest & cheapest Claude option   | Best for cost-sensitive use        |
| **Claude 3 Opus**        | Most powerful Claude model         | Highest cost                       |

> You can override the default model with e.g. `CLAUDE_MODEL: claude-3-haiku-20240307`.

---

## 🛡️ Security Note

This action **does not expose or reuse** your secrets.  
Each repository using this action must define their **own API keys**.  
The action will **fail securely** if required keys are missing.

## ✅ TODO / Roadmap

- [ ] 🧠 Add support for **DeepSeek** model family  
- [ ] 🤖 Support for **local models**  

