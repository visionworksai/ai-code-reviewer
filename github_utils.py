import os
import json
import requests
from typing import Dict, Any, List, Optional
from github import Github
import re

class PatchedFile:
    """    
    Attributes:
        path: The file path
        hunks: List of code hunks in the file
    """
    def __init__(self, path: str):
        self.path = path
        self.hunks = []
        self.source_file = f"a/{path}"
        self.target_file = f"b/{path}"

class Hunk:
    """    
    Attributes:
        source_start: Starting line number in the original file
        source_length: Number of lines in the original file section
        target_start: Starting line number in the modified file
        target_length: Number of lines in the modified file section
        content: The actual diff content of the hunk
    """
    def __init__(self, header: str, content: str):
        self.content = content
        # Parse the hunk header to extract line numbers
        match = re.match(r'^@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@', header)
        if match:
            self.source_start = int(match.group(1))
            self.source_length = int(match.group(2) or 1)
            self.target_start = int(match.group(3))
            self.target_length = int(match.group(4) or 1)
        else:
            self.source_start = 0
            self.source_length = 0
            self.target_start = 0
            self.target_length = 0

def parse_git_diff(diff_text: str) -> List[PatchedFile]:
    """
    Parse git diff text into PatchedFile objects with Hunks.
    
    Args:
        diff_text: Raw git diff string
        
    Returns:
        List of PatchedFile objects
    """
    files = []
    current_file = None
    current_hunk = None
    hunk_lines = []
    
    # File path pattern matching
    file_pattern = re.compile(r'^(\+\+\+ b/|--- a/)(.+)$')
    hunk_pattern = re.compile(r'^@@ .+ @@')
    
    for line in diff_text.splitlines():
        # New file
        if line.startswith('diff --git'):
            if current_file and current_hunk:
                current_hunk.content = '\n'.join(hunk_lines)
                current_file.hunks.append(current_hunk)
                hunk_lines = []
            
            if current_file:
                files.append(current_file)
            
            current_file = None
            current_hunk = None
            
        # File info
        elif line.startswith('+++ b/'):
            match = file_pattern.match(line)
            if match:
                path = match.group(2)
                current_file = PatchedFile(path)
                
        # Hunk header
        elif hunk_pattern.match(line):
            if current_file:
                if current_hunk:
                    current_hunk.content = '\n'.join(hunk_lines)
                    current_file.hunks.append(current_hunk)
                    hunk_lines = []
                    
                current_hunk = Hunk(line, "")
                hunk_lines = [line]
        
        # Hunk content
        elif current_hunk:
            hunk_lines.append(line)
    
    # Add the last hunk and file
    if current_file and current_hunk:
        current_hunk.content = '\n'.join(hunk_lines)
        current_file.hunks.append(current_hunk)
        files.append(current_file)
    
    return files

class PRInfo:
    """
    Data class to store pull request details.
    
    Attributes:
        repo_owner: The GitHub repository owner (username or organization)
        repo_name: The GitHub repository name
        pull_request_number: The pull request number
        pull_request_title: The pull request title
        pull_request_description: The pull request description (body)
    """
    def __init__(self, owner: str, repo: str, pull_number: int, title: str, description: str):
        self.repo_owner = owner
        self.repo_name = repo
        self.pull_request_number = pull_number
        self.pull_request_title = title
        self.pull_request_description = description

class FileInfo:
    """
    Simple class to hold file information for code review.
    
    Attributes:
        path: The path of the file in the repository
    """
    def __init__(self, path: str):
        self.path = path

def get_github_client():
    """
    Initialize and return the GitHub API client.
    
    Returns:
        Authenticated GitHub client
        
    Raises:
        ValueError: If GITHUB_TOKEN environment variable is not set
    """
    github_token = os.environ.get("GITHUB_TOKEN")
    if not github_token:
        raise ValueError("GITHUB_TOKEN environment variable is required")
    return Github(github_token)

