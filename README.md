VisionWorks AI Code Reviewer
============================

An automated code review tool that uses AI models to analyze pull requests and provide intelligent code review comments.

Overview
--------
VisionWorks AI Code Reviewer is a GitHub Action that automatically reviews pull requests using AI models. It analyzes code changes, identifies potential issues, and provides constructive feedback directly in the pull request.

The tool supports different AI models through a modular architecture, with Gemini AI currently implemented and ready for expansion to other models like OpenAI in the future.

Features
--------
- Automatic code review on pull requests
- Detection of bugs, security issues, and performance problems
- Line-specific comments posted directly to GitHub PRs
- Support for file exclusion patterns
- Modular design for integrating multiple AI models

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
             GEMINI_API_KEY: ${{ secrets.GEMINI_API_KEY }}
             GEMINI_MODEL: "gemini-2.0-flash-001"
             AI_MODEL_TYPE: "gemini"
             INPUT_EXCLUDE: "*.md,*.txt,*.png,*.jpg"
           run: python visionworks_code_reviewer.py
   ```

2. Add required secrets to your GitHub repository:
   - GITHUB_TOKEN: Automatically provided by GitHub Actions
   - GEMINI_API_KEY: Your Google Gemini API key

Usage
-----
1. Create a pull request in your repository
2. Comment "/review" on the pull request
3. The action will run and add review comments to your pull request

Configuration
------------
The following environment variables can be configured:

- GEMINI_API_KEY: API key for Google Gemini (required for Gemini model)
- GEMINI_MODEL: Specific Gemini model to use (default: "gemini-2.0-flash-001")
- AI_MODEL_TYPE: Which AI model to use (currently only "gemini")
- INPUT_EXCLUDE: Comma-separated list of file patterns to exclude (e.g., "*.md,*.json")

Project Structure
----------------
- visionworks_code_reviewer.py: Main application file
- models/: Directory containing AI model implementations
  - __init__.py: Factory method for getting the right AI model
  - base_model.py: Abstract base class for all AI models
  - gemini_model.py: Implementation for Google Gemini
  - openai_model.py: Placeholder for future OpenAI implementation
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
- google-generativeai
- requests
- unidiff

Contributing
-----------
Contributions are welcome! Please feel free to submit a Pull Request.
