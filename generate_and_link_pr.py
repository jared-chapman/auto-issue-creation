import os
import re
from datetime import datetime
import pytz
from github import Github
import csv

import csv_tools

# Load environment variables
APP_ID = os.environ.get('APP_ID')
INSTALLATION_ID = os.environ.get('INSTALLATION_ID')
CLIENT_ID = os.environ.get('CLIENT_ID')
CLIENT_SECRET = os.environ.get('CLIENT_SECRET')
PEM_KEY = os.environ.get('PEM_KEY')

REPO_NAME = ''
CSV_FILE_PATH = 'pr_issues.csv'

# Authenticate and get the GitHub client
def get_github_client(app_id, installation_id, pem_key):
    from github import GithubIntegration
    
    # Create an instance of GithubIntegration
    integration = GithubIntegration(app_id, pem_key)
    
    # Get the access token for the installation
    access_token = integration.get_access_token(installation_id).token
    
    # Return a Github client authenticated with the access token
    return Github(access_token)

def create_issue_and_link_pr(repo_name, pr_number, issue_description, pr_title):
    github_client = get_github_client(APP_ID, INSTALLATION_ID, PEM_KEY)
    repo = github_client.get_repo(repo_name)

    # Create a new issue
    new_issue = repo.create_issue(
        title=pr_title,
        body=issue_description
    )
    # Link the new issue to the PR
    pr = repo.get_pull(int(pr_number))
    pr.create_issue_comment(f"Linked to issue #{new_issue.number}")
    csv_tools.set_linked(pr_number, repo_name, new_issue.number)
    print(f"Created issue 1067 for PR #{pr_number} and linked it.")

def process_csv(csv_file_path, repo_name):
    with open(csv_file_path, mode='r', newline='') as file:
        reader = csv.reader(file)
        next(reader)  # Skip the header row if it exists

        for row in reader:
            pr_number = row[0]  # PR number
            linked_to_pr = row[3].lower() == 'true'  # Is the issue linked to a PR?
            issue_description = row[6]  # Description
            pr_title = row[5]

            # Only create issues for PRs that aren't linked
            if not linked_to_pr:
                create_issue_and_link_pr(repo_name, pr_number, issue_description, pr_title)


# Process the CSV and create issues for unlinked PRs
process_csv(CSV_FILE_PATH, REPO_NAME)