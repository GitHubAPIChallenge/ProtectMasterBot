import os
import re
import requests 
from textwrap import dedent

class GitHubClient:
    def __init__(self, access_token, org, repo, branch):
        self.access_token = access_token
        self.org = org
        self.repo = repo
        self.branch = branch

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
        print('ProtectMasterBot successfully protected the repository with { r1.status.code } code')


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
                    self.generate_issue(protection_rules) + 
                    "\n\nFor more information about brunch protection, please refer the below links\n" + 
                    "Docs: https://docs.github.com/en/free-pro-team@latest/github/administering-a-repository/configuring-protected-branches\n" +
                    "API: https://developer.github.com/v3/repos/branches/#update-branch-protection" 
            }
        )
        print('ProtectMasterBot successfully protected the repository with { r1.status.code } code')

    def generate_issue(self, protection_rule):
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