def information_for_pr_review() -> PRInfo:
    """
    Extract pull request details from GitHub Actions event payload.
    
    This function handles both direct PR events and comment events on PRs.
    
    Returns:
        PRInfo object containing pull request information
        
    Raises:
        KeyError: If required fields are missing from the event payload
    """
    # Get the GitHub event data from the environment
    with open(os.environ["GITHUB_EVENT_PATH"], "r") as f:
        github_event_path = json.load(f)

    # Handle different event types
    if "issue" in github_event_path and "pull_request" in github_event_path["issue"]:
        # For comment triggers, get PR number from the issue
        pull_number = github_event_path["issue"]["number"]
        repo_full_name = github_event_path["repository"]["full_name"]
    else:
        # For direct PR events
        pull_number = github_event_path["number"]
        repo_full_name = github_event_path["repository"]["full_name"]

    # Split repository full name into owner and repo name
    owner, repo = repo_full_name.split("/")

    # Get additional PR details from GitHub API
    github_client = get_github_client()
    repo_obj = github_client.get_repo(repo_full_name)
    pr = repo_obj.get_pull(pull_number)

    return PRInfo(owner, repo_obj.name, pull_number, pr.title, pr.body)

def fetch_diff_for_pr(owner: str, repo: str, pull_number: int) -> str:
    """
    Fetch the diff of the pull request from GitHub API.
    
    Args:
        owner: Repository owner (username or organization)
        repo: Repository name
        pull_number: Pull request number
        
    Returns:
        String containing the pull request diff
    """
    repo_name = f"{owner}/{repo}"
    print(f"Fetching diff for: {repo_name} PR#{pull_number}")

    # Get GitHub token
    github_token = os.environ.get("GITHUB_TOKEN")
    if not github_token:
        raise ValueError("GITHUB_TOKEN environment variable is required")

    # Use GitHub API to fetch the diff
    api_url = f"https://api.github.com/repos/{repo_name}/pulls/{pull_number}"
    headers = {
        'Authorization': f'Bearer {github_token}',
        'Accept': 'application/vnd.github.v3.diff'
    }

    response = requests.get(f"{api_url}.diff", headers=headers)

    if response.status_code == 200:
        diff = response.text
        print(f"Successfully retrieved diff ({len(diff)} bytes)")
        return diff
    else:
        print(f"Failed to get diff. Status code: {response.status_code}")
        print(f"Response: {response.text}")
        return ""

def make_comment_for_review(
    owner: str,
    repo: str,
    pull_number: int,
    comments: List[Dict[str, Any]],
):
    """
    Submit review comments to the GitHub pull request.
    
    Args:
        owner: Repository owner (username or organization)
        repo: Repository name
        pull_number: Pull request number
        comments: List of comment objects to post
    """
    print(f"Posting {len(comments)} review comments to GitHub")

    # Get GitHub client and repository
    github_client = get_github_client()
    repo_obj = github_client.get_repo(f"{owner}/{repo}")
    pr = repo_obj.get_pull(pull_number)
    
    try:
        # First, get the latest commit SHA for the PR
        latest_commit = pr.get_commits().reversed[0]
        commit_id = latest_commit.sha
        print(f"Using commit SHA: {commit_id}")
        
        # Instead of using create_review, use create_comment for each comment
        successful_comments = 0
        for comment in comments:
            try:
                # When using create_review_comment, we need to use 'position' parameter for line
                pr.create_review_comment(
                    body=comment["body"],
                    commit_id=commit_id,
                    path=comment["path"],
                    position=comment["position"] # Position in the diff
                )
                successful_comments += 1
                print(f"Successfully posted comment on line {comment['position']}")
            except Exception as e:
                print(f"Error posting individual comment: {str(e)}")
                print(f"Comment data: {json.dumps(comment, indent=2)}")
                
                # Try an alternative approach if the first one fails
                try:
                    print("Trying alternative approach with 'line' instead of 'position'...")
                    pr.create_review_comment(
                        body=comment["body"],
                        commit_id=commit_id,
                        path=comment["path"],
                        line=comment["position"]
                    )
                    successful_comments += 1
                    print(f"Successfully posted comment on line {comment['position']} using alternative approach")
                except Exception as alt_e:
                    print(f"Alternative approach also failed: {str(alt_e)}")
        
        print(f"Successfully posted {successful_comments} out of {len(comments)} comments")

    except Exception as e:
        print(f"Error during review process: {str(e)}")
        print(f"Comment payload: {json.dumps(comments, indent=2)}")
        
        # If the error is related to specific fields, give more detailed information
        if "'line'" in str(e):
            print("\nHelp: The GitHub API expects 'line' for the line number in the file.")
        elif "'commit_id'" in str(e):
            print("\nHelp: The 'commit_id' parameter is required and must be a valid commit SHA.")
        elif "'position'" in str(e):
            print("\nHelp: The 'position' parameter refers to the line position in the diff.")
            
        # Suggest installing a newer version of PyGithub
        print("\nNote: GitHub API and PyGithub library both evolve over time.")
        print("Consider upgrading PyGithub: pip install --upgrade PyGithub")
        print("Or check the latest PyGithub documentation for the correct parameters.")

