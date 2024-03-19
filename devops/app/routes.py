from flask import request, jsonify, render_template
from app import app, logger, REPO_URL, REPO_NAME
from app.utils.utils import delete_repo, send_email, copy_env
import subprocess
import os
import yaml
import requests
import shutil

COMMIT_MESSAGE = 'CI-commit'
URL_WEIGHT = 'http://greenteam.hopto.org:8081/health'
URL_BILLING = 'http://greenteam.hopto.org:8082/health'



# # Check compose file to get last versions
# logger.info("Getting last version from dev compose file.")
# with open('/home/ubuntu/project/gan-shmuel/docker-compose.pro.yml', 'r') as file:
#     compose_data = yaml.safe_load(file)

# weight = compose_data['services']['weight']['image']
# weight_default_name = weight.split(':')[0]
# version_weight = int(weight.split(':')[1])

# billing = compose_data['services']['billing']['image']
# billing_deafult_name = billing.split(':')[0]
# version_billing = int(billing.split(':')[1])

# logger.info(f"Starting a build process for weight.")

# # Incresing version 
# weight_tag = f"{weight_default_name}:{version_weight + 1}"

# # Building new image
# weight_build = subprocess.run(["docker", "build", "-t", weight_tag, '/home/ubuntu/project/gan-shmuel/weight'])

# # Changing compose data to new version
# compose_data['services']['weight']['image'] = weight_tag


# logger.info(f"Starting a build process for billing.")

# # Incresing version 
# billing_tag = f"{billing_deafult_name}:{version_billing + 1}"

# # Building new image
# billing_build = subprocess.run(["docker", "build", "-t", billing_tag, '/home/ubuntu/project/gan-shmuel/billing'])

# # Changing compose data to new version
# compose_data['services']['billing']['image'] = billing_tag

# # Updating docker compose file with the new versions
# with open('./docker-compose.pro.yml', 'w') as file:
#     yaml.dump(compose_data, file)

# run_production = subprocess.run(["docker", "compose", "-f", "/home/ubuntu/project/gan-shmuel/docker-compose.pro.yml", "up", "-d"])



# Copy env files to folder the repo folder
# devops_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
# logger.info(devops_dir)
# destination_folder = os.path.join(devops_dir, REPO_NAME)
# copy_env(devops_dir, destination_folder)



# Clone the repository
if not os.path.exists(REPO_NAME):
    logger.info("Cloning git repository.")
    repo_update = subprocess.run(['git', 'clone', REPO_URL], check=True)
    os.chdir(REPO_NAME)
else:
    logger.info("Pulling git repository.")
    os.chdir(REPO_NAME)
    repo_update = subprocess.run(['git', 'pull'])

if repo_update.returncode != 0:
    logger.error(f"Clone process failed.")

# Check compose file to get last versions
logger.info("Getting last version from dev compose file.")
with open('./docker-compose.dev.yml', 'r') as file:
    compose_data = yaml.safe_load(file)

weight = compose_data['services']['weight']['image']
weight_default_name = weight.split(':')[0]
version_weight = int(weight.split(':')[1])

billing = compose_data['services']['billing']['image']
billing_deafult_name = billing.split(':')[0]
version_billing = int(billing.split(':')[1])

logger.info(f"Starting a build process for weight.")

# Incresing version 
weight_tag = f"{weight_default_name}:{version_weight + 1}"

# Building new image
weight_build = subprocess.run(["docker", "build", "-t", weight_tag, './weight'])
if weight_build.returncode != 0:
    logger.error(f"Build process failed - Weight {weight_tag}.")

# Changing compose data to new version
compose_data['services']['weight']['image'] = weight_tag

    
logger.info(f"Starting a build process for billing.")

# Incresing version 
billing_tag = f"{billing_deafult_name}:{version_billing + 1}"

# Building new image
billing_build = subprocess.run(["docker", "build", "-t", billing_tag, './billing'])
if billing_build.returncode != 0:
    logger.error(f"Build process failed - Billing {billing_tag}.")


# Changing compose data to new version
compose_data['services']['billing']['image'] = billing_tag

# Updating docker compose file with the new versions
with open('./docker-compose.dev.yml', 'w') as file:
    yaml.dump(compose_data, file)


# Running testing env
logger.info(f"Running test environment.")
run_dev_env = subprocess.run(["docker", "compose", "-f", "docker-compose.dev.yml", "up", "-d"])
if run_dev_env.returncode != 0:
    logger.error(f"Run testing environment process failed.")

# # Run testing
# logger.info(f"Running tests.")
# # test = subprocess.run([ COMMEND 'exec', 'app', 'pytest'])
# # if test.returncode != 0:
# #     logger.error(f"Testing failed.")
# #     send_email(subject='Deploy Failed', html_page='failed_email.html', stage='Testing stage billing')
# #     return jsonify({'error': 'Testing failed.'}), 500

