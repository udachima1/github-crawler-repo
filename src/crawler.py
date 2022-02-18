#!/usr/bin/env python

import json
import os
from base64 import b64decode
from os.path import dirname, join

import github3
from dotenv import load_dotenv

from flask import Flask, render_template, jsonify
server = Flask(__name__)

@server.route("/")
def get_GH_repos_information():
  
  # Load environment variables from file
  dotenv_path = join(dirname(__file__), ".env")
  load_dotenv(dotenv_path)
  
  # Authenticate to GitHub.com
  ghe = os.getenv("GH_ENTERPRISE_URL", default="").strip()
  if ghe:
    gh = github3.github.GitHubEnterprise(ghe, token=os.getenv("GH_TOKEN"))
  else:
    gh = github3.login(token=os.getenv("GH_TOKEN"))
    
# Set the topic
topic = os.getenv("TOPIC")
organization = os.getenv("ORGANIZATION")

# Get all repos from organization
search_string = "org:{} topic:{}".format(organization, topic)
all_repos = gh.search_repositories(search_string)
repo_list = []

for repo in all_repos:
  if repo is not None:
    print("{0}".format(repo.repository))
    full_repository = repo.repository.refresh()
    
    innersource_repo =repo.as_dict()
    innersource_repo["_InnerSourceMetadata"] = {}
    
    # fetch innersource.json
    try:
      content = repo.repository.file_contents("/innersource.json").content
      metadata = json.loads(b64decode(content))
      
      innersource_repo["_InnerSourceMetadata"] = metadata
    except github3.exceptions.NotFoundError:
      # innersource.json not found in repository, but it's not required
      pass
    
    # fetch repository participation
    participation = repo.repository.weekly_commit_count()
    innersource_repo["_InnerSourceMetadata"]["participation"] = participation["all"]
    
    # fetch contributing guidelines
    try:
      # if CONTRIBUTING.md exists in the repository, then link to that instead of repo root
      content = repo.repository.file_contents("/cONTRIBUTING.md").content
      innersource_repo["_InnerSourceMetadata"]["guidelines"] = "CONTRIBUTING.md"
    except github3.exceptions.NotFoundError:
      # CONTRIBUTING.md not found in repository, but it is not required
      pass
    
    # fetch repository topics
    topics = repo.repository.topics()
    innersource_repo["_InnerSourceMetadata"]["topics"] = topics.names
    
    repo_list.append(innersource_repo)
   
 # Write each repository to a repos.json file
 with open("repos.json", "w") as f:
   json.dump(repo_list, f, indent=4)
  
 return render_template('index.html', title="page", repo_list=repo_list)

if __name__ == "_main_":
  server.run(host='0.0.0.0')
