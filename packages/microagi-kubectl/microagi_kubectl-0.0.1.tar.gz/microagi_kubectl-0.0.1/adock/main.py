
import openai

import argparse
from openai_api import translate_to_docker_command
from security import is_destructive

def execute_docker_command(command):
    """Executes a Docker command. For now, it's just a placeholder."""
    print(f"Executing: {command}")

def main():
    # Argument parser setup
    parser = argparse.ArgumentParser(description="Translate natural language to Docker commands with ADock.")
    parser.add_argument("command", type=str, nargs="*", help="The natural language instruction for ADock.")
    args = parser.parse_args()

    # Translate natural language to Docker command
    translation = translate_to_docker_command(' '.join(args.command))
    docker_command = translation["command"]

    # Check if the Docker command is potentially destructive
    is_dangerous, reason = is_destructive(docker_command)
    if is_dangerous:
        print(f"Warning! This command is potentially destructive because it {reason}. Proceed with caution.")

    # Provide the translated command to the user and optionally execute
    print(f"Translated Docker Command: {docker_command}")
    # Screen the translated Docker command
    if not is_allowed_command(docker_command):
        print("Error: The translated Docker command is not recognized or allowed.")
        return

    # For now, we'll just print it. Later, we can add functionality to execute the command.
    # execute_docker_command(docker_command.split())

if __name__ == "__main__":
    main()

from .config import ALLOWED_COMMANDS

def is_allowed_command(command):
    """Checks if the translated Docker command is part of ALLOWED_COMMANDS."""
    for allowed_command in ALLOWED_COMMANDS:
        if command.startswith(allowed_command):
            return True
    return False

import requests

OPENAI_API_ENDPOINT = "https://api.openai.com/v1/engines/davinci/completions"  # Placeholder endpoint
OPENAI_API_KEY = "YOUR_OPENAI_API_KEY"  # Placeholder API key


def fetch_dockerfile_from_openai(project_type="default"):
    """Makes an API call to OpenAI to fetch a Dockerfile based on the project type."""
    try:
        # Use the chat-based interface of gpt-3.5-turbo to request a Dockerfile
        response = openai.Completion.create(
            engine="gpt-3.5-turbo",
            prompt=f"Provide a Dockerfile for a {project_type} project.",
            max_tokens=300
        )
        dockerfile_content = response.choices[0].text.strip()
        
        with open("Dockerfile", "w") as dockerfile:
            dockerfile.write(dockerfile_content)
        print("Dockerfile initialized based on project type:", project_type)
    except Exception as e:
        print(f"Error fetching Dockerfile: {e}")

    """Makes an API call to OpenAI to fetch a Dockerfile based on the project type."""
    # Define the payload for the API call
    payload = {
        "prompt": f"Generate a Dockerfile for a {project_type} project.",
        "max_tokens": 150  # Limiting the response length for demonstration
    }
    
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }
    
    try:
        # Placeholder API call
        # In a real-world scenario, uncomment the lines below to make the actual API call
        # response = requests.post(OPENAI_API_ENDPOINT, json=payload, headers=headers)
        # dockerfile_content = response.json().get("choices", [{}])[0].get("text", "").strip()

        # Mock Dockerfile content for demonstration
        dockerfile_content = "FROM python:3.8\nWORKDIR /app\nCOPY . .\nCMD ["python", "app.py"]"
        
        with open("Dockerfile", "w") as dockerfile:
            dockerfile.write(dockerfile_content)
        print("Dockerfile initialized based on project type:", project_type)
    except Exception as e:
        print(f"Error fetching Dockerfile: {e}")
