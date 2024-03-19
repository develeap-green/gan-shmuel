from flask import Flask, request, jsonify, render_template
from flask_mail import Message
from flask_mail import Mail
import logging
import subprocess
import os
import yaml
import requests
import shutil
from dotenv import load_dotenv
load_dotenv()

FLASK_SECRET_KEY = os.environ.get('FLASK_SECRET_KEY')
REPO_URL = os.environ.get('REPO_URL')
REPO_NAME = REPO_URL.split('/')[-1].split('.git')[0]
EMAILS = os.environ.get('EMAILS').split(',')

MAIL_SERVER = os.environ.get('MAIL_SERVER')
MAIL_PORT = os.environ.get('MAIL_PORT')
MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER')
SENDER_NAME = os.environ.get('SENDER_NAME')

# Logger config
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# App config
logger.info('Initializing Flask app')
app = Flask(__name__)

# Email config
app.config['MAIL_SERVER'] = MAIL_SERVER
app.config['MAIL_PORT'] = MAIL_PORT
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USERNAME'] = MAIL_USERNAME
app.config['MAIL_PASSWORD'] = MAIL_PASSWORD
app.config['MAIL_DEFAULT_SENDER'] = (SENDER_NAME, MAIL_DEFAULT_SENDER)
app.config['MAIL_SUPPRESS_SEND'] = False
app.config['MAIL_ASCII_ATTACHMENTS'] = False
mail = Mail(app)


COMMIT_MESSAGE = 'CI-commit'
URL_WEIGHT = 'http://greenteam.hopto.org:8081/health'
URL_BILLING = 'http://greenteam.hopto.org:8082/health'


def delete_repo():
    try:
        if os.path.exists(os.path.join(os.getcwd(), REPO_NAME)):
            logger.info(f"Deleting repo folder.")
            shutil.rmtree(REPO_NAME)
            logger.info(f"Repo folder successful deleted.")
    except:
        pass


def send_email(subject, html_page, stage):
    try:
        recipients = ' '.join([email.split('@')[0] for email in EMAILS])
        html_body = render_template(html_page, recipients=recipients, stage=stage)
        # msg = Message(subject, recipients=EMAILS, html=html_body)
        # mail.send(msg)
        logger.info(f"Email was sent successfully to {recipients}")
    except Exception as e:
        logger.error(f'Error sending email: {e}')

def copy_env(source_dir, dest_dir):
    env_files = {'weight.env', 'billing.env', 'nginx.conf'}
    for file in env_files:
        source_file = os.path.join(source_dir, file)
        dest_file = os.path.join(dest_dir, file)
        shutil.copy(source_file, dest_file)




@app.route('/', methods=['GET'])
def index():
    return jsonify({'status': 'success', 'message': 'Ok'}), 200


@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'success', 'message': 'Ok'}), 200


