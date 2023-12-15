import requests
import subprocess
from time import sleep
from requests.auth import HTTPBasicAuth
import pandas as pd
import os
import stat
import csv

def rmtree(top):
    for root, dirs, files in os.walk(top, topdown=False):
        for name in files:
            filename = os.path.join(root, name)
            os.chmod(filename, stat.S_IWUSR)
            os.remove(filename)
        for name in dirs:
            os.rmdir(os.path.join(root, name))
    os.rmdir(top) 
# SonarQube server details
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

def configure_and_run_analysis(project_key, token, build):
    # Define the directory you want to change to
    path = 'C:\codegen_peft\dataset_prep\\' + project_name
    # Define the command you want to execute
    command = "mvn clean verify sonar:sonar -Dsonar.projectKey=" + project_key + " -Dsonar.login=" + token
    # Run the command in the specified directory
    completed_process = subprocess.run(command, shell=True, check=True, text=True, cwd=path)

    # Print the output (if any)
    print("Status code:", completed_process.returncode)
    if completed_process.stdout:
        print("Output:", completed_process.stdout)
    if completed_process.stderr:
        print("Error:", completed_process.stderr)
    # Define the metrics to retrieve
    metrics = []
    # Construct the URL for the metrics API
    sleep(30)

    url2 = f"{sonar_url}/api/metrics/search?project={project_key}"
    # Make the request to SonarQube API
    response2 = requests.get(url2)
    for metric in response2.json()['metrics']:
        metrics.append(metric['key'])
    url = f"{sonar_url}/api/measures/component?component={project_key}&metricKeys={','.join(metrics)}"
    response = requests.get(url, auth=HTTPBasicAuth(admin_token, ""))

    # Check if the request was successful
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception("Failed to retrieve metrics: " + response.text)

file_path = 'top_projects.csv'
chunk_size = 100  # You can adjust this based on your system's memory capacity
i = 0
for chunk in pd.read_csv(file_path, chunksize=chunk_size):
    for _, repo_url in chunk.iterrows():
        base_url = "https://github.com/"
        repo = repo_url['github']
        version = repo_url['version']
        build = repo_url['build']
        if repo != 'newbee-ltd/newbee-mall':
            continue
        if build not in ('maven'):
            print("Build tool not supported")
            continue
        full_url = f"{base_url}{repo}"
        print(full_url)
        project_name = repo_url['github'].split('/')[1]
        try:
            print(f"Analyzing {repo_url['github']}")
            # Clone the repository
            subprocess.run(f"git clone {full_url}", shell=True, check=True)
            checkout_command = f"cd C:\codegen_peft\dataset_prep\{project_name} && git checkout {version}"
            sleep(5)
            subprocess.run(checkout_command, shell=True, check=True)
            project_key, user_token = create_project_and_token(project_name)
            response = configure_and_run_analysis(project_key, user_token, build)
            results = {}
            if i == 0:
                results['project'] = 'project'
                results['repo'] = 'repo'
                results['version'] = 'version'
                for metric in response['component']['measures']:
                    results[metric['metric']] = metric['metric']
                with open ('results.csv', 'a') as f:
                    writer = csv.DictWriter(f, fieldnames=results.keys())
                    writer.writeheader()
                i = 1
            results['project'] = project_name
            results['repo'] = repo_url['github']
            results['version'] = repo_url['version']
            print(response['component']['measures'])
            for metric in response['component']['measures']:
                if metric['value']:
                    results[metric['metric']] = metric['value']
            with open ('results.csv', 'a') as f:
                writer = csv.DictWriter(f, fieldnames=results.keys())
                writer.writerow(results)
            break
        except subprocess.CalledProcessError as e:
            print(f"Failed to clone {repo_url['github']}: {e}")
            continue
        finally:
            rmtree('C:\codegen_peft\dataset_prep\\' + project_name)