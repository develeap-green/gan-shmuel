from flask import request, jsonify, render_template
from app import app, logger, REPO_URL, REPO_NAME
from app.utils.utils import delete_repo, send_email, copy_env
import subprocess
import os
import yaml


@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')


@app.route('/health', methods=['GET'])
def health():
    #### ADD HEALTH CHECK TO BILLING AND WEIGHT SERVICES
    return jsonify({'status': 'success', 'message': 'Ok'}), 200


@app.route('/monitor', methods=['GET'])
def monitor():
    return render_template('index.html')
    

@app.route('/trigger', methods=['POST'])
def trigger():
        if 'Content-Type' not in request.headers or request.headers['Content-Type'] != 'application/json':
            return jsonify({'status': 'error', 'message': 'Invalid Content-Type'}), 400

        data = request.json
        logger.info(data)

        # Check branch
        ref = data.get('ref','')
        branch = ref.split('/')[-1]
        if branch != 'main':
            return jsonify({'status': 'success', 'message': 'Skipped push not to main branch.'}), 200
        
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

    
        # Clone the repository
        logger.info("Cloning git repository.")

        # Clone the repository
        if not os.path.exists(REPO_NAME):
            logger.info("Cloning git repository.")
            repo_update = subprocess.run(['git', 'clone', REPO_URL], check=True)
            os.chdir(REPO_NAME)
        else:
            logger.info("Pulling git repository.")
            os.chdir(REPO_NAME)
            repo_update = subprocess.run(['git', 'pull'], check=True)

        if repo_update.returncode != 0:
            logger.error(f"Clone process failed.")
            send_email(subject='Deploy Failed', html_page='failed_email.html', stage='Update repo stage')
            return jsonify({'error': 'Clone process failed.'}), 500

        # Check compose file to get last versions
        logger.info("Getting last version from dev compose file.")
        with open('./docker-compose.dev.yml', 'r') as file:
            compose_data = yaml.safe_load(file)

        weight = compose_data['services']['weight']['image']
        weight_version = int(weight.split(':')[-1])
        weight_default_name = weight.split(':')[0]

        billing = compose_data['services']['billing']['image']
        billing_version = int(billing.split(':')[-1])
        billing_deafult_name = billing.split(':')[0]

        # Build images
        if weight_changed:
            logger.info(f"Starting a build process for weight.")

             # Incresing version 
            weight_tag = f"{weight_default_name}:{weight_version+1}"

            # Building new image
            weight_build = subprocess.run(["docker", "build", "-t", weight_tag, './weight'])
            if weight_build.returncode != 0:
                logger.error(f"Build process failed - Weight {weight_tag}.")
                send_email(subject='Deploy Failed', html_page='failed_email.html', stage='Build stage weight')
                return jsonify({'error': f"Build process failed - Weight {weight_tag}."}), 500
            
            # Changing compose data to new version
            compose_data['services']['weight']['image'] = weight_tag

            
        if billing_changed:
            logger.info(f"Starting a build process for billing.")

            # Incresing version 
            billing_tag = f"{billing_deafult_name}:{billing_version+1}"

            # Building new image
            billing_build = subprocess.run(["docker", "build", "-t", billing_tag, './billing'])
            if billing_build.returncode != 0:
                logger.error(f"Build process failed - Billing {billing_tag}.")
                send_email(subject='Deploy Failed', html_page='failed_email.html', stage='Build stage billing')
                return jsonify({'error': f'Build process failed - Billing {billing_tag}.'}), 500
            
            # Changing compose data to new version
            compose_data['services']['billing']['image'] = billing_tag

        # Updating docker compose file with the new versions
        with open('./docker-compose.dev.yml', 'w') as file:
            yaml.dump(compose_data, file)


        # Copy env files to folder the repo folder
        devops_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
        destination_folder = os.path.join(devops_dir, REPO_NAME)
        copy_env(devops_dir, destination_folder)


        # Running testing env
        logger.info(f"Running test environment.")
        run_dev_env = subprocess.run(["docker", "compose", "-f", "docker-compose.dev.yml", "up", "-d"])
        if run_dev_env.returncode != 0:
            logger.error(f"Run testing environment process failed.")
            send_email(subject='Deploy Failed', html_page='failed_email.html', stage='Run testing environment')
            return jsonify({'error': 'Run testing environment process failed.'}), 500

        # Run testing
        logger.info(f"Running tests.")
        # test = subprocess.run([ COMMEND 'exec', 'app', 'pytest'])
        # if test.returncode != 0:
        #     logger.error(f"Testing failed.")
        #     send_email(subject='Deploy Failed', html_page='failed_email.html', stage='Testing stage billing')
        #     return jsonify({'error': 'Testing failed.'}), 500

        logger.info(f"Tearing down test environment.")
        stop_dev_env = subprocess.run(["docker", "compose", "-f", "docker-compose.dev.yml", "down"])
        if stop_dev_env.returncode != 0:
            logger.error("Failed to stop running containers.")


        # Replace production
        logger.info(f"Replacing production")

        # Replace version
        with open('docker-compose.pro.yml', 'r') as file:
            compose_pro_data = yaml.safe_load(file)

        if weight_changed:
            compose_pro_data['services']['weight']['image'] = weight_tag
        
        if billing_changed:
            compose_pro_data['services']['billing']['image'] = billing_tag
        
        with open('docker-compose.pro.yml', 'w') as file:
            yaml.dump(compose_pro_data, file, sort_keys=False)


        # Stop nginx
        logger.info(f"Stop nginx!")
        replace_production = subprocess.run(["docker", "stop", "devops-nginx-1"])

        replace_production = subprocess.run(["docker", "compose", "-f", "docker-compose.pro.yml", "up", "-d"])
        if replace_production.returncode != 0:
            logger.error(f"Replacing production process failed.")
            send_email(subject='Deploy Failed', html_page='failed_email.html', stage='Replacing production')
            return jsonify({'error': 'Replacing production process failed.'}), 500

        # # Update git with the new version
        # subprocess.run(["git", "add", "."])
        # subprocess.run(["git", "commit", "-m", f"Update"])
        # subprocess.run(["git", "push", "origin", "main"])

        send_email(subject='Deploy succeeded', html_page='success_email.html', stage='')
        return jsonify({'status': 'success', 'message': 'Deployment successful'}), 200
































