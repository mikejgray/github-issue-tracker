from os import getenv
import time
import requests
from tabulate import tabulate
import csv

# Constants
GITHUB_API = getenv("GITHUB_API", "https://api.github.com")
ORGANIZATION = getenv("GH_ORGANIZATION")
TOKEN = getenv("GH_TOKEN")
MAX_BODY_LENGTH = int(
    getenv("MAX_BODY_LENGTH", "100")
)  # Maximum characters of the issue body to display
CSV_FILENAME = getenv("CSV_FILENAME", f"{ORGANIZATION}_issues.csv")

if not TOKEN:
    raise ValueError("GH_TOKEN environment variable is required.")
if not ORGANIZATION:
    raise ValueError("GH_ORGANIZATION environment variable is required.")

# Headers for authentication
headers = {
    "Authorization": f"token {TOKEN}",
    "Accept": "application/vnd.github.v3+json",
}


def truncate_text(text, max_length):
    """Truncate text to a maximum length, adding ellipsis if shortened."""
    return (text[:max_length] + "...") if text and len(text) > max_length else text


def get_paginated_data(url):
    """Retrieve data from paginated API endpoints."""
    data = []
    while url:
        response = requests.get(url, headers=headers, timeout=5)
        if response.status_code == 403 and "rate limit" in response.text.lower():
            # Handle rate limiting
            retry_after = int(response.headers.get("Retry-After", 60))
            print(f"Rate limit exceeded. Retrying after {retry_after} seconds.")
            time.sleep(retry_after)
            continue

        response.raise_for_status()  # Raise an exception for HTTP errors
        data.extend(response.json())
        url = response.links.get("next", {}).get("url")  # Get the URL for the next page
    return data


def get_repos(org):
    """Get a list of non-archived repositories in the organization."""
    url = f"{GITHUB_API}/orgs/{org}/repos"
    all_repos = get_paginated_data(url)
    return [repo for repo in all_repos if not repo["archived"]]


def get_issues(org, repo):
    """Get issues (excluding pull requests) for a given repository."""
    url = f"{GITHUB_API}/repos/{org}/{repo}/issues"
    all_issues = get_paginated_data(url)
    return [issue for issue in all_issues if "pull_request" not in issue]


def sort_issues(issues):
    """Sort issues by prioritizing 'bug' and 'breaking' labels."""

    def priority(issue):
        labels = [label["name"].lower() for label in issue["labels"]]
        return ("bug" in labels, "breaking" in labels, issue["repository"])

    return sorted(issues, key=priority, reverse=True)


def write_to_csv(issues):
    """Write issues to a CSV file."""
    with open(CSV_FILENAME, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(
            [
                "Title",
                "State",
                "Labels",
                "Created At",
                "Updated At",
                "Body",
                "URL",
                "Repository",
            ]
        )
        for issue in issues:
            labels = ", ".join([label["name"] for label in issue["labels"]])
            body = truncate_text(issue["body"], MAX_BODY_LENGTH)
            writer.writerow(
                [
                    issue["title"],
                    issue["state"],
                    labels,
                    issue["created_at"],
                    issue["updated_at"],
                    body,
                    issue["html_url"],
                    issue["repository"],
                ]
            )


def main():
    """Main function to fetch, sort, display, and write issues to CSV."""
    all_issues = []
    repos = get_repos(ORGANIZATION)
    for repo in repos:
        repo_name = repo["name"]
        issues = get_issues(ORGANIZATION, repo_name)
        for issue in issues:
            issue[
                "repository"
            ] = repo_name  # Add repository name to issue for sorting and output
            all_issues.append(issue)

    sorted_issues = sort_issues(all_issues)
    write_to_csv(sorted_issues)

    for repo in repos:
        repo_issues = [
            issue for issue in sorted_issues if issue["repository"] == repo["name"]
        ]
        if repo_issues:
            issue_data = []
            for issue in repo_issues:
                labels = ", ".join([label["name"] for label in issue["labels"]])
                body = truncate_text(issue["body"], MAX_BODY_LENGTH)
                issue_data.append(
                    [
                        issue["title"],
                        issue["state"],
                        labels,
                        issue["created_at"],
                        issue["updated_at"],
                        body,
                        issue["html_url"],
                    ]
                )

            print(f"\nRepository: {repo['name']} - Issues:\n{'=' * 50}")
            print(
                tabulate(
                    issue_data,
                    headers=[
                        "Title",
                        "State",
                        "Labels",
                        "Created At",
                        "Updated At",
                        "Body",
                        "URL",
                    ],
                )
            )


if __name__ == "__main__":
    main()
