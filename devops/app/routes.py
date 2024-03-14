from flask import request, jsonify, render_template
from app import app, logger
import subprocess
import shutil
import json
import os

REPO_URL = os.environ.get('REPO_URL')
REPO_NAME = REPO_URL.split('/')[-1].split('.git')[0]

def del_repo():
    if os.path.exists(os.path.join(os.getcwd(), REPO_NAME)):
        shutil.rmtree(REPO_NAME)


@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')


@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'success', 'message': 'Ok'}), 200


@app.route('/trigger', methods=['POST'])
def trigger():
    if request.headers['Content-Type'] == 'application/json':
        data = json.dumps(request.json)
        logger.info(data)

        # Clone the repository
        logger.info(f"Cloning git repository.")
        del_repo()
        clone = subprocess.run(['git', 'clone', REPO_URL])

        if clone.returncode != 0:
            logger.error(f"Clone process failed.")
            del_repo()
            return jsonify({'error': 'Clone process failed.'}), 500

        # Change dir
        os.chdir(REPO_URL.split('/')[-1].split('.git')[0])

        # Run tests
        logger.info(f"Running tests.")
        

        # Build
        logger.info(f"Starting the build process.")


        # Running
        logger.info(f"Starting the container.")


        # del_repo()
        return jsonify({'status': 'success', 'message': 'Deployment successful'}), 200



@app.route('/test', methods=['GET'])
def test():

    # Clone the repository
    logger.info(f"Cloning git repository.")
    del_repo()
    clone = subprocess.run(['git', 'clone', REPO_URL])

    if clone.returncode != 0:
        logger.error(f"Clone process failed.")
        del_repo()
        return jsonify({'error': 'Clone process failed.'}), 500

    # Change dir
    os.chdir(REPO_NAME)

    # Run tests
    logger.info(f"Running tests.")
    

    # Build
    logger.info(f"Starting the build process.")


    # Running
    logger.info(f"Starting the container.")


    # del_repo()
    return jsonify({'status': 'success', 'message': 'Deployment successful'}), 200