# logger.info(f"Tearing down test environment.")
# stop_dev_env = subprocess.run(["docker", "compose", "-f", "docker-compose.dev.yml", "down"])
# if stop_dev_env.returncode != 0:
#     logger.error("Failed to stop running containers.")


# # Replace production
# logger.info(f"Replacing production")

# # Replace version
# with open('docker-compose.pro.yml', 'r') as file:
#     compose_pro_data = yaml.safe_load(file)

# compose_pro_data['services']['weight']['image'] = weight_tag

# compose_pro_data['services']['billing']['image'] = billing_tag

# with open('docker-compose.pro.yml', 'w') as file:
#     yaml.dump(compose_pro_data, file, sort_keys=False)


# replace_production = subprocess.run(["docker", "compose", "-f", "docker-compose.pro.yml", "up", "-d"])
# if replace_production.returncode != 0:
#     logger.error(f"Replacing production process failed.")
#     send_email(subject='Deploy Failed', html_page='failed_email.html', stage='Replacing production')
#     return jsonify({'error': 'Replacing production process failed.'}), 500






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
    response = requests.get(URL_WEIGHT)
    if response.status_code == 200:
        weight_status = True

    billing_status = False
    response = requests.get(URL_BILLING)
    if response.status_code == 200:
        billing_status = True

    data = {
        'weight_status': billing_status,
        'billing_status': weight_status 
    }

    return render_template('monitor.html', data=data, images_weight=images_weight, images_billing=images_billing)
    

@app.route('/api/v1/rollback', methods=['POST'])
def rollback():
    try:

        weight_tag = request.form.get('weight_tag')
        billing_tag = request.form.get('billing_tag')

        if not weight_tag and not billing_tag:
            return jsonify({'message': 'Keeping current version.'}), 200


        # Replace production
        logger.info(f"Replacing production")
        with open('docker-compose.rollback.yml', 'r') as file:
            compose_pro_data = yaml.safe_load(file)

        if weight_tag:
            compose_pro_data['services']['weight']['image'] = weight_tag
        
        if billing_tag:
            compose_pro_data['services']['billing']['image'] = billing_tag
        
        with open('docker-compose.rollback.yml', 'w') as file:
            yaml.dump(compose_pro_data, file, sort_keys=False)


        replace_production = subprocess.run(["docker", "compose", "-f", "docker-compose.rollback.yml", "up", "-d"])
        if replace_production.returncode != 0:
            logger.error(f"Replacing production process failed.")
            send_email(subject='Deploy Failed', html_page='failed_email.html', stage='Replacing production')
            return jsonify({'error': 'Replacing production process failed.'}), 500

        # Update git with the new version
        subprocess.run(["git", "add", "."])
        subprocess.run(["git", "commit", "-m", f"{COMMIT_MESSAGE}"])
        subprocess.run(["git", "push", "origin", "main"])

        send_email(subject='Rollback succeeded', html_page='success_email.html', stage='')
        return jsonify({'message': 'Rollback initiated successfully.'}), 200

    except Exception as e:
        logger.error(f"Faild to rollback.")
        return jsonify({'error': str(e)}), 500


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

        new_tag_weight = max(images_weight) if images_weight else 1
        new_tag_billing = max(images_billing) if images_billing else 1

        # Clone the repository
        if not os.path.exists(REPO_NAME):
            logger.info("Cloning git repository.")
            repo_update = subprocess.run(['git', 'clone', REPO_URL], check=True)
            os.chdir(REPO_NAME)
        else:
            logger.info("Pulling git repository.")
            os.chdir(REPO_NAME)
            repo_update = subprocess.run(['git', 'pull'])

        if repo_update.returncode != 0:
            logger.error(f"Clone process failed.")
            send_email(subject='Deploy Failed', html_page='failed_email.html', stage='Update repo stage')
            return jsonify({'error': 'Clone process failed.'}), 500

        # Check compose file to get last versions
        logger.info("Getting last version from dev compose file.")
        with open('./docker-compose.dev.yml', 'r') as file:
            compose_data = yaml.safe_load(file)

        weight = compose_data['services']['weight']['image']
        weight_default_name = weight.split(':')[0]

        billing = compose_data['services']['billing']['image']
        billing_deafult_name = billing.split(':')[0]

        # Build images
        if weight_changed:
            logger.info(f"Starting a build process for weight.")

             # Incresing version 
            weight_tag = f"{weight_default_name}:{new_tag_weight}"

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
            billing_tag = f"{billing_deafult_name}:{new_tag_billing}"

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


        replace_production = subprocess.run(["docker", "compose", "-f", "docker-compose.pro.yml", "up", "-d"])
        if replace_production.returncode != 0:
            logger.error(f"Replacing production process failed.")
            send_email(subject='Deploy Failed', html_page='failed_email.html', stage='Replacing production')
            return jsonify({'error': 'Replacing production process failed.'}), 500


        send_email(subject='Deploy succeeded', html_page='success_email.html', stage='')
        return jsonify({'status': 'success', 'message': 'Deployment successful'}), 200
