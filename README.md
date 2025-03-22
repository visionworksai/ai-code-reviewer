VisionWorks AI Code Reviewer
============================

An automated code review tool that uses AI models (Gemini and OpenAI) to analyze pull requests and provide intelligent code review comments.

Overview
--------
VisionWorks AI Code Reviewer is a GitHub Action that automatically reviews pull requests using AI models. It analyzes code changes, identifies potential issues, and provides constructive feedback directly in the pull request.

The tool supports multiple AI models through a modular architecture, with both Google's Gemini AI and OpenAI's models currently implemented.

Features
--------
- Automatic code review on pull requests
- Detection of bugs, security issues, and performance problems
- Line-specific comments posted directly to GitHub PRs
- Support for file exclusion patterns
- Modular design supporting multiple AI models:
  - Google Gemini
  - OpenAI (GPT-4, etc.)

Installation
-----------
1. Add the GitHub Action to your repository workflow:

   ```yml
   name: AI Code Review

   on:
     issue_comment:
       types: [created]

   jobs:
     review:
       runs-on: ubuntu-latest
       if: github.event.comment.body == '/review'
       steps:
         - uses: actions/checkout@v3
           with:
             fetch-depth: 0
         
         - name: Set up Python
           uses: actions/setup-python@v4
           with:
             python-version: '3.10'
             
         - name: Install dependencies
           run: |
             python -m pip install --upgrade pip
             pip install -r requirements.txt
             
         - name: Run AI Code Review
           env:
             GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
             # For Gemini
             GEMINI_API_KEY: ${{ secrets.GEMINI_API_KEY }}
             GEMINI_MODEL: "gemini-2.0-flash-001"
             # For OpenAI
             # OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
             # OPENAI_MODEL: "gpt-4"
             AI_MODEL_TYPE: "gemini"  # Change to "openai" if using OpenAI
             INPUT_EXCLUDE: "*.md,*.txt,*.png,*.jpg"
           run: python visionworks_code_reviewer.py
   ```

2. Add required secrets to your GitHub repository:
   - GITHUB_TOKEN: Automatically provided by GitHub Actions
   - GEMINI_API_KEY: Your Google Gemini API key (for Gemini model)
   - OPENAI_API_KEY: Your OpenAI API key (for OpenAI model)

Usage
-----
1. Create a pull request in your repository
2. Comment "/review" on the pull request
3. The action will run and add review comments to your pull request

Configuration
------------
The following environment variables can be configured:

Common:
- AI_MODEL_TYPE: Which AI model to use ("gemini" or "openai")
- INPUT_EXCLUDE: Comma-separated list of file patterns to exclude (e.g., "*.md,*.json")

For Gemini:
- GEMINI_API_KEY: API key for Google Gemini (required for Gemini model)
- GEMINI_MODEL: Specific Gemini model to use (default: "gemini-2.0-flash-001")

For OpenAI:
- OPENAI_API_KEY: API key for OpenAI (required for OpenAI model)
- OPENAI_MODEL: Specific OpenAI model to use (default: "gpt-4")
- OPENAI_ORGANIZATION: Optional organization ID if you have multiple organizations

Project Structure
----------------
- visionworks_code_reviewer.py: Main application file
- models/: Directory containing AI model implementations
  - __init__.py: Factory method for getting the right AI model
  - base_model.py: Abstract base class for all AI models
  - gemini_model.py: Implementation for Google Gemini
  - openai_model.py: Implementation for OpenAI models
- github_utils.py: GitHub API interaction utilities
- diff_utils.py: Git diff parsing and filtering utilities

Adding New AI Models
-------------------
To add a new AI model:

1. Create a new file in the models/ directory (e.g., models/new_model.py)
2. Implement the BaseAIModel abstract class
3. Add the new model to the factory method in models/__init__.py

Requirements
-----------
- Python 3.7+
- PyGithub
- google-generativeai (for Gemini model)
- openai (for OpenAI model)
- requests
- unidiff

Comparing AI Models
------------------
- Gemini: Google's AI model, good for code analysis with lower cost
- OpenAI: Powerful GPT models like GPT-4, potentially more comprehensive reviews but higher cost

Choose the model that best fits your needs and budget.
