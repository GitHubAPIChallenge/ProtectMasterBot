import os
import base64
import logging
import requests 
from textwrap import dedent

# ---------------------------------------------------------
# 
#  This is a class to handle GitHub API access
# 
# ---------------------------------------------------------

class GitHubClient:
    def __init__(self, access_token, org, repo, branch):
        self.access_token = access_token
        self.org = org
        self.repo = repo
        self.branch = branch

    # API Request to create README.md
    def create_readme(self):
        text = self.get_readme_text()
        try:
            r = requests.put(
                f"https://api.github.com/repos/{ self.org }/{ self.repo }/contents/README.md",
                headers = {
                    'Authorization': f"Token { self.access_token }"
                },
                json = {
                    "message": "Added README.md",
                    "committer": {
                        "name": "Protect Master Bot",
                        "email": "protect@hattori.dev"
                    },
                    "content": base64.b64encode(text.encode('utf-8')).decode()
                }
            )
        except requests.exceptions.RequestException:
            logging.error("RequestException while contents creation.")
        return r

        

    # API request to protect repository
    def protect_repository(self, protection_rules):
        headers = {
            'Accept': 'application/vnd.github.luke-cage-preview+json',
            'Authorization': f"Token { self.access_token }"
        }
        try:
            r = requests.put(
                f"https://api.github.com/repos/{ self.org }/{ self.repo }/branches/{ self.branch }/protection",
                headers = headers,
                json = protection_rules
            )
            # if default branch was actually "main", try to protect main as well.
            if r.status_code == 404:
                r = requests.put(
                    f"https://api.github.com/repos/{ self.org }/{ self.repo }/branches/main/protection",
                    headers = headers,
                    json = protection_rules
                )
        except requests.exceptions.RequestException:
            logging.error("RequestException while branch protection")
        return r



    # API request for an issue creation
    def create_issue(self, mention, protection_rules=False):
        payload = {
            'title': 'Your default branch is not protected.',
            'body': f"{ mention }\n\n" + self.get_failure_text()
        }

        # if protection_rules is passed
        if protection_rules:
            payload = {
                'title': 'Your default branch is protected now!',
                'body': f'{ mention }\n\n' + self.get_success_text(protection_rules)
            }

        try:
            r = requests.post(
                f"https://api.github.com/repos/{ self.org }/{ self.repo }/issues",
                headers = {
                    'Accept': 'application/vnd.github.squirrel-girl-preview',
                    'Authorization': f"Token { self.access_token }"
                },
                json = payload
            )
        except requests.exceptions.RequestException:
            logging.error("RequestException while branch protection")
        return r

    # Read json argument in a safe way
    def read_json_safe(self, json, *args):
        param = ""
        try:
            if len(args) == 1:
                param = json[args[0]]
            elif len(args) == 2: 
                param = json[args[0]][args[1]]
            elif len(args) == 3: 
                param = json[args[0]][args[1]][args[2]]
        except:
            logging.error("Failed to parse rule json")
            pass

        if isinstance(param, list):
            param = ", ".join(param)

        return param

    # Get formated text for successful branch protection
    def get_success_text(self, protection_rules):
        try: 
            text = dedent((f'''
The default branch has just been protected. Please refer the setting like below.\n\n
Rule                            |                                   |               | Parameter
------------                    | -------------                     | ------------  | ------------- 
required_status_checks          | strict                            |               | { self.read_json_safe(protection_rules, "required_status_checks", "strict") }
|                               | contexts                          |               | { self.read_json_safe(protection_rules, "required_status_checks", "contexts") }
enforce_admins                  |                                   |               | { self.read_json_safe(protection_rules, "enforce_admins") }
required_pull_request_reviews   | dismissal_restrictions            | users         | { self.read_json_safe(protection_rules, "required_pull_request_reviews", "dismissal_restrictions", "users") }
|                               |                                   | teams         | { self.read_json_safe(protection_rules, "required_pull_request_reviews", "dismissal_restrictions", "teams") }
|                               |                                   | apps          | { self.read_json_safe(protection_rules, "required_pull_request_reviews", "dismissal_restrictions", "apps" ) }
|                               | dismiss_stale_reviews             |               | { self.read_json_safe(protection_rules, "required_pull_request_reviews", "dismiss_stale_reviews") }
|                               | require_code_owner_reviews        |               | { self.read_json_safe(protection_rules, "required_pull_request_reviews", "require_code_owner_reviews") }
|                               | required_approving_review_count   |               | { self.read_json_safe(protection_rules, "required_pull_request_reviews", "required_approving_review_count") }
restrictions                    | users                             |               | { self.read_json_safe(protection_rules, "restrictions", "users") }
|                               | teams                             |               | { self.read_json_safe(protection_rules, "restrictions", "teams") }
|                               | apps                              |               | { self.read_json_safe(protection_rules, "restrictions", "apps") }
required_linear_history         |                                   |               | { self.read_json_safe(protection_rules, "required_linear_history") }
allow_force_pushes              |                                   |               | { self.read_json_safe(protection_rules, "allow_force_pushes") }
allow_deletions                 |                                   |               | { self.read_json_safe(protection_rules, "allow_deletions") }
\n\n
For more information about brunch protection, please refer the below links.\n
Docs: https://docs.github.com/en/free-pro-team@latest/github/administering-a-repository/configuring-protected-branches\n
API: https://developer.github.com/v3/repos/branches/#update-branch-protection
''')).strip()
        except:
            text = "Given branch protection json payload couldn't be read"
            logging.error("Couldn't format protection rules text. Please check the log")
        return text

    # Get text for failed branch protection
    def get_failure_text(self):
        return '''
Please check your branch status. \n
Note: To protect private repository's branch, you need to be a premium user. If so, please consider to upgrade the plan!\n
For more information about plans, please refer the below links.\n
https://github.com/pricing
'''

    # Get text for README.md
    def get_readme_text(self):
        return '''
# README.md
ProtectMasterBot initiated this repository. 
Please take a look at the [issue](https://github.com/{ self.org }/{ self.repo }/issues/1) for more information about protection!
'''
