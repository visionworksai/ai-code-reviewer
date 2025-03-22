from typing import List, Dict, Any
import fnmatch

def parse_diff(diff_str: str) -> List[Dict[str, Any]]:
    """
    Parse a git diff string into a structured format for processing.
    
    Args:
        diff_str: Raw git diff string from GitHub API
        
    Returns:
        List of dictionaries representing files and their hunks
    """
    files = []
    current_file = None
    current_hunk = None

    # Process the diff line by line
    for line in diff_str.splitlines():
        if line.startswith('diff --git'):
            # Start of a new file
            if current_file:
                files.append(current_file)
            current_file = {'path': '', 'hunks': []}

        elif line.startswith('--- a/'):
            # Old file path
            if current_file:
                current_file['path'] = line[6:]

        elif line.startswith('+++ b/'):
            # New file path
            if current_file:
                current_file['path'] = line[6:]

        elif line.startswith('@@'):
            # Start of a new hunk
            if current_file:
                current_hunk = {'header': line, 'lines': []}
                current_file['hunks'].append(current_hunk)

        elif current_hunk is not None:
            # Content of the current hunk
            current_hunk['lines'].append(line)

    # Add the last file if there is one
    if current_file:
        files.append(current_file)

    return files

def filter_diff_by_patterns(parsed_diff: List[Dict[str, Any]], exclude_patterns: List[str]) -> List[Dict[str, Any]]:
    """
    Filter the parsed diff to exclude files matching specific patterns.
    
    Args:
        parsed_diff: List of dictionaries with parsed diff information
        exclude_patterns: List of glob patterns for files to exclude
        
    Returns:
        Filtered list of file dictionaries
    """
    # Skip empty patterns
    if not exclude_patterns or all(not pattern for pattern in exclude_patterns):
        return parsed_diff
    
    # Filter out files that match any of the exclude patterns
    filtered = [
        file for file in parsed_diff
        if not any(
            fnmatch.fnmatch(file.get('path', ''), pattern) 
            for pattern in exclude_patterns 
            if pattern
        )
    ]
    
    excluded_count = len(parsed_diff) - len(filtered)
    if excluded_count > 0:
        print(f"Excluded {excluded_count} files based on patterns: {exclude_patterns}")
    
    return filtered