def generate_review_prompt(file: PatchedFile, hunk: Hunk, pr_details: PRInfo) -> str:
    """
    Create the AI prompt for reviewing a code chunk.
    
    Args:
        file: File information
        hunk: Code chunk (hunk) to review
        pr_details: Pull request details
        
    Returns:
        Formatted prompt string to send to the AI model
    """
    # Count lines in the hunk to help with line number references
    lines = hunk.content.split('\n')
    line_count = len(lines)
    
    return f"""Your task is reviewing pull requests. IMPORTANT INSTRUCTIONS:
    - RESPOND ONLY WITH JSON in the exact format shown below. Do not include any explanations.
    - The JSON format must be:  {{"reviews": [{{"lineNumber":  <line_number>, "reviewComment": "<review comment>"}}]}}
    - If there's nothing to improve, return {{"reviews": []}} - an empty array.
    - CRITICALLY IMPORTANT: Line numbers must be accurate and correspond to the diff below.
    - The diff has {line_count} lines. Line numbers should be between 1 and {line_count}.
    - The first line of the diff starts with line 1, the second with line 2, and so on.
    - Use GitHub Markdown in comments
    - Focus on bugs, security issues, and performance problems
    - NEVER suggest adding comments to the code

Review the following code diff in the file "{file.path}" and take the pull request title and description into account when writing the response.

Pull request title: {pr_details.pull_request_title}
Pull request description:

---
{pr_details.pull_request_description or 'No description provided'}
---

Git diff to review:

```diff
{hunk.content}
```

REMEMBER: Your ENTIRE response must be valid JSON in the format {{"reviews": [...]}} with no other text.
The lineNumber field MUST refer to the line number in the diff above (1 to {line_count}).
"""

def create_github_comment(file: FileInfo, hunk: Hunk, model_response: List[Dict[str, str]]) -> List[Dict[str, Any]]:
    """
    Convert AI responses into GitHub comment objects.
    
    Args:
        file: File information
        hunk: Code chunk that was reviewed
        model_response: List of AI review responses
        
    Returns:
        List of comment objects ready to be posted to GitHub
    """
    print(f"Processing {len(model_response)} AI review suggestions")
    
    # Determine the maximum line number in the hunk for validation
    hunk_lines = hunk.content.split("\n")
    max_line_number = len(hunk_lines)
    
    created_github_comments = []
    for review in model_response:
        try:
            # Extract line number from AI response
            model_response_line_number = int(review["lineNumber"])
            
            # Make sure the line number is within valid range
            if model_response_line_number < 1:
                print(f"Warning: Line number {model_response_line_number} is less than 1, using line 1 instead")
                model_response_line_number = 1
            elif model_response_line_number > max_line_number:
                print(f"Warning: Line number {model_response_line_number} exceeds max lines in hunk ({max_line_number}), using last line instead")
                model_response_line_number = max_line_number
            
            # Create comment object - keeping it simple with just the essential fields
            # PyGithub create_review_comment requires body, path, and position/line
            comment = {
                "body": review["reviewComment"],
                "path": file.path,
                "position": model_response_line_number  # This will be used as the line parameter
            }
            created_github_comments.append(comment)
            print(f"Created comment for line {model_response_line_number}")

        except (KeyError, TypeError, ValueError) as e:
            print(f"Error creating comment: {e}")
            print(f"Problematic AI response: {review}")
    
    return created_github_comments

def get_diff_and_files(owner: str, repo: str, pull_number: int) -> tuple[str, List[PatchedFile]]:
    """
    Fetch the diff of the pull request and parse it into file objects.
    
    Args:
        owner: Repository owner (username or organization)
        repo: Repository name
        pull_number: Pull request number
        
    Returns:
        Tuple of (raw diff string, list of parsed PatchedFile objects)
    """
    diff_text = fetch_diff_for_pr(owner, repo, pull_number)
    files = parse_git_diff(diff_text)
    return diff_text, files 