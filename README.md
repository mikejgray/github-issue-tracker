# github-issue-tracker

A basic Python script to crawl a GitHub organization's repositories and pull information on all issues.

The information will be output to a CSV file, and a pretty report will be printed to the console.

Handles rate limiting and pagination.

Outputs a pretty report using [tabulate](https://pypi.org/project/tabulate/).

## Usage

```sh
# Requires Python Poetry
poetry install
GH_ORGANIZATION=YourOrgHere GH_TOKEN=gh_EGHRIUHGJOEHOT poetry run python github_issue_tracker/main.py
```

Only `GH_ORGANIZATION` and `GH_TOKEN` are required, but there are a few other environment variables you can set:

- `GITHUB_API`: Defaults to `https://api.github.com`
- `MAX_BODY_LENGTH`: Defaults to `100` characters
- `CSV_FILENAME`: Defaults to `$GH_ORGANIZATION_issues.csv`

## Contributing

Contributions welcome! This is a first pass at a script to help me with a specific task, so there's a lot of room for improvement.
