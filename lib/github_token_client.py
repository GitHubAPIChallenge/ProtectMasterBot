import os
import jwt
import json
import requests
from datetime import timedelta, datetime

class GitHubTokenClient:
    def __init__(self, app_id, app_pem, installation_id):
        self.app_id = app_id
        self.app_pem = app_pem
        self.private_key = app_pem.encode()
        self.installation_id = installation_id

        # from cryptography.hazmat.backends import default_backend
        # self.cert_bytes = app_pem.encode()
        # self.private_key = default_backend().load_pem_private_key(self.cert_bytes, None)

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

    def generate_headers(self):
        jwt = self.generate_jwt_token()
        return {
            'Authorization': f'Bearer { jwt }',
            'Accept': 'application/vnd.github.machine-man-preview+json',
        }

    def get_token(self):
        response = requests.post(
            f'https://api.github.com/app/installations/{ self.installation_id }/access_tokens',
            headers=self.generate_headers()
        )
        return json.loads(response.text).get('token')

    # Add Functions to get installation detail
        # https://api.github.com/app/installations/13018984