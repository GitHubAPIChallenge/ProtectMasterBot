import os
import re
import requests 
import base64
from textwrap import dedent

class GitHubClient:
    def __init__(self, access_token, org, repo, branch):
        self.access_token = access_token
        self.org = org
        self.repo = repo
        self.branch = branch

    def create_readme(self):
        text = f"""
# README.md
ProtectMasterBot initiated this repository. 
Master / Main branch is currently protected.
Please take a look at the [issue](https://github.com/{ self.org }/{ self.repo }/issues/1) for more information about protection!"""

        r = requests.put(
            f"https://api.github.com/repos/{ self.org }/{ self.repo }/contents/README.md",
            headers = {
                'Authorization': f"Token { self.access_token }"
            },
            json = {
                "message": "init!",
                "committer": {
                    "name": "Protect Master Bot",
                    "email": "protect@hattori.dev"
                },
                "content": base64.b64encode(text.encode('utf-8')).decode()
            }
        )

    # Protect repository
    def protect_repository(self, protection_rules):
        r = requests.put(
            f"https://api.github.com/repos/{ self.org }/{ self.repo }/branches/{ self.branch }/protection",
            headers = {
                'Accept': 'application/vnd.github.luke-cage-preview+json',
                'Authorization': f"Token { self.access_token }"
            },
            json = protection_rules
        )

        if r.status_code == 404:
            r = requests.put(
                f"https://api.github.com/repos/{ self.org }/{ self.repo }/branches/main/protection",
                headers = {
                    'Accept': 'application/vnd.github.luke-cage-preview+json',
                    'Authorization': f"Token { self.access_token }"
                },
                json = protection_rules
            )

        return r.status_code


    def create_issue(self, protection_rules):
        r = requests.post(
            f"https://api.github.com/repos/{ self.org }/{ self.repo }/issues",
            headers = {
                'Accept': 'application/vnd.github.squirrel-girl-preview',
                'Authorization': f"Token { self.access_token }"
            },
            json = {
                "title": "Your branch is protected now!",
                "body": "@yuhattor \n" + 
                    "The default branch has just been protected. Please refer the setting like below.\n" + 
                    self.generate_issue_text(protection_rules) + 
                    "\n\nFor more information about brunch protection, please refer the below links\n" + 
                    "Docs: https://docs.github.com/en/free-pro-team@latest/github/administering-a-repository/configuring-protected-branches\n" +
                    "API: https://developer.github.com/v3/repos/branches/#update-branch-protection" 
            }
        )

    def create_failure_issue(self):
        r = requests.post(
            f"https://api.github.com/repos/{ self.org }/{ self.repo }/issues",
            headers = {
                'Accept': 'application/vnd.github.squirrel-girl-preview',
                'Authorization': f"Token { self.access_token }"
            },
            json = {
                "title": "Your branch couldn't be protected.",
                "body": "@yuhattor \n" + 
                    "Please check if branch protection is applicable for the branch. If you are not premium user and want to use branch protection for private repos, please consider to upgrade the plan:)"
                    "\n\nFor more information about plans, please refer the below links\n" + 
                    "https://github.com/pricing\n"
            }
        )

    def generate_issue_text(self, protection_rule):
        return self.heredoc(f'''
            Rule                            |                                   |               | Parameter
            ------------                    | -------------                     | ------------  | ------------- 
            required_status_checks          | strict                            |               | { self.read_json(protection_rule, "required_status_checks", "strict") }
            |                               | contexts                          |               | { self.read_json(protection_rule, "required_status_checks", "contexts") }
            enforce_admins                  |                                   |               | { self.read_json(protection_rule, "enforce_admins") }
            required_pull_request_reviews   | dismissal_restrictions            | users         | { self.read_json(protection_rule, "required_pull_request_reviews", "dismissal_restrictions", "users") }
            |                               |                                   | teams         | { self.read_json(protection_rule, "required_pull_request_reviews", "dismissal_restrictions", "teams") }
            |                               |                                   | apps          | { self.read_json(protection_rule, "required_pull_request_reviews", "dismissal_restrictions", "apps" ) }
            |                               | dismiss_stale_reviews             |               | { self.read_json(protection_rule, "required_pull_request_reviews", "dismiss_stale_reviews") }
            |                               | require_code_owner_reviews        |               | { self.read_json(protection_rule, "required_pull_request_reviews", "require_code_owner_reviews") }
            |                               | required_approving_review_count   |               | { self.read_json(protection_rule, "required_pull_request_reviews", "required_approving_review_count") }
            restrictions                    | users                             |               | { self.read_json(protection_rule, "restrictions", "users") }
            |                               | teams                             |               | { self.read_json(protection_rule, "restrictions", "teams") }
            |                               | apps                              |               | { self.read_json(protection_rule, "restrictions", "apps") }
            required_linear_history         |                                   |               | { self.read_json(protection_rule, "required_linear_history") }
            allow_force_pushes              |                                   |               | { self.read_json(protection_rule, "allow_force_pushes") }
            allow_deletions                 |                                   |               | { self.read_json(protection_rule, "allow_deletions") }
            ''').replace(" ", "")          

    # json read safe
    def read_json(self, json, *args):
        param = "null"
        try:
            if len(args) == 1:
                param = json[args[0]]
            elif len(args) == 2: 
                param = json[args[0]][args[1]]
            elif len(args) == 3: 
                param = json[args[0]][args[1]][args[2]]
        except:
            pass

        if isinstance(param, list):
            param = ", ".join(param)
        return param

    def heredoc(self, str):
        return dedent(str).strip()