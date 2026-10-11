// Declarative CI/CD pipeline for the Hotel Room Booking Portal.
//
//   Checkout -> Build -> Unit tests -> E2E tests -> Package -> Deploy
//
// Every step is a shell command. If any command fails (for example pytest
// reports a failing test, so it exits with a non-zero code) its stage fails
// and the pipeline stops: a broken build is never packaged or deployed.
//
// Agent requirements: python3.11, Chromium + chromedriver, Docker CLI with
// compose plugin (all provided by deploy/jenkins/Dockerfile).
// Credential required: Secret text with ID "hotel-secret-key".

pipeline {
    agent any

    parameters {
        // The parameterised environment setting.
        choice(name: 'APP_ENV', choices: ['staging', 'prod'],
               description: 'Where to deploy. Sets APP_ENV in the container and the port: staging = 8081, prod = 8082.')
    }

    triggers {
        // CI: check the repository for new commits about every 5 minutes.
        pollSCM('H/5 * * * *')
    }

    options {
        timestamps()
        buildDiscarder(logRotator(numToKeepStr: '15'))
        disableConcurrentBuilds()        // two deploys at once would fight over the same containers
        timeout(time: 30, unit: 'MINUTES')
    }

    environment {
        PYTHON    = 'python3.11'         // same Python version as the production image
        IMAGE_TAG = "${env.BUILD_NUMBER}" // every build produces uniquely tagged images
        HOST_PORT = "${params.APP_ENV == 'prod' ? '8082' : '8081'}"
        // Separate compose project per environment = separate containers and
        // separate database volume for staging and prod.
        COMPOSE_PROJECT_NAME = "hotel-${params.APP_ENV}"
        // APP_ENV itself is exported automatically because it is a parameter.
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
                sh 'git log -1 --pretty="Building commit %h: %s"'
            }
        }

        stage('Build') {
            steps {
                sh '''
                    $PYTHON --version
                    $PYTHON -m venv .venv
                    .venv/bin/pip install --quiet --upgrade pip
                    .venv/bin/pip install --quiet -r requirements-dev.txt
                    # Byte-compile all code: catches syntax errors before testing.
                    .venv/bin/python -m compileall -q app wsgi.py
                '''
            }
        }

        stage('Unit tests') {
            steps {
                sh '.venv/bin/pytest -m "not e2e" --junitxml=reports/unit-tests.xml'
            }
        }

        stage('E2E tests') {
            steps {
                // Starts the app on a free port and drives headless Chromium.
                // Screenshots of failures land in reports/screenshots/.
                sh '.venv/bin/pytest -m e2e --junitxml=reports/e2e-tests.xml'
            }
        }

        stage('Package') {
            steps {
                // The deployable artefacts are two Docker images tagged with the build number.
                sh '''
                    docker build -t hotel-booking-app:$IMAGE_TAG .
                    docker build -f deploy/nginx/Dockerfile -t hotel-booking-nginx:$IMAGE_TAG .
                '''
            }
        }

        stage('Deploy') {
            steps {
                // The secret is injected only for this block and masked in the log.
                withCredentials([string(credentialsId: 'hotel-secret-key', variable: 'SECRET_KEY')]) {
                    // --wait: block until containers are running and healthy,
                    // and fail the stage if they do not become healthy.
                    sh 'docker compose up -d --no-build --wait --wait-timeout 120'
                    // Smoke test through the whole chain: nginx -> gunicorn -> SQLite.
                    sh 'docker compose exec -T nginx wget -qO- http://127.0.0.1/health'
                }
            }
        }
    }

    post {
        always {
            // Publish test results (Jenkins shows pass/fail trends) and keep
            // the reports + any failure screenshots with the build.
            junit allowEmptyResults: true, testResults: 'reports/*.xml'
            archiveArtifacts artifacts: 'reports/**', allowEmptyArchive: true
        }
        success {
            echo "Build ${env.BUILD_NUMBER} deployed to ${params.APP_ENV}: http://localhost:${env.HOST_PORT}"
        }
        failure {
            echo 'Pipeline FAILED - see the red stage above and the Test Results page.'
        }
    }
}
