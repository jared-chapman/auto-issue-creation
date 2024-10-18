import os
import csv

CSV_FILE_PATH = 'pr_issues.csv'

def create_csv_if_not_exists():
    # Create the CSV file if it does not already exist.
    if not os.path.isfile(CSV_FILE_PATH):
        print('creating csv')
        with open(CSV_FILE_PATH, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['PR Number', 'Repo Name', 'Issue Number', 'Linked to PR', 'PR URL', 'PR Title', 'PR Description', 'Issue Description'])
        file.close()

def remove_duplicates():
    # Remove duplicate rows from the CSV file based on issue number and repo name.
    with open(CSV_FILE_PATH, mode='r') as file:
        reader = csv.reader(file)
        rows = [row for row in reader]

    # Exit if there are fewer than three rows
    if len(rows) < 3:
        return
    
    file.close()
    
    # Remove duplicates based on issue number and repo name
    unique_rows = [rows[0]]
    seen = set()
    for row in rows[1:]:
        print(row)
        key = (row[1], row[0])
        if key not in seen:
            unique_rows.append(row)
            seen.add(key)
    
    with open(CSV_FILE_PATH, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(unique_rows)
    
    file.close()

def add_row_to_csv(pr_number, repo_name, issue_number, linked_to_pr, url, pr_title, pr_description, issue_description):
  # Add a row to the CSV file.
  # Return if there's already a line with matching pr_number and repo_name
  with open(CSV_FILE_PATH, mode='r') as file: 
      reader = csv.reader(file)
      for row in reader:
          if row[0] == pr_number and row[1] == repo_name:
              return
  with open(CSV_FILE_PATH, mode='a', newline='') as file:
      writer = csv.writer(file)
      writer.writerow([pr_number, repo_name, issue_number, linked_to_pr, url, pr_title, pr_description, issue_description])
      file.close()

def get_prs_without_issue_descriptions():
    # Get PRs that are missing issue descriptions but that have PR title.
    remove_duplicates()
    with open(CSV_FILE_PATH, mode='r') as file:
        reader = csv.reader(file)
        # if row[6] (issue_description) is empty and if row[4] (pr_title) is not empty
        prs = [row for row in reader if row[7] == '' ]
    file.close()
    return prs

def update_issue_description(pr_number, repo_name, issue_description):
    # Update the issue description for a PR in the CSV file.
    with open(CSV_FILE_PATH, mode='r') as file:
        reader = csv.reader(file)
        rows = [row for row in reader]

    for row in rows:
        if row[0] == pr_number and row[1] == repo_name:
            row[7] = issue_description
            break

    with open(CSV_FILE_PATH, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(rows)

    file.close()

def set_linked(pr_number, repo_name, issue_number):
    # Set the 'Linked to PR' flag for a specific PR in the CSV file.
    print('setting linked for pr', pr_number, 'in', repo_name, 'to', issue_number)
    with open(CSV_FILE_PATH, mode='r') as file:
        reader = csv.reader(file)
        rows = [row for row in reader]

    for row in rows:
        if str(row[0]) == str(pr_number) and str(row[1]).lower() == str(repo_name).lower():
            print('hit')
            row[2] = issue_number
            row[3] = 'True'
            break

    with open(CSV_FILE_PATH, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(rows)

    file.close()