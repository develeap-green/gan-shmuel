from flask import request, jsonify, render_template
from app import app, logger, REPO_URL, REPO_NAME
from app.utils.utils import delete_repo, send_email
import subprocess
import json
import os

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')


@app.route('/health', methods=['GET'])
def health():
    #### ADD HEALTH CHECK TO BILLING AND WEIGHT SERVICES
    return jsonify({'status': 'success', 'message': 'Ok'}), 200


@app.route('/trigger', methods=['POST'])
def trigger():
    if request.headers['Content-Type'] == 'application/json':
        data = json.dumps(request.json)
        logger.info(data)

        # Clone the repository
        if not os.path.exists(REPO_NAME):
            logger.info("Cloning git repository.")
            repo_update = subprocess.run(['git', 'clone', REPO_URL], check=True)
        else:
            logger.info("Pulling git repository.")
            repo_update = subprocess.run(['git', 'pull'], check=True)

        if repo_update.returncode != 0:
            logger.error(f"Clone process failed.")
            send_email(subject='Deploy Failed', html_page='failed_email.html', stage='Update repo stage')
            return jsonify({'error': 'Clone process failed.'}), 500

        # Change dir
        os.chdir(REPO_NAME)

        ##################
        ##### WEIGHT #####
        ##################
        # Build environment
        logger.info(f"Starting the build process.")
        build = subprocess.run(['docker compose', '-f', 'docker-compose.weight-dev.yml', 'build'])
        if build.returncode != 0:
            logger.error(f"Build process failed.")
            send_email(subject='Deploy Failed', html_page='failed_email.html', stage='Build stage weight')
            return jsonify({'error': 'Build process failed.'}), 500

        # Up environment
        logger.info(f"Running dev environment.")
        up_env = subprocess.run(['docker compose', '-f', 'docker-compose.weight-dev.yml', 'up'])
        if up_env.returncode != 0:
            logger.error(f"Up process failed.")
            send_email(subject='Deploy Failed', html_page='failed_email.html', stage='Run stage weight')
            return jsonify({'error': 'Run process failed.'}), 500

        # Run testing
        logger.info(f"Running tests.")
        test = subprocess.run(['docker compose', '-f', 'docker-compose.weight-dev.yml', 'exec', 'app', 'pytest'])
        if test.returncode != 0:
            logger.error(f"Testing failed.")
            send_email(subject='Deploy Failed', html_page='failed_email.html', stage='Testing stage weight')
            return jsonify({'error': 'Testing failed.'}), 500
        
        ###################
        ##### BILLING #####
        ###################
        # Build environment
        logger.info(f"Starting the build process.")
        build = subprocess.run(['docker compose', '-f', 'docker-compose.bill-dev.yml', 'build'])
        if build.returncode != 0:
            logger.error(f"Build process failed.")
            send_email(subject='Deploy Failed', html_page='failed_email.html', stage='Build stage billing')
            return jsonify({'error': 'Build process failed.'}), 500

        # Up environment
        logger.info(f"Running dev environment.")
        up_env = subprocess.run(['docker compose', '-f', 'docker-compose.bill-dev.yml', 'up'])
        if up_env.returncode != 0:
            logger.error(f"Up process failed.")
            send_email(subject='Deploy Failed', html_page='failed_email.html', stage='Run stage billing')
            return jsonify({'error': 'Run process failed.'}), 500

        # Run testing
        logger.info(f"Running tests.")
        test = subprocess.run(['docker compose', '-f', 'docker-compose.bill-dev.yml', 'exec', 'app', 'pytest'])
        if test.returncode != 0:
            logger.error(f"Testing failed.")
            send_email(subject='Deploy Failed', html_page='failed_email.html', stage='Testing stage billing')
            return jsonify({'error': 'Testing failed.'}), 500


        # Replace production
        logger.info(f"Replace production")
        up = subprocess.run(['docker compose', '-f', 'docker-compose.pro.yml', 'up'])
        if up.returncode != 0:
            logger.error(f"Up process failed.")
            send_email(subject='Deploy Failed', html_page='failed_email.html', stage='Replace production')
            return jsonify({'error': 'Replace production failed.'}), 500

        send_email(subject='Deploy succeeded', html_page='success_email.html', stage='')
        return jsonify({'status': 'success', 'message': 'Deployment successful'}), 200







@app.route('/test-email', methods=['GET'])
def email():
    send_email(subject='Deploy succeeded', html_page='success_email.html', stage='')
    return jsonify({'status': 'success', 'message': 'Deployment successful'}), 200