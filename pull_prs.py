import os
import re
from datetime import datetime
import pytz
from github import Github

import csv_tools

# Load environment variables
APP_ID = os.environ.get('APP_ID')
INSTALLATION_ID = os.environ.get('INSTALLATION_ID')
CLIENT_ID = os.environ.get('CLIENT_ID')
CLIENT_SECRET = os.environ.get('CLIENT_SECRET')
PEM_KEY = os.environ.get('PEM_KEY')

REPO_NAME = ''

date_threshold = datetime(2024, 7, 1, tzinfo=pytz.UTC)
number_to_check = 5

# Authenticate and get the GitHub client
def get_github_client(app_id, installation_id, pem_key):
    from github import GithubIntegration
    
    # Create an instance of GithubIntegration
    integration = GithubIntegration(app_id, pem_key)
    
    # Get the access token for the installation
    access_token = integration.get_access_token(installation_id).token
    
    # Return a Github client authenticated with the access token
    return Github(access_token)

# Fetch PRs not linked to issues
def fetch_unlinked_prs(repo_name):
    g = get_github_client(APP_ID, INSTALLATION_ID, PEM_KEY)

    repo = g.get_repo(repo_name)

    

    unlinked_prs = []
    linked_prs = set()  # Track PRs that are linked to issues

    issue_count = 0
    # Check for cross-referenced events in the issue timeline
    for issue in repo.get_issues(state='all', since=date_threshold):
        if issue_count >= number_to_check or issue.created_at < date_threshold:
            break
        issue_count += 1
        print('issue', issue.number, issue.title)
        for event in issue.get_events():
            # print(' - ', event.event)
            if event.event == 'cross-referenced' and event.source:
                # Add the PR number if the event is related to a pull request
                linked_prs.add(event.source.issue.pull_request.number)

    # Fetch pull requests and check if they're in the linked_prs set
    pr_count = 0
    all_prs = repo.get_pulls(state='closed', sort='created', direction='desc')
    print('total prs:', all_prs.totalCount)
    for pr in all_prs:
        print('pr', pr.number, pr.title)
        if pr_count >= number_to_check or pr.created_at < date_threshold:
            print('breaking')
            break
        pr_count += 1
        if pr.closed_at and pr.closed_at >= date_threshold:
        # uncomment next to lines to only store unlinked prs
            if pr.number not in linked_prs:
                # regex to remove HTML comments
                cleaned_description = re.sub(r'<!--.*?-->', '', pr.body, flags=re.DOTALL).strip() 
                # put clean_description into a single line
                cleaned_description = re.sub(r'\s+', ' ', cleaned_description)
                
                pr_info = {
                    'pr_number': pr.number,
                    'pr_name': pr.title,
                    'pr_description': cleaned_description,
                    'closed_at': pr.closed_at,
                    'linked_to_issue': pr.number in linked_prs,
                    'url': pr.html_url
                }
                unlinked_prs.append(pr_info)

    return unlinked_prs



unlinked_prs = fetch_unlinked_prs(REPO_NAME)
print('unlinked prs:', unlinked_prs)

for pr in unlinked_prs:
    csv_tools.add_row_to_csv(pr['pr_number'], REPO_NAME, '', pr['linked_to_issue'], pr['url'], pr['pr_name'], pr['pr_description'],'')
csv_tools.remove_duplicates()