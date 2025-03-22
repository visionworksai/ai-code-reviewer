import os
import json
import requests
from typing import Dict, Any, List
from github import Github
from unidiff import Hunk, PatchedFile

class PRDetails:
    """
    Data class to store pull request details.
    
    Attributes:
        owner: The GitHub repository owner (username or organization)
        repo: The GitHub repository name
        pull_number: The pull request number
        title: The pull request title
        description: The pull request description (body)
    """
    def __init__(self, owner: str, repo: str, pull_number: int, title: str, description: str):
        self.owner = owner
        self.repo = repo
        self.pull_number = pull_number
        self.title = title
        self.description = description

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

def get_pr_details() -> PRDetails:
    """
    Extract pull request details from GitHub Actions event payload.
    
    This function handles both direct PR events and comment events on PRs.
    
    Returns:
        PRDetails object containing pull request information
        
    Raises:
        KeyError: If required fields are missing from the event payload
    """
    # Get the GitHub event data from the environment
    with open(os.environ["GITHUB_EVENT_PATH"], "r") as f:
        event_data = json.load(f)

    # Handle different event types
    if "issue" in event_data and "pull_request" in event_data["issue"]:
        # For comment triggers, get PR number from the issue
        pull_number = event_data["issue"]["number"]
        repo_full_name = event_data["repository"]["full_name"]
    else:
        # For direct PR events
        pull_number = event_data["number"]
        repo_full_name = event_data["repository"]["full_name"]

    # Split repository full name into owner and repo name
    owner, repo = repo_full_name.split("/")

    # Get additional PR details from GitHub API
    gh = get_github_client()
    repo_obj = gh.get_repo(repo_full_name)
    pr = repo_obj.get_pull(pull_number)

    return PRDetails(owner, repo_obj.name, pull_number, pr.title, pr.body)

def get_diff(owner: str, repo: str, pull_number: int) -> str:
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

def create_review_comment(
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
    gh = get_github_client()
    repo_obj = gh.get_repo(f"{owner}/{repo}")
    pr = repo_obj.get_pull(pull_number)
    
    try:
        # Create the review with comments
        review = pr.create_review(
            body="AI Code Reviewer Comments",
            comments=comments,
            event="COMMENT"  # Post as regular comments, not approvals or rejections
        )
        print(f"Review successfully posted with ID: {review.id}")

    except Exception as e:
        print(f"Error posting review to GitHub: {str(e)}")
        print(f"Comment payload: {json.dumps(comments, indent=2)}")

def create_prompt(file: PatchedFile, hunk: Hunk, pr_details: PRDetails) -> str:
    """
    Create the AI prompt for reviewing a code chunk.
    
    Args:
        file: File information
        hunk: Code chunk (hunk) to review
        pr_details: Pull request details
        
    Returns:
        Formatted prompt string to send to the AI model
    """
    return f"""Your task is reviewing pull requests. Instructions:
    - Provide the response in following JSON format:  {{"reviews": [{{"lineNumber":  <line_number>, "reviewComment": "<review comment>"}}]}}
    - Provide comments and suggestions ONLY if there is something to improve, otherwise "reviews" should be an empty array.
    - Use GitHub Markdown in comments
    - Focus on bugs, security issues, and performance problems
    - IMPORTANT: NEVER suggest adding comments to the code

Review the following code diff in the file "{file.path}" and take the pull request title and description into account when writing the response.

Pull request title: {pr_details.title}
Pull request description:

---
{pr_details.description or 'No description provided'}
---

Git diff to review:

```diff
{hunk.content}
```
"""

def create_comment(file: FileInfo, hunk: Hunk, ai_responses: List[Dict[str, str]]) -> List[Dict[str, Any]]:
    """
    Convert AI responses into GitHub comment objects.
    
    Args:
        file: File information
        hunk: Code chunk that was reviewed
        ai_responses: List of AI review responses
        
    Returns:
        List of comment objects ready to be posted to GitHub
    """
    print(f"Processing {len(ai_responses)} AI review suggestions")
    
    comments = []
    for ai_response in ai_responses:
        try:
            # Extract line number from AI response
            line_number = int(ai_response["lineNumber"])
            
            # Validate line number is within the hunk's range
            if line_number < 1 or line_number > hunk.source_length:
                print(f"Warning: Line number {line_number} is outside the valid range")
                continue

            # Create comment object in GitHub-compatible format
            comment = {
                "body": ai_response["reviewComment"],
                "path": file.path,
                "position": line_number
            }
            comments.append(comment)
            print(f"Created comment for line {line_number}")

        except (KeyError, TypeError, ValueError) as e:
            print(f"Error creating comment: {e}")
            print(f"Problematic AI response: {ai_response}")
    
    return comments 