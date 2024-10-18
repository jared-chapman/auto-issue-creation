import openai
import csv_tools

# Replace with OpenAI API key
OPENAI_API_KEY = ''

# Set up the OpenAI API key
openai.api_key = OPENAI_API_KEY

def generate_issue_description(pr_title, pr_description):
    """Generate an issue description based on the PR title and description."""
    messages = [
        {"role": "system", "content": "You are a helpful assistant that generates GitHub issue descriptions."},
        {"role": "user", "content": f"Generate a very short GitHub issue description based on the following pull request title and description. \n\n"
                                    f"It should be 1 to 2 sentences and provide instructions for creating the existing PR.\n\n"
                                    f"PR Title: {pr_title}\n"
                                    f"PR Description: {pr_description}\n\n"
                                    f"Issue Description:"}
    ]

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages,
        max_tokens=150,
        temperature=0.7,
        n=1,
        stop=None
    )

    # Extract the generated text from the response
    issue_description = response.choices[0].message['content'].strip()
    return issue_description

# get prs from csv with missing issue descriptions
prs = csv_tools.get_prs_without_issue_descriptions()

for pr in prs:
    pr_number = pr[0]
    repo_name = pr[1]
    pr_title = pr[5]
    pr_description = pr[7]
    print('generating issue description for pr', pr_number, 'in', repo_name, 'with title:', pr_title, 'and description:', pr_description)
    issue_description = generate_issue_description(pr_title, pr_description).replace("\n", " ")
    csv_tools.update_issue_description(pr_number, repo_name, issue_description)