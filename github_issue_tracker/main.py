from os import environ
import requests
import time
from tabulate import tabulate

# Constants
GITHUB_API = "https://api.github.com"
ORGANIZATION = "OpenVoiceOS"  # Replace with your organization name
TOKEN = environ["GH_TOKEN"]

# Headers for authentication
headers = {
    "Authorization": f"token {TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}

def get_paginated_data(url):
    """Retrieve data from paginated API endpoints."""
    data = []
    while url:
        response = requests.get(url, headers=headers)
        if response.status_code == 403 and 'rate limit' in response.text.lower():
            # Handle rate limiting
            retry_after = int(response.headers.get('Retry-After', 60))
            print(f"Rate limit exceeded. Retrying after {retry_after} seconds.")
            time.sleep(retry_after)
            continue

        response.raise_for_status()  # Raise an exception for HTTP errors
        data.extend(response.json())
        url = response.links.get('next', {}).get('url')  # Get the URL for the next page
    return data

def get_repos(org):
    """Get a list of repositories in the organization."""
    url = f"{GITHUB_API}/orgs/{org}/repos"
    return get_paginated_data(url)

def get_issues(org, repo):
    """Get issues for a given repository."""
    url = f"{GITHUB_API}/repos/{org}/{repo}/issues"
    return get_paginated_data(url)

def main():
    """Main function to fetch and display issues."""
    repos = get_repos(ORGANIZATION)
    for repo in repos:
        repo_name = repo['name']
        issues = get_issues(ORGANIZATION, repo_name)

        if issues:
            issue_data = []
            for issue in issues:
                labels = ", ".join([label['name'] for label in issue['labels']])
                issue_data.append([
                    issue['title'],
                    issue['state'],
                    labels,
                    issue['created_at'],
                    issue['updated_at'],
                    issue['html_url']
                ])

            print(f"\nRepository: {repo_name} - Issues:\n{'=' * 50}")
            print(tabulate(issue_data, headers=["Title", "State", "Labels", "Created At", "Updated At", "URL"]))

if __name__ == "__main__":
    main()
