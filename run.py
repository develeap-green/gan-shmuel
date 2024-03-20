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
FILE_COMPOSE_DEV = './docker-compose.dev.yml'
FILE_COMPOSE_PROD = './docker-compose.pro.yml'
BILLING_IMAGE = 'billing-image'
WEIGHT_IMAGE = 'weight-image'


def delete_repo():
    try:
        if os.path.exists(os.path.join(os.getcwd(), REPO_NAME)):
            logger.info(f"Deleting repo folder.")
            shutil.rmtree(REPO_NAME)
            logger.info(f"Repo folder successful deleted.")
    except:
        pass


def send_email(subject, html_page, stage, emails):
    try:
        recipients = ' '.join([email.split('@')[0] for email in emails])
        html_body = render_template(html_page, recipients=recipients, stage=stage)
        msg = Message(subject, recipients=emails, html=html_body)
        mail.send(msg)
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

    # Run the docker images command
    process = subprocess.Popen(['docker', 'images'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output, error = process.communicate()

    if process.returncode != 0:
        return jsonify({'error': error.decode()}), 500
    

    # Extract all the last versions of billing and weight
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


    # Check health routes
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
        'weight_status': weight_status,
        'billing_status': billing_status 
    }

    return render_template('monitor.html', data=data, images_weight=images_weight, images_billing=images_billing)
    

@app.route('/api/v1/rollback', methods=['POST'])
def rollback():
    try:

        # Get values from submit form
        weight_tag = request.form.get('weight_tag')
        billing_tag = request.form.get('billing_tag')

        if not weight_tag and not billing_tag:
            return jsonify({'message': 'Keeping current version.'}), 200


        # Check compose prod file to get last versions (to replace it with the new one)
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

        # Change versions in file with sed cmd
        subprocess.run(["sed", "-i", f"s/{weight_default_name}:{ver_tag_w}/{weight_tag}/", FILE_COMPOSE_PROD])
        subprocess.run(["sed", "-i", f"s/{billing_deafult_name}:{ver_tag_b}/{billing_tag}/", FILE_COMPOSE_PROD])

        # Run prod compose with updated version
        replace_production = subprocess.run(["docker", "compose", "-f", "docker-compose.pro.yml", "up", "-d"])
        if replace_production.returncode != 0:
            logger.error(f"Replacing production process failed.")
            send_email(subject='Deploy Failed', html_page='failed_email.html', stage='Replacing production' ,emails=EMAILS)
            return jsonify({'error': 'Replacing production process failed.'}), 500


        send_email(subject='Rollback succeeded', html_page='success_email.html', stage='' ,emails=EMAILS)
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

    # Check if commit is in branch main
    ref = data.get('ref','')
    branch = ref.split('/')[-1]
    if branch != 'main':
        return jsonify({'status': 'success', 'message': 'Skipped push not to main branch.'}), 200
    
    # Check if the commit was created by the CI to stop loop
    commits = data.get('commits','')
    for commit in commits:
        if commit.get('message') == COMMIT_MESSAGE:
            return jsonify({'status': 'success', 'message': 'Skipped CI push.'}), 200

    
    # Check which branch commited the change and get emails
    emails = []
    weight_changed = False
    billing_changed = False
    for commit in commits:
        added = commit.get('added')
        modified = commit.get('modified')
        author = commit.get('author')
        email = author.get('email')
        emails.append(email)

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

    # Add the commiter mail to the dev emails list
    emails.extend(EMAILS)

    if not weight_changed and not billing_changed:
            return jsonify({'status': 'success', 'message': 'Skipped CI push.'}), 200


    # Run the docker images command to get last versions
    process = subprocess.Popen(['docker', 'images'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output, error = process.communicate()

    if process.returncode != 0:
        return jsonify({'error': error.decode()}), 500

    # Extract all the last versions of billing and weight
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

    # Find the last version by number
    new_ver_weight = max(images_weight) if images_weight else 1
    new_ver_billing = max(images_billing) if images_billing else 1

    # Pull from repository
    logger.info("Pulling git repository.")
    subprocess.run(['git', 'reset', '--hard', 'HEAD'])
    subprocess.run(['git', 'pull'])

    # Check compose file to get last versions (to find and replace with sed)
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
        logger.info(f"Weight changed, Starting a build process for weight.")

         # Incresing version 
        weight_tag = f"{WEIGHT_IMAGE}:{new_ver_weight + 1}"

        # Building new image
        weight_build = subprocess.run(["docker", "build", '--no-cache', "-t", weight_tag, './weight'])
        if weight_build.returncode != 0:
            logger.error(f"Build process failed - Weight {weight_tag}.")
            send_email(subject='Deploy Failed', html_page='failed_email.html', stage='Build stage weight',emails=emails)
            return jsonify({'error': f"Build process failed - Weight {weight_tag}."}), 500
        
        # Changing the compose file version to new version with sed cmd
        subprocess.run(["sed", "-i", f"s/{WEIGHT_IMAGE}:{ver_tag_w}/{WEIGHT_IMAGE}:{new_ver_weight + 1}/", FILE_COMPOSE_DEV])


    if billing_changed:
        logger.info(f"Billing changed, Starting a build process for billing.")

        # Incresing version 
        billing_tag = f"{BILLING_IMAGE}:{new_ver_billing + 1}"

        # Building new image
        billing_build = subprocess.run(["docker", "build", '--no-cache', "-t", billing_tag, './billing'])
        if billing_build.returncode != 0:
            logger.error(f"Build process failed - Billing {billing_tag}.")
            send_email(subject='Deploy Failed', html_page='failed_email.html', stage='Build stage billing',emails=emails)
            return jsonify({'error': f'Build process failed - Billing {billing_tag}.'}), 500
        
        # Changing compose data to new version
        subprocess.run(["sed", "-i", f"s/{BILLING_IMAGE}:{ver_tag_b}/{BILLING_IMAGE}:{new_ver_billing + 1}/", FILE_COMPOSE_DEV])

    # Running testing environment
    logger.info(f"Running test environment.")
    run_dev_env = subprocess.run(["docker", "compose", "-p", "testing", "-f", "docker-compose.dev.yml", "up", "-d"])
    if run_dev_env.returncode != 0:
        logger.error(f"Run testing environment process failed.")
        send_email(subject='Deploy Failed', html_page='failed_email.html', stage='Run testing environment',emails=emails)
        return jsonify({'error': 'Run testing environment process failed.'}), 500

    # # Run testing
    # logger.info(f"Running tests.")
    # test = subprocess.run([ 'COMMEND' 'exec', 'app', 'pytest'])
    # if test.returncode != 0:
    #     logger.error(f"Testing failed.")
    #     send_email(subject='Deploy Failed', html_page='failed_email.html', stage='Testing stage billing', emails=emails)
    #     return jsonify({'error': 'Testing failed.'}), 500

    logger.info(f"Tearing down test environment.")
    stop_dev_env = subprocess.run(["docker", "compose", "-p", "testing", "-f", "docker-compose.dev.yml", "down"])
    if stop_dev_env.returncode != 0:
        logger.error("Failed to stop running containers.")

    logger.info(f"Removing unused test volumes.")
    subprocess.run(["docker", "volume", "rm", "testing_billing_database", "testing_weight_database"])


    # Replace production
    logger.info(f"Replacing production")

    # Replace version
    logger.info(f"s/{WEIGHT_IMAGE}:{ver_tag_w}/{WEIGHT_IMAGE}:{new_ver_weight + 1}/")
    logger.info(f"s/{BILLING_IMAGE}:{ver_tag_b}/{BILLING_IMAGE}:{new_ver_billing + 1}/")
    subprocess.run(["sed", "-i", f"s/{WEIGHT_IMAGE}:{ver_tag_w}/{WEIGHT_IMAGE}:{new_ver_weight + 1}/", FILE_COMPOSE_PROD])
    subprocess.run(["sed", "-i", f"s/{BILLING_IMAGE}:{ver_tag_b}/{BILLING_IMAGE}:{new_ver_billing + 1}/", FILE_COMPOSE_PROD])

    # Run production with the new version
    replace_production = subprocess.run(["docker", "compose", "-f", "docker-compose.pro.yml", "up", "-d"])
    if replace_production.returncode != 0:
        logger.error(f"Replacing production process failed.")
        send_email(subject='Deploy Failed', html_page='failed_email.html', stage='Replacing production',emails=emails)
        return jsonify({'error': 'Replacing production process failed.'}), 500


    # send_email(subject='Deploy succeeded', html_page='success_email.html', stage='', emails=emails)
    return jsonify({'status': 'success', 'message': 'Deployment successful'}), 200



if __name__ == '__main__':
    app.run(port=5000, debug=False)