@app.route('/monitor', methods=['GET'])
def monitor():

    # Run the 'docker images' command
    process = subprocess.Popen(['docker', 'images'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output, error = process.communicate()

    if process.returncode != 0:
        return jsonify({'error': error.decode()}), 500

    lines = output.decode().split('\n')[1:]
    images_weight = []
    images_billing = []
    for line in lines:
        if line:
            parts = line.split()
            if parts[0] == 'weight-image':
                images_weight.append({
                    'repository': parts[0],
                    'tag': parts[1],
                    'image_id': parts[2],
                    'created': parts[4] + ' ' + parts[5] + ' ' + parts[6]
                })
            if parts[0] == 'billing-image':
                images_billing.append({
                    'repository': parts[0],
                    'tag': parts[1],
                    'image_id': parts[2],
                    'created': parts[4] + ' ' + parts[5] + ' ' + parts[6]
                })

    weight_status = False
    try:
      response = requests.get(URL_WEIGHT)
      if response.status_code == 200:
          weight_status = True
    except:
        pass

    billing_status = False
    try:
      response = requests.get(URL_BILLING)
      if response.status_code == 200:
          billing_status = True
    except:
        pass

    data = {
        'weight_status': billing_status,
        'billing_status': weight_status 
    }

    return render_template('monitor.html', data=data, images_weight=images_weight, images_billing=images_billing)
    

@app.route('/api/v1/rollback', methods=['POST'])
def rollback():
    try:

        weight_tag = int(request.form.get('weight_tag'))
        billing_tag = int(request.form.get('billing_tag'))

        if not weight_tag and not billing_tag:
            return jsonify({'message': 'Keeping current version.'}), 200



        # Check compose file to get last versions
        logger.info("Getting last version from dev compose file.")
        with open('./docker-compose.pro.yml', 'r') as file:
            compose_data = yaml.safe_load(file)

        weight = compose_data['services']['weight']['image']
        weight_default_name = weight.split(':')[0]
        ver_tag_w = int(weight.split(':')[1])

        billing = compose_data['services']['billing']['image']
        billing_deafult_name = billing.split(':')[0]
        ver_tag_b = int(billing.split(':')[1])


        # Replace production
        logger.info(f"Replacing production")
        FILE_COMPOSE_PROD = './docker-compose.pro.yml'
        change_version_w = subprocess.run(["sed", "-i", f"s/{weight_default_name}:{ver_tag_w}/{weight_default_name}:{weight_tag + 1}/", FILE_COMPOSE_PROD])
        change_version_b = subprocess.run(["sed", "-i", f"s/{billing_deafult_name}:{ver_tag_b}/{billing_deafult_name}:{billing_tag + 1}/", FILE_COMPOSE_PROD])


        replace_production = subprocess.run(["docker", "compose", "-f", "docker-compose.rollback.yml", "up", "-d"])
        if replace_production.returncode != 0:
            logger.error(f"Replacing production process failed.")
            send_email(subject='Deploy Failed', html_page='failed_email.html', stage='Replacing production')
            return jsonify({'error': 'Replacing production process failed.'}), 500


        send_email(subject='Rollback succeeded', html_page='success_email.html', stage='')
        return jsonify({'message': 'Rollback initiated successfully.'}), 200

    except Exception as e:
        logger.error(f"Faild to rollback.")
        return jsonify({'error': str(e)}), 500




data = {
  "ref": "refs/heads/main",
  "before": "c668f4e1158b53be784f277c4d775e118deb19fb",
  "after": "c2901b9c104a2d5fdef14518de149b8fdf3bd47a",
  "repository": {
    "id": 771988013,
    "node_id": "R_kgDOLgOaLQ",
    "name": "gan-shmuel",
    "full_name": "develeap-green/gan-shmuel",
    "private": False,
    "owner": {
      "name": "develeap-green",
      "email": '',
      "login": "develeap-green",
      "id": 163397731,
      "node_id": "O_kgDOCb1AYw",
      "avatar_url": "https://avatars.githubusercontent.com/u/163397731?v=4",
      "gravatar_id": "",
      "url": "https://api.github.com/users/develeap-green",
      "html_url": "https://github.com/develeap-green",
      "followers_url": "https://api.github.com/users/develeap-green/followers",
      "following_url": "https://api.github.com/users/develeap-green/following{/other_user}",
      "gists_url": "https://api.github.com/users/develeap-green/gists{/gist_id}",
      "starred_url": "https://api.github.com/users/develeap-green/starred{/owner}{/repo}",
      "subscriptions_url": "https://api.github.com/users/develeap-green/subscriptions",
      "organizations_url": "https://api.github.com/users/develeap-green/orgs",
      "repos_url": "https://api.github.com/users/develeap-green/repos",
      "events_url": "https://api.github.com/users/develeap-green/events{/privacy}",
      "received_events_url": "https://api.github.com/users/develeap-green/received_events",
      "type": "Organization",
      "site_admin": False
    },
    "html_url": "https://github.com/develeap-green/gan-shmuel",
    "description": '',
    "fork": False,
    "url": "https://github.com/develeap-green/gan-shmuel",
    "forks_url": "https://api.github.com/repos/develeap-green/gan-shmuel/forks",
    "keys_url": "https://api.github.com/repos/develeap-green/gan-shmuel/keys{/key_id}",
    "collaborators_url": "https://api.github.com/repos/develeap-green/gan-shmuel/collaborators{/collaborator}",
    "teams_url": "https://api.github.com/repos/develeap-green/gan-shmuel/teams",
    "hooks_url": "https://api.github.com/repos/develeap-green/gan-shmuel/hooks",
    "issue_events_url": "https://api.github.com/repos/develeap-green/gan-shmuel/issues/events{/number}",
    "events_url": "https://api.github.com/repos/develeap-green/gan-shmuel/events",
    "assignees_url": "https://api.github.com/repos/develeap-green/gan-shmuel/assignees{/user}",
    "branches_url": "https://api.github.com/repos/develeap-green/gan-shmuel/branches{/branch}",
    "tags_url": "https://api.github.com/repos/develeap-green/gan-shmuel/tags",
    "blobs_url": "https://api.github.com/repos/develeap-green/gan-shmuel/git/blobs{/sha}",
    "git_tags_url": "https://api.github.com/repos/develeap-green/gan-shmuel/git/tags{/sha}",
    "git_refs_url": "https://api.github.com/repos/develeap-green/gan-shmuel/git/refs{/sha}",
    "trees_url": "https://api.github.com/repos/develeap-green/gan-shmuel/git/trees{/sha}",
    "statuses_url": "https://api.github.com/repos/develeap-green/gan-shmuel/statuses/{sha}",
    "languages_url": "https://api.github.com/repos/develeap-green/gan-shmuel/languages",
    "stargazers_url": "https://api.github.com/repos/develeap-green/gan-shmuel/stargazers",
    "contributors_url": "https://api.github.com/repos/develeap-green/gan-shmuel/contributors",
    "subscribers_url": "https://api.github.com/repos/develeap-green/gan-shmuel/subscribers",
    "subscription_url": "https://api.github.com/repos/develeap-green/gan-shmuel/subscription",
    "commits_url": "https://api.github.com/repos/develeap-green/gan-shmuel/commits{/sha}",
    "git_commits_url": "https://api.github.com/repos/develeap-green/gan-shmuel/git/commits{/sha}",
    "comments_url": "https://api.github.com/repos/develeap-green/gan-shmuel/comments{/number}",
    "issue_comment_url": "https://api.github.com/repos/develeap-green/gan-shmuel/issues/comments{/number}",
    "contents_url": "https://api.github.com/repos/develeap-green/gan-shmuel/contents/{+path}",
    "compare_url": "https://api.github.com/repos/develeap-green/gan-shmuel/compare/{base}...{head}",
    "merges_url": "https://api.github.com/repos/develeap-green/gan-shmuel/merges",
    "archive_url": "https://api.github.com/repos/develeap-green/gan-shmuel/{archive_format}{/ref}",
    "downloads_url": "https://api.github.com/repos/develeap-green/gan-shmuel/downloads",
    "issues_url": "https://api.github.com/repos/develeap-green/gan-shmuel/issues{/number}",
    "pulls_url": "https://api.github.com/repos/develeap-green/gan-shmuel/pulls{/number}",
    "milestones_url": "https://api.github.com/repos/develeap-green/gan-shmuel/milestones{/number}",
    "notifications_url": "https://api.github.com/repos/develeap-green/gan-shmuel/notifications{?since,all,participating}",
    "labels_url": "https://api.github.com/repos/develeap-green/gan-shmuel/labels{/name}",
    "releases_url": "https://api.github.com/repos/develeap-green/gan-shmuel/releases{/id}",
    "deployments_url": "https://api.github.com/repos/develeap-green/gan-shmuel/deployments",
    "created_at": 1710411626,
    "updated_at": "2024-03-17T12:56:07Z",
    "pushed_at": 1710750244,
    "git_url": "git://github.com/develeap-green/gan-shmuel.git",
    "ssh_url": "git@github.com:develeap-green/gan-shmuel.git",
    "clone_url": "https://github.com/develeap-green/gan-shmuel.git",
    "svn_url": "https://github.com/develeap-green/gan-shmuel",
    "homepage": '',
    "size": 89,
    "stargazers_count": 0,
    "watchers_count": 0,
    "language": "Python",
    "has_issues": True,
    "has_projects": True,
    "has_downloads": True,
    "has_wiki": True,
    "has_pages": False,
    "has_discussions": False,
    "forks_count": 0,
    "mirror_url": '',
    "archived": False,
    "disabled": False,
    "open_issues_count": 0,
    "license": {
      "key": "mit",
      "name": "MIT License",
      "spdx_id": "MIT",
      "url": "https://api.github.com/licenses/mit",
      "node_id": "MDc6TGljZW5zZTEz"
    },
    "allow_forking": True,
    "is_template": False,
    "web_commit_signoff_required": False,
    "topics": [

    ],
    "visibility": "public",
    "forks": 0,
    "open_issues": 0,
    "watchers": 0,
    "default_branch": "main",
    "stargazers": 0,
    "master_branch": "main",
    "organization": "develeap-green",
    "custom_properties": {

    }
  },
  "pusher": {
    "name": "DanArbiv",
    "email": "107798538+DanArbiv@users.noreply.github.com"
  },
  "organization": {
    "login": "develeap-green",
    "id": 163397731,
    "node_id": "O_kgDOCb1AYw",
    "url": "https://api.github.com/orgs/develeap-green",
    "repos_url": "https://api.github.com/orgs/develeap-green/repos",
    "events_url": "https://api.github.com/orgs/develeap-green/events",
    "hooks_url": "https://api.github.com/orgs/develeap-green/hooks",
    "issues_url": "https://api.github.com/orgs/develeap-green/issues",
    "members_url": "https://api.github.com/orgs/develeap-green/members{/member}",
    "public_members_url": "https://api.github.com/orgs/develeap-green/public_members{/member}",
    "avatar_url": "https://avatars.githubusercontent.com/u/163397731?v=4",
    "description": ''
  },
  "sender": {
    "login": "DanArbiv",
    "id": 107798538,
    "node_id": "U_kgDOBmzgCg",
    "avatar_url": "https://avatars.githubusercontent.com/u/107798538?v=4",
    "gravatar_id": "",
    "url": "https://api.github.com/users/DanArbiv",
    "html_url": "https://github.com/DanArbiv",
    "followers_url": "https://api.github.com/users/DanArbiv/followers",
    "following_url": "https://api.github.com/users/DanArbiv/following{/other_user}",
    "gists_url": "https://api.github.com/users/DanArbiv/gists{/gist_id}",
    "starred_url": "https://api.github.com/users/DanArbiv/starred{/owner}{/repo}",
    "subscriptions_url": "https://api.github.com/users/DanArbiv/subscriptions",
    "organizations_url": "https://api.github.com/users/DanArbiv/orgs",
    "repos_url": "https://api.github.com/users/DanArbiv/repos",
    "events_url": "https://api.github.com/users/DanArbiv/events{/privacy}",
    "received_events_url": "https://api.github.com/users/DanArbiv/received_events",
    "type": "User",
    "site_admin": False
  },
  "created": False,
  "deleted": False,
  "forced": False,
  "base_ref": '',
  "compare": "https://github.com/develeap-green/gan-shmuel/compare/c668f4e1158b...c2901b9c104a",
  "commits": [
    {
      "id": "e01664d5ed4316849b1a252357bf678986cdbab0",
      "tree_id": "d0d5ec5c126e4f552def4718f67ababd0d72ee92",
      "distinct": True,
      "message": "Update",
      "timestamp": "2024-03-17T20:57:00+07:00",
      "url": "https://github.com/develeap-green/gan-shmuel/commit/e01664d5ed4316849b1a252357bf678986cdbab0",
      "author": {
        "name": "DanArbib",
        "email": "arbibdan@gmail.com",
        "username": "DanArbiv"
      },
      "committer": {
        "name": "DanArbib",
        "email": "arbibdan@gmail.com",
        "username": "DanArbiv"
      },
      "added": [
        "docker-compose.dev.yml"
      ],
      "removed": [
        "docker-compose.bill-dev.yml",
        "docker-compose.weight-dev.yml"
      ],
      "modified": [
        "devops/app/routes.py"
      ]
    },
    {
      "id": "bacae0291d09e12066aaa3d958180961b7b38a17",
      "tree_id": "385a60edca91c466fa6e28e515718f92bc8feb0a",
      "distinct": True,
      "message": "Merge branch 'main' of github.com:develeap-green/gan-shmuel",
      "timestamp": "2024-03-17T20:59:48+07:00",
      "url": "https://github.com/develeap-green/gan-shmuel/commit/bacae0291d09e12066aaa3d958180961b7b38a17",
      "author": {
        "name": "DanArbib",
        "email": "arbibdan@gmail.com",
        "username": "DanArbiv"
      },
      "committer": {
        "name": "DanArbib",
        "email": "arbibdan@gmail.com",
        "username": "DanArbiv"
      },
      "added": [
        "billing/.dockerignore",
        "billing/Dockerfile",
        "billing/README_Saturday.txt",
        "billing/app/db_test.py",
        "billing/app/models.py",
        "billing/app/routes.py",
        "billing/app/utils.py",
        "billing/db-init/billingdb.sql",
        "billing/docker-compose.yml",
        "billing/requirements.txt",
        "weight/.flaskenv",
        "weight/CONTRIB.md",
        "weight/Dockerfile",
        "weight/README.md",
        "weight/app/models.py",
        "weight/app/routes.py",
        "weight/compose.yaml",
        "weight/data/containers1.csv",
        "weight/data/containers2.csv",
        "weight/data/spec.md",
        "weight/db/db.sql",
        "weight/requirements.txt"
      ],
      "removed": [
        ".gitignore",
        "weight/weight.py"
      ],
      "modified": [
        "billing/app/__init__.py",
        "billing/billing.py",
        "weight/app/__init__.py"
      ]
    },
    {
      "id": "c10f554845e5638287262fa8319f76f7ed2a1bc7",
      "tree_id": "c37f440102a970bb5f447056308db4838af7b0d8",
      "distinct": True,
      "message": "Update CI flow",
      "timestamp": "2024-03-18T15:08:12+07:00",
      "url": "https://github.com/develeap-green/gan-shmuel/commit/c10f554845e5638287262fa8319f76f7ed2a1bc7",
      "author": {
        "name": "DanArbib",
        "email": "arbibdan@gmail.com",
        "username": "DanArbiv"
      },
      "committer": {
        "name": "DanArbib",
        "email": "arbibdan@gmail.com",
        "username": "DanArbiv"
      },
      "added": [
        ".gitignore",
        "devops/billing.env",
        "devops/weight.env"
      ],
      "removed": [

      ],
      "modified": [
        "devops/app/routes.py",
        "devops/app/utils/utils.py",
        "devops/docker-compose.yml",
        "devops/nginx.conf",
        "devops/requirements.txt",
        "docker-compose.dev.yml",
        "docker-compose.pro.yml"
      ]
    },
    {
      "id": "c2901b9c104a2d5fdef14518de149b8fdf3bd47a",
      "tree_id": "3bafaf4948d611412b7137f8ac6a8566c6b73264",
      "distinct": True,
      "message": "Update CI flow",
      "timestamp": "2024-03-18T15:23:55+07:00",
      "url": "https://github.com/develeap-green/gan-shmuel/commit/c2901b9c104a2d5fdef14518de149b8fdf3bd47a",
      "author": {
        "name": "DanArbib",
        "email": "arbibdan@gmail.com",
        "username": "DanArbiv"
      },
      "committer": {
        "name": "DanArbib",
        "email": "arbibdan@gmail.com",
        "username": "DanArbiv"
      },
      "added": [
        "weight/env.example",
        "weight/weight.py"
      ],
      "removed": [

      ],
      "modified": [
        ".gitignore"
      ]
    }
  ],
  "head_commit": {
    "id": "c2901b9c104a2d5fdef14518de149b8fdf3bd47a",
    "tree_id": "3bafaf4948d611412b7137f8ac6a8566c6b73264",
    "distinct": True,
    "message": "Update CI flow",
    "timestamp": "2024-03-18T15:23:55+07:00",
    "url": "https://github.com/develeap-green/gan-shmuel/commit/c2901b9c104a2d5fdef14518de149b8fdf3bd47a",
    "author": {
      "name": "DanArbib",
      "email": "arbibdan@gmail.com",
      "username": "DanArbiv"
    },
    "committer": {
      "name": "DanArbib",
      "email": "arbibdan@gmail.com",
      "username": "DanArbiv"
    },
    "added": [
      "weight/env.example",
      "weight/weight.py"
    ],
    "removed": [

    ],
    "modified": [
      ".gitignore"
    ]
  }
}







@app.route('/trigger', methods=['GET'])
def trigger():
    # if 'Content-Type' not in request.headers or request.headers['Content-Type'] != 'application/json':
    #     return jsonify({'status': 'error', 'message': 'Invalid Content-Type'}), 400

    # data = request.json
    # logger.info(data)

    # Check branch
    ref = data.get('ref','')
    branch = ref.split('/')[-1]
    if branch != 'main':
        return jsonify({'status': 'success', 'message': 'Skipped push not to main branch.'}), 200
    
    commits = data.get('commits','')
    for commit in commits:
        if commit.get('message') == COMMIT_MESSAGE:
            return jsonify({'status': 'success', 'message': 'Skipped CI push.'}), 200

    
    # Check commits changes by the modified files 
    weight_changed = False
    billing_changed = False
    commits = data.get('commits','')
    for commit in commits:
        added = commit.get('added')
        modified = commit.get('modified')

        for file in added:
            if file.startswith("weight"):
                weight_changed = True

            if file.startswith("billing"):
                billing_changed = True
            
        for file in modified:            
            if file.startswith("weight"):
                weight_changed = True

            if file.startswith("billing"):
                billing_changed = True

    if not weight_changed and not billing_changed:
            return jsonify({'status': 'success', 'message': 'Skipped CI push.'}), 200


    # Run the 'docker images' command to get last version
    process = subprocess.Popen(['docker', 'images'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output, error = process.communicate()

    if process.returncode != 0:
        return jsonify({'error': error.decode()}), 500

    lines = output.decode().split('\n')[1:]
    images_weight = []
    images_billing = []
    for line in lines:
        if line:
            parts = line.split()
            if parts[0] == 'weight-image':
                try:
                    tag = int(parts[1])
                except:
                    tag = 1
                images_weight.append(tag)

            if parts[0] == 'billing-image':
                try:
                    tag = int(parts[1])
                except:
                    tag = 1
                images_billing.append(tag)


    new_ver_weight = max(images_weight) if images_weight else 1
    new_ver_billing = max(images_billing) if images_billing else 1

    # Clone the repository
    logger.info("Pulling git repository.")
    repo_update = subprocess.run(['git', 'pull'])

    if repo_update.returncode != 0:
        logger.error(f"Pull repo process failed.")
        send_email(subject='Deploy Failed', html_page='failed_email.html', stage='Update repo stage')
        return jsonify({'error': 'Clone process failed.'}), 500

    # Check compose file to get last versions
    logger.info("Getting last version from dev compose file.")
    with open('./docker-compose.dev.yml', 'r') as file:
        compose_data = yaml.safe_load(file)

    weight = compose_data['services']['weight']['image']
    weight_default_name = weight.split(':')[0]
    ver_tag_w = int(weight.split(':')[1])

    billing = compose_data['services']['billing']['image']
    billing_deafult_name = billing.split(':')[0]
    ver_tag_b = int(billing.split(':')[1])

    # Build images
    if weight_changed:
        logger.info(f"Starting a build process for weight.")

         # Incresing version 
        weight_tag = f"{weight_default_name}:{new_ver_weight + 1}"

        # Building new image
        weight_build = subprocess.run(["docker", "build", "-t", weight_tag, './weight'])
        if weight_build.returncode != 0:
            logger.error(f"Build process failed - Weight {weight_tag}.")
            send_email(subject='Deploy Failed', html_page='failed_email.html', stage='Build stage weight')
            return jsonify({'error': f"Build process failed - Weight {weight_tag}."}), 500
        
        # Changing compose data to new version
        FILE_COMPOSE_DEV = './docker-compose.dev.yml'
        change_version_w = subprocess.run(["sed", "-i", f"s/{weight_default_name}:{ver_tag_w}/{weight_default_name}:{new_ver_weight + 1}/", FILE_COMPOSE_DEV])

        
    if billing_changed:
        logger.info(f"Starting a build process for billing.")

        # Incresing version 
        billing_tag = f"{billing_deafult_name}:{new_ver_billing + 1}"

        # Building new image
        billing_build = subprocess.run(["docker", "build", "-t", billing_tag, './billing'])
        if billing_build.returncode != 0:
            logger.error(f"Build process failed - Billing {billing_tag}.")
            send_email(subject='Deploy Failed', html_page='failed_email.html', stage='Build stage billing')
            return jsonify({'error': f'Build process failed - Billing {billing_tag}.'}), 500
        
        # Changing compose data to new version
        change_version_b = subprocess.run(["sed", "-i", f"s/{billing_deafult_name}:{ver_tag_b}/{billing_deafult_name}:{new_ver_billing + 1}/", FILE_COMPOSE_DEV])

    # Running testing env
    logger.info(f"Running test environment.")
    run_dev_env = subprocess.run(["docker", "compose", "-f", "docker-compose.dev.yml", "up", "-d"])
    if run_dev_env.returncode != 0:
        logger.error(f"Run testing environment process failed.")
        send_email(subject='Deploy Failed', html_page='failed_email.html', stage='Run testing environment')
        return jsonify({'error': 'Run testing environment process failed.'}), 500

    # # Run testing
    # logger.info(f"Running tests.")
    # # test = subprocess.run([ COMMEND 'exec', 'app', 'pytest'])
    # # if test.returncode != 0:
    # #     logger.error(f"Testing failed.")
    # #     send_email(subject='Deploy Failed', html_page='failed_email.html', stage='Testing stage billing')
    # #     return jsonify({'error': 'Testing failed.'}), 500

    logger.info(f"Tearing down test environment.")
    stop_dev_env = subprocess.run(["docker", "compose", "-f", "docker-compose.dev.yml", "down"])
    if stop_dev_env.returncode != 0:
        logger.error("Failed to stop running containers.")


    # Replace production
    logger.info(f"Replacing production")

    # Replace version
    FILE_COMPOSE_PROD = './docker-compose.pro.yml'
    change_version_w = subprocess.run(["sed", "-i", f"s/{weight_default_name}:{ver_tag_w}/{weight_default_name}:{new_ver_weight + 1}/", FILE_COMPOSE_PROD])
    change_version_b = subprocess.run(["sed", "-i", f"s/{billing_deafult_name}:{ver_tag_b}/{billing_deafult_name}:{new_ver_billing + 1}/", FILE_COMPOSE_PROD])

    replace_production = subprocess.run(["docker", "compose", "-f", "docker-compose.pro.yml", "up", "-d"])
    if replace_production.returncode != 0:
        logger.error(f"Replacing production process failed.")
        send_email(subject='Deploy Failed', html_page='failed_email.html', stage='Replacing production')
        return jsonify({'error': 'Replacing production process failed.'}), 500


    # send_email(subject='Deploy succeeded', html_page='success_email.html', stage='')
    return jsonify({'status': 'success', 'message': 'Deployment successful'}), 200



if __name__ == '__main__':
    app.run(port=5000, debug=False)