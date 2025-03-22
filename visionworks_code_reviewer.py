import json
import os
from typing import List, Dict, Any
from unidiff import Hunk

# Import from our custom modules
from models import get_ai_model
from github_utils import (
    get_pr_details, get_diff, create_review_comment, 
    create_prompt, create_comment, FileInfo
)
from diff_utils import parse_diff, filter_diff_by_patterns

def analyze_code(parsed_diff: List[Dict[str, Any]], pr_details, model_type: str = "gemini") -> List[Dict[str, Any]]:
    """
    Analyzes code changes and generates review comments using the specified AI model.
    
    Args:
        parsed_diff: List of dictionaries containing parsed diff information
        pr_details: Pull request details (title, description, etc.)
        model_type: Type of AI model to use (default: "gemini")
        
    Returns:
        List of review comments to be posted on GitHub
    """
    print("Starting code analysis...")
    print(f"Number of files to analyze: {len(parsed_diff)}")
    comments = []

    # Initialize the appropriate AI model based on configuration
    ai_model = get_ai_model(model_type)
    ai_model.configure()

    # Process each file in the diff
    for file_data in parsed_diff:
        file_path = file_data.get('path', '')
        print(f"\nAnalyzing file: {file_path}")

        # Skip deleted files or invalid paths
        if not file_path or file_path == "/dev/null":
            continue

        file_info = FileInfo(file_path)
        hunks = file_data.get('hunks', [])
        print(f"Found {len(hunks)} code chunks to review")

        # Process each code chunk (hunk) in the file
        for hunk_data in hunks:
            hunk_lines = hunk_data.get('lines', [])
            if not hunk_lines:
                continue

            # Create a unidiff Hunk object for better processing
            hunk = Hunk()
            hunk.source_start = 1
            hunk.source_length = len(hunk_lines)
            hunk.target_start = 1
            hunk.target_length = len(hunk_lines)
            hunk.content = '\n'.join(hunk_lines)

            # Create prompt and get AI analysis
            prompt = create_prompt(file_info, hunk, pr_details)
            print("Sending code chunk to AI for review...")
            ai_response = ai_model.get_ai_response(prompt)

            # Process AI responses into GitHub comments
            if ai_response:
                new_comments = create_comment(file_info, hunk, ai_response)
                if new_comments:
                    comments.extend(new_comments)
                    print(f"Added {len(new_comments)} review comment(s)")

    print(f"Analysis complete. Generated {len(comments)} total comments")
    return comments

def main():
    """
    Main function that coordinates the PR review workflow.
    
    Retrieves PR details, fetches and parses the diff, filters files based on
    patterns, analyzes code changes, and posts review comments to GitHub.
    """
    # Get pull request details from GitHub event
    pr_details = get_pr_details()
    
    # Load GitHub event data
    event_data = json.load(open(os.environ["GITHUB_EVENT_PATH"], "r"))
    event_name = os.environ.get("GITHUB_EVENT_NAME")
    
    # Currently only supports issue_comment event (comment on PR)
    if event_name == "issue_comment":
        # Verify it's a comment on a pull request
        if not event_data.get("issue", {}).get("pull_request"):
            print("Comment was not on a pull request. Exiting.")
            return

        # Get the diff for the pull request
        diff = get_diff(pr_details.owner, pr_details.repo, pr_details.pull_number)
        if not diff:
            print("No diff found for this pull request. Exiting.")
            return

        # Parse and filter the diff
        parsed_diff = parse_diff(diff)
        
        # Get exclusion patterns from environment variables
        exclude_patterns = os.environ.get("INPUT_EXCLUDE", "").split(",")
        exclude_patterns = [pattern.strip() for pattern in exclude_patterns]
        filtered_diff = filter_diff_by_patterns(parsed_diff, exclude_patterns)

        # Get AI model type from environment (default to gemini)
        model_type = os.environ.get("AI_MODEL_TYPE", "gemini")
        
        # Analyze code and generate review comments
        comments = analyze_code(filtered_diff, pr_details, model_type)
        
        # Post comments to GitHub if any were generated
        if comments:
            try:
                create_review_comment(
                    pr_details.owner, pr_details.repo, pr_details.pull_number, comments
                )
                print(f"Successfully posted {len(comments)} review comments")
            except Exception as e:
                print(f"Error posting review comments: {e}")
    else:
        print(f"Unsupported GitHub event: {event_name}")
        return

if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        print(f"Fatal error during execution: {error}")