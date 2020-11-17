import os
import sys
import uuid
import bcrypt

def generate_password():
    password = uuid.uuid4().hex
    hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt(12)).decode('utf-8') # for db
    print(hash)
    return {
        "password": password, # will be given_password
        "hash": hash # will be saved_password
    }

def validate_password(given_password, saved_password):
    hash = bcrypt.checkpw(given_password.encode(), saved_password.encode())
    return hash