import os
import jwt
import sys
import json
import logging
import requests
from datetime import timedelta, datetime

# ---------------------------------------------------------
# 
#  This is a class to handle GitHub Apps credentials and related info.
# 
# ---------------------------------------------------------

class GitHubTokenClient:
    def __init__(self, app_id, app_pem, installation_id):
        self.app_id = app_id
        self.private_key = app_pem.encode()
        self.installation_id = installation_id

    # Generate JWT Token from private key
    def generate_jwt_token(self):
        alg = 'RS256'
        utcnow = datetime.utcnow()
        payload = {
            'typ': 'JWT',
            'alg': alg,
            'iat': utcnow,
            'exp': utcnow + timedelta(seconds=30),
            'iss': self.app_id
        }
        return jwt.encode(payload, self.private_key, algorithm=alg).decode('utf-8')

    # Get GitHub Apps installation information. This function returns org name.
    def get_installation(self):
        org = ""
        jwt = self.generate_jwt_token()
        try:
            response = requests.get(
                f'https://api.github.com/app/installations/{ self.installation_id }',
                headers= {
                    'Authorization': f'Bearer { jwt }',
                    'Accept': 'application/vnd.github.v3+json'
                }
            )
            org = json.loads(response.text)['account']['login']
        except requests.exceptions.RequestException:
            logging.error("RequestException while getting installation info.")
        except KeyError:
            logging.error("KeyError occured while getting installation info.")
        except TypeError:
            logging.error("TypeError occured while getting installation info.")
        except Exception as e:
            logging.error(e)
        return org
        


    # Issue access token for GitHub Apps.
    def get_token(self):
        jwt = self.generate_jwt_token()
        try:
            response = requests.post(
                f'https://api.github.com/app/installations/{ self.installation_id }/access_tokens',
                headers= {
                    'Authorization': f'Bearer { jwt }',
                    'Accept': 'application/vnd.github.machine-man-preview+json'
                }
            )
            return json.loads(response.text).get('token')
        except requests.exceptions.RequestException:
            logging.error("RequestException while contents creation.")
            return ""
