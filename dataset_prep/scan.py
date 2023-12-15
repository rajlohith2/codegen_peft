import requests
import subprocess
from time import sleep
from requests.auth import HTTPBasicAuth
import pandas as pd
import os
import stat
import csv
sonar_url = 'http://localhost:9000'
admin_token = 'squ_78240ebee56c48134afd37e55a901fb83f8c503a'  # Token with permissions to create projects and tokens


def create_project_and_token(project_name):
    # Create project
    create_project_response = requests.post(f"{sonar_url}/api/projects/create", 
                                            data={'name': project_name, 'project': project_name},
                                            auth=(admin_token, ''))
    if create_project_response.status_code != 200:
        raise Exception(f"Failed to create project: {create_project_response.text}")

    # Generate token
    generate_token_response = requests.post(f"{sonar_url}/api/user_tokens/generate", 
                                            data={'name': project_name},
                                            auth=(admin_token, ''))

    if generate_token_response.status_code != 200:
        raise Exception(f"Failed to generate token: {generate_token_response.text}")

    # Extracting the token from the response
    token_data = generate_token_response.json()
    if 'token' not in token_data:
        raise Exception("Token not found in the response")
    token = token_data['token']

    return project_name, token

def configure_and_run_analysis(project_key, token):
    # Define the directory you want to change to
    path = 'C:\codegen_peft\dataset_prep\\' + project_key
    # Define the command you want to execute
    command = "mvn clean verify sonar:sonar -Dsonar.projectKey=" + project_key + " -Dsonar.login=" + token + " -DskipTests"
    # Run the command in the specified directory
    completed_process = subprocess.run(command, shell=True, check=True, text=True, cwd=path)

    # Print the output (if any)
    print("Status code:", completed_process.returncode)
    if completed_process.stdout:
        print("Output:", completed_process.stdout)
    if completed_process.stderr:
        print("Error:", completed_process.stderr)

project_name, token = create_project_and_token('guava')
configure_and_run_analysis(project_name, token)