@app.route('/test-email', methods=['GET'])
def email():
    send_email(subject='Deploy succeeded', html_page='success_email.html', stage='')
    return jsonify({'status': 'success', 'message': 'Deployment successful'}), 200

@app.route('/test', methods=['GET'])
def test():

        data = {"ref": "refs/heads/main", "before": "93e310bcff40aed29896a8c34f2551d1a080db6a", "after": "95770bcddb5e2d93a80fd2ba03fae99e9f849a1f", "repository": {"id": 771988013, "node_id": "R_kgDOLgOaLQ", "name": "gan-shmuel", "full_name": "develeap-green/gan-shmuel", "private": False, "owner": {"name": "develeap-green", "email": '', "login": "develeap-green", "id": 163397731, "node_id": "O_kgDOCb1AYw", "avatar_url": "https://avatars.githubusercontent.com/u/163397731?v=4", "gravatar_id": "", "url": "https://api.github.com/users/develeap-green", "html_url": "https://github.com/develeap-green", "followers_url": "https://api.github.com/users/develeap-green/followers", "following_url": "https://api.github.com/users/develeap-green/following{/other_user}", "gists_url": "https://api.github.com/users/develeap-green/gists{/gist_id}", "starred_url": "https://api.github.com/users/develeap-green/starred{/owner}{/repo}", "subscriptions_url": "https://api.github.com/users/develeap-green/subscriptions", "organizations_url": "https://api.github.com/users/develeap-green/orgs", "repos_url": "https://api.github.com/users/develeap-green/repos", "events_url": "https://api.github.com/users/develeap-green/events{/privacy}", "received_events_url": "https://api.github.com/users/develeap-green/received_events", "type": "Organization", "site_admin": False}, "html_url": "https://github.com/develeap-green/gan-shmuel", "description": '', "fork": False, "url": "https://github.com/develeap-green/gan-shmuel", "forks_url": "https://api.github.com/repos/develeap-green/gan-shmuel/forks", "keys_url": "https://api.github.com/repos/develeap-green/gan-shmuel/keys{/key_id}", "collaborators_url": "https://api.github.com/repos/develeap-green/gan-shmuel/collaborators{/collaborator}", "teams_url": "https://api.github.com/repos/develeap-green/gan-shmuel/teams", "hooks_url": "https://api.github.com/repos/develeap-green/gan-shmuel/hooks", "issue_events_url": "https://api.github.com/repos/develeap-green/gan-shmuel/issues/events{/number}", "events_url": "https://api.github.com/repos/develeap-green/gan-shmuel/events", "assignees_url": "https://api.github.com/repos/develeap-green/gan-shmuel/assignees{/user}", "branches_url": "https://api.github.com/repos/develeap-green/gan-shmuel/branches{/branch}", "tags_url": "https://api.github.com/repos/develeap-green/gan-shmuel/tags", "blobs_url": "https://api.github.com/repos/develeap-green/gan-shmuel/git/blobs{/sha}", "git_tags_url": "https://api.github.com/repos/develeap-green/gan-shmuel/git/tags{/sha}", "git_refs_url": "https://api.github.com/repos/develeap-green/gan-shmuel/git/refs{/sha}", "trees_url": "https://api.github.com/repos/develeap-green/gan-shmuel/git/trees{/sha}", "statuses_url": "https://api.github.com/repos/develeap-green/gan-shmuel/statuses/{sha}", "languages_url": "https://api.github.com/repos/develeap-green/gan-shmuel/languages", "stargazers_url": "https://api.github.com/repos/develeap-green/gan-shmuel/stargazers", "contributors_url": "https://api.github.com/repos/develeap-green/gan-shmuel/contributors", "subscribers_url": "https://api.github.com/repos/develeap-green/gan-shmuel/subscribers", "subscription_url": "https://api.github.com/repos/develeap-green/gan-shmuel/subscription", "commits_url": "https://api.github.com/repos/develeap-green/gan-shmuel/commits{/sha}", "git_commits_url": "https://api.github.com/repos/develeap-green/gan-shmuel/git/commits{/sha}", "comments_url": "https://api.github.com/repos/develeap-green/gan-shmuel/comments{/number}", "issue_comment_url": "https://api.github.com/repos/develeap-green/gan-shmuel/issues/comments{/number}", "contents_url": "https://api.github.com/repos/develeap-green/gan-shmuel/contents/{+path}", "compare_url": "https://api.github.com/repos/develeap-green/gan-shmuel/compare/{base}...{head}", "merges_url": "https://api.github.com/repos/develeap-green/gan-shmuel/merges", "archive_url": "https://api.github.com/repos/develeap-green/gan-shmuel/{archive_format}{/ref}", "downloads_url": "https://api.github.com/repos/develeap-green/gan-shmuel/downloads", "issues_url": "https://api.github.com/repos/develeap-green/gan-shmuel/issues{/number}", "pulls_url": "https://api.github.com/repos/develeap-green/gan-shmuel/pulls{/number}", "milestones_url": "https://api.github.com/repos/develeap-green/gan-shmuel/milestones{/number}", "notifications_url": "https://api.github.com/repos/develeap-green/gan-shmuel/notifications{?since,all,participating}", "labels_url": "https://api.github.com/repos/develeap-green/gan-shmuel/labels{/name}", "releases_url": "https://api.github.com/repos/develeap-green/gan-shmuel/releases{/id}", "deployments_url": "https://api.github.com/repos/develeap-green/gan-shmuel/deployments", "created_at": 1710411626, "updated_at": "2024-03-17T12:56:07Z", "pushed_at": 1710684521, "git_url": "git://github.com/develeap-green/gan-shmuel.git", "ssh_url": "git@github.com:develeap-green/gan-shmuel.git", "clone_url": "https://github.com/develeap-green/gan-shmuel.git", "svn_url": "https://github.com/develeap-green/gan-shmuel", "homepage": '', "size": 84, "stargazers_count": 0, "watchers_count": 0, "language": "Python", "has_issues": True, "has_projects": True, "has_downloads": True, "has_wiki": True, "has_pages": False, "has_discussions": False, "forks_count": 0, "mirror_url": '', "archived": False, "disabled": False, "open_issues_count": 0, "license": {"key": "mit", "name": "MIT License", "spdx_id": "MIT", "url": "https://api.github.com/licenses/mit", "node_id": "MDc6TGljZW5zZTEz"}, "allow_forking": True, "is_template": False, "web_commit_signoff_required": False, "topics": [], "visibility": "public", "forks": 0, "open_issues": 0, "watchers": 0, "default_branch": "main", "stargazers": 0, "master_branch": "main", "organization": "develeap-green", "custom_properties": {}}, "pusher": {"name": "danirdd92", "email": "danirdd92@gmail.com"}, "organization": {"login": "develeap-green", "id": 163397731, "node_id": "O_kgDOCb1AYw", "url": "https://api.github.com/orgs/develeap-green", "repos_url": "https://api.github.com/orgs/develeap-green/repos", "events_url": "https://api.github.com/orgs/develeap-green/events", "hooks_url": "https://api.github.com/orgs/develeap-green/hooks", "issues_url": "https://api.github.com/orgs/develeap-green/issues", "members_url": "https://api.github.com/orgs/develeap-green/members{/member}", "public_members_url": "https://api.github.com/orgs/develeap-green/public_members{/member}", "avatar_url": "https://avatars.githubusercontent.com/u/163397731?v=4", "description": ''}, "sender": {"login": "danirdd92", "id": 15320627, "node_id": "MDQ6VXNlcjE1MzIwNjI3", "avatar_url": "https://avatars.githubusercontent.com/u/15320627?v=4", "gravatar_id": "", "url": "https://api.github.com/users/danirdd92", "html_url": "https://github.com/danirdd92", "followers_url": "https://api.github.com/users/danirdd92/followers", "following_url": "https://api.github.com/users/danirdd92/following{/other_user}", "gists_url": "https://api.github.com/users/danirdd92/gists{/gist_id}", "starred_url": "https://api.github.com/users/danirdd92/starred{/owner}{/repo}", "subscriptions_url": "https://api.github.com/users/danirdd92/subscriptions", "organizations_url": "https://api.github.com/users/danirdd92/orgs", "repos_url": "https://api.github.com/users/danirdd92/repos", "events_url": "https://api.github.com/users/danirdd92/events{/privacy}", "received_events_url": "https://api.github.com/users/danirdd92/received_events", "type": "User", "site_admin": False}, "created": False, "deleted": False, "forced": False, "base_ref": "refs/heads/main", "compare": "https://github.com/develeap-green/gan-shmuel/compare/93e310bcff40...95770bcddb5e", "commits": [{"id": "e486fd8a2a50375c1fdb12efdd13de541e83ff53", "tree_id": "f77c31d4942af8212a003ea8cd9f1ba05d2f5062", "distinct": False, "message": "Initial commit", "timestamp": "2024-03-14T14:17:15+02:00", "url": "https://github.com/develeap-green/gan-shmuel/commit/e486fd8a2a50375c1fdb12efdd13de541e83ff53", "author": {"name": "root", "email": "11roeyw55"}, "committer": {"name": "root", "email": "11roeyw55"}, "added": ["billing/app/models.py", "billing/app/routes.py", "billing/requirements.txt", "billing/weight.py", "weight/.env.example"], "removed": [], "modified": ["billing/app/__init__.py", "billing/billing.py", "weight/weight.py"]}, {"id": "b6337e8d5a0e95cfe5e283ef59bc6e368afb3c8a", "tree_id": "dc5ff7e2c767ff878fa472aab842f36e25714274", "distinct": False, "message": "Initial commit", "timestamp": "2024-03-14T21:31:16+07:00", "url": "https://github.com/develeap-green/gan-shmuel/commit/b6337e8d5a0e95cfe5e283ef59bc6e368afb3c8a", "author": {"name": "DanArbib", "email": "arbibdan@gmail.com", "username": "DanArbiv"}, "committer": {"name": "DanArbib", "email": "arbibdan@gmail.com", "username": "DanArbiv"}, "added": ["devops/Dockerfile.api", "devops/app/__init__.py", "devops/app/routes.py", "devops/app/templates/index.html", "devops/docker-compose.yml", "devops/env.example", "devops/nginx.conf", "devops/requirements.txt", "devops/run.py"], "removed": [], "modified": [".gitignore"]}, {"id": "64d632f54d4dd1706d131955164bbf8f0ef4a243", "tree_id": "26a50334d5f89e0094e784cbc4cba9112080a677", "distinct": False, "message": "adding function to update provider nameto routes.py", "timestamp": "2024-03-14T16:32:28+02:00", "url": "https://github.com/develeap-green/gan-shmuel/commit/64d632f54d4dd1706d131955164bbf8f0ef4a243", "author": {"name": "NaorHadad", "email": "naor.hadad@outlook.com", "username": "NaorHadad"}, "committer": {"name": "NaorHadad", "email": "naor.hadad@outlook.com", "username": "NaorHadad"}, "added": [], "removed": [], "modified": ["billing/app/routes.py"]}, {"id": "5b1599b9a6966167dc2bb19ee68cbd0be923fabf", "tree_id": "ab4d7886bf56285a82af0f2631001b1262b06e83", "distinct": False, "message": "Health check v1", "timestamp": "2024-03-14T17:22:25+02:00", "url": "https://github.com/develeap-green/gan-shmuel/commit/5b1599b9a6966167dc2bb19ee68cbd0be923fabf", "author": {"name": "alone", "email": "alon90620@gmail.com", "username": "alon-efrati"}, "committer": {"name": "alone", "email": "alon90620@gmail.com", "username": "alon-efrati"}, "added": [], "removed": [], "modified": ["billing/app/routes.py"]}, {"id": "85f792401d6b53ead41d47728f16d7ba7b00b598", "tree_id": "8f2de264857965a8d73a6942076ff03ce8e94f8a", "distinct": False, "message": "Fix nginx", "timestamp": "2024-03-14T22:23:23+07:00", "url": "https://github.com/develeap-green/gan-shmuel/commit/85f792401d6b53ead41d47728f16d7ba7b00b598", "author": {"name": "DanArbib", "email": "arbibdan@gmail.com", "username": "DanArbiv"}, "committer": {"name": "DanArbib", "email": "arbibdan@gmail.com", "username": "DanArbiv"}, "added": [], "removed": [], "modified": ["devops/app/__init__.py", "devops/nginx.conf"]}, {"id": "29f9505430cb313f9f9f7107aa00e288b74776fd", "tree_id": "e2c8b3c9582df5fbe9a9957b3439163a1d92f1fe", "distinct": False, "message": "cleaning import line and adding comments to\n routes.py", "timestamp": "2024-03-14T17:38:24+02:00", "url": "https://github.com/develeap-green/gan-shmuel/commit/29f9505430cb313f9f9f7107aa00e288b74776fd", "author": {"name": "NaorHadad", "email": "naor.hadad@outlook.com", "username": "NaorHadad"}, "committer": {"name": "NaorHadad", "email": "naor.hadad@outlook.com", "username": "NaorHadad"}, "added": ["billing/app/__pycache__/routes.cpython-310.pyc"], "removed": [], "modified": ["billing/app/routes.py"]}, {"id": "1bd9c5658ab7ea8a01a8f25e3abc8c026baffb6f", "tree_id": "65df569573bd1a90e2085deb3f5ca086ca8bba8c", "distinct": False, "message": "Fix nginx", "timestamp": "2024-03-14T22:43:53+07:00", "url": "https://github.com/develeap-green/gan-shmuel/commit/1bd9c5658ab7ea8a01a8f25e3abc8c026baffb6f", "author": {"name": "DanArbib", "email": "arbibdan@gmail.com", "username": "DanArbiv"}, "committer": {"name": "DanArbib", "email": "arbibdan@gmail.com", "username": "DanArbiv"}, "added": [], "removed": [], "modified": ["devops/nginx.conf"]}, {"id": "2ccecaeb802e6b28a89803b58c232481ea4ad270", "tree_id": "3b18dec0a375f72c4e310dcb0bde20b75fc85ae9", "distinct": False, "message": "Fix nginx", "timestamp": "2024-03-14T22:50:58+07:00", "url": "https://github.com/develeap-green/gan-shmuel/commit/2ccecaeb802e6b28a89803b58c232481ea4ad270", "author": {"name": "DanArbib", "email": "arbibdan@gmail.com", "username": "DanArbiv"}, "committer": {"name": "DanArbib", "email": "arbibdan@gmail.com", "username": "DanArbiv"}, "added": [], "removed": [], "modified": ["devops/docker-compose.yml"]}, {"id": "2b1241843273f6805060b0ce9ae7b882292c6a78", "tree_id": "f317b77daa8afab28a17ca11479e25bffba67c4f", "distinct": False, "message": "Fix nginx", "timestamp": "2024-03-14T22:55:59+07:00", "url": "https://github.com/develeap-green/gan-shmuel/commit/2b1241843273f6805060b0ce9ae7b882292c6a78", "author": {"name": "DanArbib", "email": "arbibdan@gmail.com", "username": "DanArbiv"}, "committer": {"name": "DanArbib", "email": "arbibdan@gmail.com", "username": "DanArbiv"}, "added": [], "removed": [], "modified": ["devops/docker-compose.yml"]}, {"id": "ae8c4939c2038a8ee39c44fe7cf49e5050198fca", "tree_id": "81a7a5b06ba9b92e324ff2efdc5705fb77c466e6", "distinct": False, "message": "Project Structure Cleanup", "timestamp": "2024-03-14T18:37:05+02:00", "url": "https://github.com/develeap-green/gan-shmuel/commit/ae8c4939c2038a8ee39c44fe7cf49e5050198fca", "author": {"name": "root", "email": "11roeyw55"}, "committer": {"name": "root", "email": "11roeyw55"}, "added": [], "removed": [], "modified": ["billing/app/__init__.py", "billing/app/models.py", "billing/app/routes.py", "billing/billing.py", "billing/requirements.txt"]}, {"id": "73573e144a98ab158aba9595bb5b247f0aa0b52f", "tree_id": "73e56374881b1697fb044564f86b61cbe23acfe0", "distinct": False, "message": "changed the libry of db to  from flask_sqlalchemy import SQLAlchemy", "timestamp": "2024-03-14T19:00:00+02:00", "url": "https://github.com/develeap-green/gan-shmuel/commit/73573e144a98ab158aba9595bb5b247f0aa0b52f", "author": {"name": "NaorHadad", "email": "naor.hadad@outlook.com", "username": "NaorHadad"}, "committer": {"name": "NaorHadad", "email": "naor.hadad@outlook.com", "username": "NaorHadad"}, "added": [], "removed": [], "modified": ["billing/app/routes.py"]}, {"id": "d09f655c6f14bfca54462b16b962e84c87d270c8", "tree_id": "89c0fd6f69e6bf9f968d46fe7ac70d4627e4ccf4", "distinct": False, "message": "Updated .gitignore\n\nadded pycache", "timestamp": "2024-03-14T19:10:39+02:00", "url": "https://github.com/develeap-green/gan-shmuel/commit/d09f655c6f14bfca54462b16b962e84c87d270c8", "author": {"name": "ShahafSegg", "email": "162299649+ShahafSegg@users.noreply.github.com", "username": "ShahafSegg"}, "committer": {"name": "GitHub", "email": "noreply@github.com", "username": "web-flow"}, "added": [], "removed": [], "modified": [".gitignore"]}, {"id": "b0d0a3e6108059981478946048fe415bfd142697", "tree_id": "827ff180d22f154b4a072aafb20144b7eb2517da", "distinct": False, "message": "changed fro msql to sqlAlchemy", "timestamp": "2024-03-14T19:40:24+02:00", "url": "https://github.com/develeap-green/gan-shmuel/commit/b0d0a3e6108059981478946048fe415bfd142697", "author": {"name": "NaorHadad", "email": "naor.hadad@outlook.com", "username": "NaorHadad"}, "committer": {"name": "NaorHadad", "email": "naor.hadad@outlook.com", "username": "NaorHadad"}, "added": ["billing/app/__pycache__/routes.cpython-310.pyc"], "removed": [], "modified": [".gitignore", "billing/app/__init__.py", "billing/app/models.py", "billing/app/routes.py", "billing/billing.py", "billing/requirements.txt"]}, {"id": "35e1241832b11e8e8b40c2f45d3b912f49c7250c", "tree_id": "8225485122e30377f230e0c385c9a6329fc0b4a0", "distinct": False, "message": "changed fro msql to sqlAlchemy", "timestamp": "2024-03-14T19:54:01+02:00", "url": "https://github.com/develeap-green/gan-shmuel/commit/35e1241832b11e8e8b40c2f45d3b912f49c7250c", "author": {"name": "NaorHadad", "email": "naor.hadad@outlook.com", "username": "NaorHadad"}, "committer": {"name": "NaorHadad", "email": "naor.hadad@outlook.com", "username": "NaorHadad"}, "added": [], "removed": [], "modified": ["billing/app/routes.py"]}, {"id": "f8c6cfaa2b18feeca3316ab7c912661f50fd208e", "tree_id": "bd68b8761f240e00af663044a3ae5b6562a31ff7", "distinct": False, "message": "add health include json v2", "timestamp": "2024-03-14T21:48:02+02:00", "url": "https://github.com/develeap-green/gan-shmuel/commit/f8c6cfaa2b18feeca3316ab7c912661f50fd208e", "author": {"name": "alone", "email": "alon90620@gmail.com", "username": "alon-efrati"}, "committer": {"name": "alone", "email": "alon90620@gmail.com", "username": "alon-efrati"}, "added": [], "removed": [], "modified": ["billing/app/routes.py"]}, {"id": "8f54bec3b37bff026ff4948d6e7aca03d7cc53fe", "tree_id": "631fd232bcd9789c3d8612b39235cc160ebc0fce", "distinct": False, "message": "Added dockerfile, compose and db", "timestamp": "2024-03-15T10:09:11+02:00", "url": "https://github.com/develeap-green/gan-shmuel/commit/8f54bec3b37bff026ff4948d6e7aca03d7cc53fe", "author": {"name": "root", "email": "11roeyw55"}, "committer": {"name": "root", "email": "11roeyw55"}, "added": ["billing/.dockerignore", "billing/Dockerfile", "billing/db-init/billingdb.sql", "billing/docker-compose.yml"], "removed": ["billing/app/__pycache__/routes.cpython-310.pyc", "billing/weight.py"], "modified": ["billing/app/__init__.py", "billing/requirements.txt"]}, {"id": "d1d69ed6ff8b21bd913e0c967e9fd1a7b81552d9", "tree_id": "d7f590dd2c5d7f16a0b06c4fe693415befa17640", "distinct": False, "message": "Added readme for new stuff, DB & App containers work", "timestamp": "2024-03-15T12:17:40+02:00", "url": "https://github.com/develeap-green/gan-shmuel/commit/d1d69ed6ff8b21bd913e0c967e9fd1a7b81552d9", "author": {"name": "Roeyw", "email": "roey.wullman@gmail.com", "username": "roeyw5"}, "committer": {"name": "Roeyw", "email": "roey.wullman@gmail.com", "username": "roeyw5"}, "added": ["billing/README_Friday.txt"], "removed": [], "modified": ["billing/app/__init__.py", "billing/app/routes.py", "billing/billing.py", "billing/requirements.txt"]}, {"id": "720d6a0d8366591aa82d80632b00858b6520f840", "tree_id": "272f23263dec569c2143f35d758093426287b174", "distinct": False, "message": "Containers health-check working, need more work on the DB functions", "timestamp": "2024-03-15T15:53:15+02:00", "url": "https://github.com/develeap-green/gan-shmuel/commit/720d6a0d8366591aa82d80632b00858b6520f840", "author": {"name": "Roeyw", "email": "roey.wullman@gmail.com", "username": "roeyw5"}, "committer": {"name": "Roeyw", "email": "roey.wullman@gmail.com", "username": "roeyw5"}, "added": ["billing/app/health.py"], "removed": [], "modified": ["billing/app/__init__.py", "billing/app/models.py", "billing/app/routes.py", "billing/billing.py", "billing/docker-compose.yml"]}, {"id": "6eb0ff34209d024a326167fbe4a3036d5a57aaf7", "tree_id": "3efd54ae5cd192feca4526c851e1fb62d87dbbd3", "distinct": False, "message": "Added POST /providr function. Removed duplicate environment variable in docker-compose.yml", "timestamp": "2024-03-16T17:17:54+02:00", "url": "https://github.com/develeap-green/gan-shmuel/commit/6eb0ff34209d024a326167fbe4a3036d5a57aaf7", "author": {"name": "Zori", "email": "zoril.devops@gmail.com", "username": "ZoriLDevOps"}, "committer": {"name": "Zori", "email": "zoril.devops@gmail.com", "username": "ZoriLDevOps"}, "added": [], "removed": [], "modified": ["billing/app/routes.py", "billing/docker-compose.yml"]}, {"id": "3179c0357d4d14611ccb9bc4b2bb0ad86189aeea", "tree_id": "b9e01029bf8bb8faccc9f41bbb9cf52698345303", "distinct": False, "message": "Established DB connection in Flask app, refined overall functionality, added utils.py", "timestamp": "2024-03-17T00:10:35+02:00", "url": "https://github.com/develeap-green/gan-shmuel/commit/3179c0357d4d14611ccb9bc4b2bb0ad86189aeea", "author": {"name": "Roeyw", "email": "roey.wullman@gmail.com", "username": "roeyw5"}, "committer": {"name": "Roeyw", "email": "roey.wullman@gmail.com", "username": "roeyw5"}, "added": ["billing/README_Saturday.txt", "billing/app/db_test.py", "billing/app/utils.py"], "removed": ["billing/README_Friday.txt", "billing/app/health.py"], "modified": ["billing/app/__init__.py", "billing/app/models.py", "billing/app/routes.py", "billing/db-init/billingdb.sql"]}, {"id": "0ec44f27d421a6d5605646815374e76e98aed2cb", "tree_id": "fc60570c97eeed5a36c613daec15e6fe5615c7f0", "distinct": False, "message": "Added empty/whitespace string check for createProvider.", "timestamp": "2024-03-17T01:12:30+02:00", "url": "https://github.com/develeap-green/gan-shmuel/commit/0ec44f27d421a6d5605646815374e76e98aed2cb", "author": {"name": "Zori", "email": "zoril.devops@gmail.com", "username": "ZoriLDevOps"}, "committer": {"name": "Zori", "email": "zoril.devops@gmail.com", "username": "ZoriLDevOps"}, "added": [], "removed": [], "modified": ["billing/app/routes.py"]}, {"id": "30d36ed7b1e0791a05db7c4c55f58ef312f7e84b", "tree_id": "04e410eb6637ebc1402fcec17196adb64f111bcd", "distinct": False, "message": "added Post truck function v_1", "timestamp": "2024-03-17T11:31:20+02:00", "url": "https://github.com/develeap-green/gan-shmuel/commit/30d36ed7b1e0791a05db7c4c55f58ef312f7e84b", "author": {"name": "NaorHadad", "email": "naor.hadad@outlook.com", "username": "NaorHadad"}, "committer": {"name": "NaorHadad", "email": "naor.hadad@outlook.com", "username": "NaorHadad"}, "added": [], "removed": [], "modified": ["billing/app/routes.py"]}, {"id": "74a75222c39d013a2f05193e520caf7043b86159", "tree_id": "fa5bdee347b042631a8d9eb37e2c052759aa134b", "distinct": False, "message": "Update CI and mail notification", "timestamp": "2024-03-17T16:37:47+07:00", "url": "https://github.com/develeap-green/gan-shmuel/commit/74a75222c39d013a2f05193e520caf7043b86159", "author": {"name": "DanArbib", "email": "arbibdan@gmail.com", "username": "DanArbiv"}, "committer": {"name": "DanArbib", "email": "arbibdan@gmail.com", "username": "DanArbiv"}, "added": ["devops/app/templates/failed_email.html", "devops/app/templates/success_email.html", "devops/app/utils/utils.py"], "removed": [], "modified": ["devops/Dockerfile.api", "devops/app/__init__.py", "devops/app/routes.py", "devops/app/templates/index.html", "devops/docker-compose.yml", "devops/env.example", "devops/requirements.txt"]}, {"id": "441649d9036ae1f108d2a59bd96a02941ea26b10", "tree_id": "43b89d42ba0685748f44cc019e3fe2a8fddefa8f", "distinct": False, "message": "added Post truck function v_2", "timestamp": "2024-03-17T11:52:59+02:00", "url": "https://github.com/develeap-green/gan-shmuel/commit/441649d9036ae1f108d2a59bd96a02941ea26b10", "author": {"name": "NaorHadad", "email": "naor.hadad@outlook.com", "username": "NaorHadad"}, "committer": {"name": "NaorHadad", "email": "naor.hadad@outlook.com", "username": "NaorHadad"}, "added": [], "removed": [], "modified": ["billing/app/routes.py"]}, {"id": "aac42a85386201560eb3aed4f1f5b278c3dc2ae4", "tree_id": "43f11c2ccabfab1114e8fd8a935e46642774873f", "distinct": False, "message": "Update CI and mail notification", "timestamp": "2024-03-17T16:57:10+07:00", "url": "https://github.com/develeap-green/gan-shmuel/commit/aac42a85386201560eb3aed4f1f5b278c3dc2ae4", "author": {"name": "DanArbib", "email": "arbibdan@gmail.com", "username": "DanArbiv"}, "committer": {"name": "DanArbib", "email": "arbibdan@gmail.com", "username": "DanArbiv"}, "added": [], "removed": [], "modified": ["devops/app/__init__.py", "devops/app/routes.py"]}, {"id": "bfe933ecef9f9cff5408e48aa225584f7a860dbb", "tree_id": "567b5a198e9929c3f357b2d8e8fda328af9b8c27", "distinct": False, "message": "added Post truck function v_3", "timestamp": "2024-03-17T12:15:22+02:00", "url": "https://github.com/develeap-green/gan-shmuel/commit/bfe933ecef9f9cff5408e48aa225584f7a860dbb", "author": {"name": "NaorHadad", "email": "naor.hadad@outlook.com", "username": "NaorHadad"}, "committer": {"name": "NaorHadad", "email": "naor.hadad@outlook.com", "username": "NaorHadad"}, "added": [], "removed": [], "modified": ["billing/app/routes.py"]}, {"id": "34c09f32266afbed77448c58a97bbd584e3f61bb", "tree_id": "e288604b616cedb3000dd93fac1ba04574e14338", "distinct": False, "message": "added Post truck function v_4", "timestamp": "2024-03-17T12:21:11+02:00", "url": "https://github.com/develeap-green/gan-shmuel/commit/34c09f32266afbed77448c58a97bbd584e3f61bb", "author": {"name": "NaorHadad", "email": "naor.hadad@outlook.com", "username": "NaorHadad"}, "committer": {"name": "NaorHadad", "email": "naor.hadad@outlook.com", "username": "NaorHadad"}, "added": [], "removed": [], "modified": ["billing/app/routes.py"]}, {"id": "cbbbef98922087996b7a4c28ef466e457ec1c731", "tree_id": "65b208ccd37ad159c9743569d1049630c3cda662", "distinct": False, "message": "added Post truck function v_5", "timestamp": "2024-03-17T12:37:35+02:00", "url": "https://github.com/develeap-green/gan-shmuel/commit/cbbbef98922087996b7a4c28ef466e457ec1c731", "author": {"name": "NaorHadad", "email": "naor.hadad@outlook.com", "username": "NaorHadad"}, "committer": {"name": "NaorHadad", "email": "naor.hadad@outlook.com", "username": "NaorHadad"}, "added": [], "removed": [], "modified": ["billing/app/routes.py"]}, {"id": "9ee777c39c55f930ebeff8ee8e38e3024d10ef88", "tree_id": "c385715a5135830c9bd5cc2fa087f414e7073f22", "distinct": False, "message": "added PUT truck function and updated the provider id in the truck table", "timestamp": "2024-03-17T13:58:39+02:00", "url": "https://github.com/develeap-green/gan-shmuel/commit/9ee777c39c55f930ebeff8ee8e38e3024d10ef88", "author": {"name": "NaorHadad", "email": "naor.hadad@outlook.com", "username": "NaorHadad"}, "committer": {"name": "NaorHadad", "email": "naor.hadad@outlook.com", "username": "NaorHadad"}, "added": [], "removed": [], "modified": ["billing/app/routes.py", "billing/db-init/billingdb.sql"]}, {"id": "cea6c8c48f8b1960395af693f6511f54fc188907", "tree_id": "b8b2062dd5a2f6bc8ba06be907f2a16394a60038", "distinct": False, "message": "Update compose", "timestamp": "2024-03-17T19:55:56+07:00", "url": "https://github.com/develeap-green/gan-shmuel/commit/cea6c8c48f8b1960395af693f6511f54fc188907", "author": {"name": "DanArbib", "email": "arbibdan@gmail.com", "username": "DanArbiv"}, "committer": {"name": "DanArbib", "email": "arbibdan@gmail.com", "username": "DanArbiv"}, "added": ["docker-compose.bill-dev.yml", "docker-compose.pro.yml", "docker-compose.weight-dev.yml"], "removed": [], "modified": ["devops/app/routes.py"]}, {"id": "c9ee42c397abeafd0c5b6163e01436ddff695b1c", "tree_id": "9bad2eca484871a9e19150667af5e434f10a23f6", "distinct": False, "message": "Merge branch 'weight-main'", "timestamp": "2024-03-17T15:16:24+02:00", "url": "https://github.com/develeap-green/gan-shmuel/commit/c9ee42c397abeafd0c5b6163e01436ddff695b1c", "author": {"name": "Daniel Rashba", "email": "danirdd92@gmail.com", "username": "danirdd92"}, "committer": {"name": "Daniel Rashba", "email": "danirdd92@gmail.com", "username": "danirdd92"}, "added": ["weight/.env.example", "weight/.flaskenv", "weight/CONTRIB.md", "weight/Dockerfile", "weight/README.md", "weight/app/models.py", "weight/app/routes.py", "weight/compose.yaml", "weight/data/containers1.csv", "weight/data/containers2.csv", "weight/data/spec.md", "weight/db/db.sql", "weight/requirements.txt"], "removed": [], "modified": [".gitignore", "weight/app/__init__.py", "weight/weight.py"]}, {"id": "0e8bfd7cb7d59a93d3ed252f37b8a3759f01ab68", "tree_id": "f7489d981eb1099785a9ecd22cb7d8834908b5f6", "distinct": False, "message": "Merge branch 'main' into billing-main", "timestamp": "2024-03-17T15:43:28+02:00", "url": "https://github.com/develeap-green/gan-shmuel/commit/0e8bfd7cb7d59a93d3ed252f37b8a3759f01ab68", "author": {"name": "Roeyw", "email": "roey.wullman@gmail.com", "username": "roeyw5"}, "committer": {"name": "Roeyw", "email": "roey.wullman@gmail.com", "username": "roeyw5"}, "added": ["devops/Dockerfile.api", "devops/app/__init__.py", "devops/app/routes.py", "devops/app/templates/failed_email.html", "devops/app/templates/index.html", "devops/app/templates/success_email.html", "devops/app/utils/utils.py", "devops/docker-compose.yml", "devops/env.example", "devops/nginx.conf", "devops/requirements.txt", "devops/run.py", "docker-compose.bill-dev.yml", "docker-compose.pro.yml", "docker-compose.weight-dev.yml", "weight/.flaskenv", "weight/CONTRIB.md", "weight/Dockerfile", "weight/README.md", "weight/app/models.py", "weight/app/routes.py", "weight/compose.yaml", "weight/data/containers1.csv", "weight/data/containers2.csv", "weight/data/spec.md", "weight/db/db.sql", "weight/requirements.txt"], "removed": [".gitignore", "weight/.env.example", "weight/weight.py"], "modified": ["weight/app/__init__.py"]}, {"id": "95770bcddb5e2d93a80fd2ba03fae99e9f849a1f", "tree_id": "3c7488c5b821034eb73ceb7cb5a9dcf63c750da9", "distinct": False, "message": "Fix everything Shahaf fucked up", "timestamp": "2024-03-17T16:03:30+02:00", "url": "https://github.com/develeap-green/gan-shmuel/commit/95770bcddb5e2d93a80fd2ba03fae99e9f849a1f", "author": {"name": "Roeyw", "email": "roey.wullman@gmail.com", "username": "roeyw5"}, "committer": {"name": "Roeyw", "email": "roey.wullman@gmail.com", "username": "roeyw5"}, "added": ["gitignore.txt", "weight/env.example", "weight/weight.py"], "removed": [], "modified": []}], "head_commit": {"id": "95770bcddb5e2d93a80fd2ba03fae99e9f849a1f", "tree_id": "3c7488c5b821034eb73ceb7cb5a9dcf63c750da9", "distinct": False, "message": "Fix everything Shahaf fucked up", "timestamp": "2024-03-17T16:03:30+02:00", "url": "https://github.com/develeap-green/gan-shmuel/commit/95770bcddb5e2d93a80fd2ba03fae99e9f849a1f", "author": {"name": "Roeyw", "email": "roey.wullman@gmail.com", "username": "roeyw5"}, "committer": {"name": "Roeyw", "email": "roey.wullman@gmail.com", "username": "roeyw5"}, "added": ["gitignore.txt", "weight/env.example", "weight/weight.py"], "removed": [], "modified": []}}

        # Check branch
        ref = data.get('ref','')
        branch = ref.split('/')[-1]
        if branch != 'main':
            return jsonify({'status': 'success', 'message': 'Skipped push not to main branch.'}), 200
        
        
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

        
                
        # # Clone the repository
        # delete_repo()
        # logger.info("Cloning git repository.")
        # repo_update = subprocess.run(['git', 'clone', REPO_URL], check=True)

        # if repo_update.returncode != 0:
        #     logger.error(f"Clone process failed.")
        #     send_email(subject='Deploy Failed', html_page='failed_email.html', stage='Update repo stage')
        #     return jsonify({'error': 'Clone process failed.'}), 500

        # Change dir
        os.chdir(REPO_NAME)

        # Check compose file to get last versions
        with open('./docker-compose.bill-dev.yml', 'r') as file:
            compose_data = yaml.safe_load(file)

        weight = compose_data['services']['weight']['image']
        weight_version = int(weight.split(':')[-1])
        weight_default_name = weight.split(':')[0]

        billing = compose_data['services']['billing']['image']
        billing_version = int(billing.split(':')[-1])
        billing_deafult_name = billing.split(':')[0]

        # Build images
        if weight_changed:
            logger.info(f"Starting a build process for weight.")

             # Incresing version 
            weight_tag = f"{weight_default_name}:{weight_version+1}"

            # Building new image
            weight_build = subprocess.run(["docker", "build", "-t", weight_tag, './weight'])
            if weight_build.returncode != 0:
                logger.error(f"Build process failed - Weight {weight_tag}.")
                send_email(subject='Deploy Failed', html_page='failed_email.html', stage='Build stage weight')
                return jsonify({'error': f"Build process failed - Weight {weight_tag}."}), 500
            
            # Changing compose data to new version
            compose_data['services']['weight']['image'] = weight_tag

            
        if billing_changed:
            logger.info(f"Starting a build process for billing.")

            # Incresing version 
            billing_tag = f"{billing_deafult_name}:{billing_version+1}"

            # Building new image
            billing_build = subprocess.run(["docker", "build", "-t", billing_tag, './billing'])
            if billing_build.returncode != 0:
                logger.error(f"Build process failed - Billing {billing_tag}.")
                send_email(subject='Deploy Failed', html_page='failed_email.html', stage='Build stage billing')
                return jsonify({'error': f'Build process failed - Billing {billing_tag}.'}), 500
            
            # Changing compose data to new version
            compose_data['services']['billing']['image'] = billing_tag

        # Updating docker compose file with the new versions
        with open('./docker-compose.bill-dev.yml', 'w') as file:
            yaml.dump(compose_data, file)


        # Copy env files to folder the repo folder
        devops_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
        destination_folder = os.path.join(devops_dir, REPO_NAME)
        copy_env(devops_dir, destination_folder)


        # Running testing env
        run_dev_env = subprocess.run(["docker", "compose", "-f", "./docker-compose.bill-dev.yml", "up"])
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


        # Replace production
        logger.info(f"Replacing production")

        # # Replace version
        # with open('./docker-compose.pro.yml', 'r') as file:
        #     compose_pro_data = yaml.safe_load(file)

        # if weight_changed:
        #     compose_pro_data['services']['weight']['image'] = weight_tag
        
        # if billing_changed:
        #     compose_pro_data['services']['billing']['image'] = billing_tag
        
        # with open('docker-compose.dev.yml', 'w') as file:
        #     yaml.dump(compose_pro_data, file)


        # replace_production = subprocess.run(["docker-compose", "-f", "docker-compose.pro.yml", "up"])
        # if replace_production.returncode != 0:
        #     logger.error(f"Replacing production process failed.")
        #     send_email(subject='Deploy Failed', html_page='failed_email.html', stage='Replacing production')
        #     return jsonify({'error': 'Replacing production process failed.'}), 500


        # # Update git with the new version
        # # Git add
        # subprocess.run(["git", "add", "."])

        # # Git commit
        # subprocess.run(["git", "commit", "-m", f"Update"])

        # # Git push
        # subprocess.run(["git", "push", "origin", "main"])

        # send_email(subject='Deploy succeeded', html_page='success_email.html', stage='')
        return jsonify({'status': 'success', 'message': 'Deployment successful'}), 200