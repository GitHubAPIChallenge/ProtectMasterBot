import os
import jwt
import sys
import json
import requests
import bcrypt
import secrets
from datetime import timedelta, datetime

class GitHubTokenClient:
    def __init__(self, app_id, app_pem, installation_id):
        self.app_id = app_id
        self.app_pem = app_pem
        self.private_key = app_pem.encode()
        self.installation_id = installation_id

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

    def get_installation(self):
        jwt = self.generate_jwt_token()
        response = requests.get(
            f'https://api.github.com/app/installations/{ self.installation_id }',
            headers= {
                'Authorization': f'Bearer { jwt }',
                'Accept': 'application/vnd.github.v3+json'
            }
        )
        return json.loads(response.text)['account']['login']

    def generate_password(self):
        password = secrets.token_urlsafe(16) # for user
        hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt(12)).decode('utf-8') # for db
        print(hash)
        return {
            "password": password, # will be given_password
            "hash": hash # will be saved_password
        }

    def validate_password(self, given_password, saved_password):
        hash = bcrypt.checkpw(given_password.encode(), saved_password.encode())
        return hash

    def get_token(self):
        jwt = self.generate_jwt_token()
        response = requests.post(
            f'https://api.github.com/app/installations/{ self.installation_id }/access_tokens',
            headers= {
                'Authorization': f'Bearer { jwt }',
                'Accept': 'application/vnd.github.machine-man-preview+json'
            }
        )
        return json.loads(response.text).get('token')