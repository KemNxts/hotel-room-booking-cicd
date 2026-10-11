// Declarative CI/CD pipeline for the Hotel Room Booking Portal.
//
//   Checkout -> Install -> Static checks -> Unit & integration tests -> E2E tests
//            -> Package source -> Build images -> Publish images -> Deploy -> Health check
//
// Quality gate: every step is a shell command. If any command fails (pytest
// reports a failing test, flake8 finds a problem, ...) it exits non-zero, its
// stage fails and every later stage is SKIPPED - untested code is never
// packaged, published or deployed.
//
// Agent requirements: python3.11, Chromium + chromedriver, Docker CLI with
// compose plugin (all provided by deploy/jenkins/Dockerfile).
// Credentials: "hotel-secret-key" (Secret text) - required.
//              "registry-creds" (Username/password) - only for a remote registry such as Docker Hub.

pipeline {
    agent any

    parameters {
        // The parameterised environment-specific setting.
        choice(name: 'APP_ENV', choices: ['staging', 'prod'],
               description: 'Where to deploy. Sets APP_ENV in the container and the port: staging = 8081, prod = 8082.')
        // Used by the job's SCM settings ("*/${BRANCH}") to pick the branch to build.
        string(name: 'BRANCH', defaultValue: 'develop',
               description: 'Git branch to build (e.g. develop, main, experiment/defect-demo).')
        string(name: 'REGISTRY', defaultValue: 'localhost:5000',
               description: 'Image registry. localhost:5000 = local registry started with Jenkins. ' +
                            'For Docker Hub use docker.io/<your-docker-id> and add the "registry-creds" credential.')
    }

    triggers {
        // CI: check the repository for new commits about every 5 minutes.
        // (A GitHub webhook needs Jenkins to be reachable from the internet;
        // this local Jenkins is not, so it polls instead.)
        pollSCM('H/5 * * * *')
    }

    options {
        timestamps()
        buildDiscarder(logRotator(numToKeepStr: '20'))
        disableConcurrentBuilds()        // two deploys at once would fight over the same containers
        timeout(time: 30, unit: 'MINUTES')
    }

    environment {
        PYTHON    = 'python3.11'         // same Python version as the production image
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
                // The workspace is reused between builds. Delete outputs of the
                // previous build, otherwise a stage skipped in THIS build would
                // still publish the OLD build's test report.
                sh 'rm -rf reports dist'
                script {
                    // Version = VERSION file + commit, e.g. 1.0.0-3f2c1ab. The same
                    // tag goes on the source archive, both images and /health,
                    // so every deployment can be traced back to one commit.
                    env.APP_VERSION  = readFile('VERSION').trim()
                    env.GIT_SHORT    = sh(script: 'git rev-parse --short HEAD', returnStdout: true).trim()
                    env.IMAGE_TAG    = "${env.APP_VERSION}-${env.GIT_SHORT}"
                    env.IMAGE_PREFIX = params.REGISTRY ? "${params.REGISTRY}/" : ''
                    currentBuild.displayName = "#${env.BUILD_NUMBER} ${env.IMAGE_TAG}"
                }
                sh 'git log -1 --pretty="Building commit %h on ${BRANCH}: %s"'
            }
        }

        stage('Install dependencies') {
            steps {
                // Pinned versions from requirements*.txt = reproducible installs.
                sh '''
                    $PYTHON --version
                    $PYTHON -m venv .venv
                    .venv/bin/pip install --quiet --upgrade pip
                    .venv/bin/pip install --quiet -r requirements-dev.txt
                '''
            }
        }

        stage('Static checks') {
            steps {
                // compileall: syntax errors. flake8: style problems, unused
                // imports, undefined names (config in .flake8).
                sh '''
                    .venv/bin/python -m compileall -q app wsgi.py
                    .venv/bin/flake8 app tests wsgi.py gunicorn.conf.py
                '''
            }
        }

        stage('Unit & integration tests') {
            steps {
                sh '.venv/bin/pytest tests/unit tests/integration --junitxml=reports/unit-integration-tests.xml'
            }
        }

        stage('E2E tests (Selenium)') {
            steps {
                // Starts the app on a free port with a throw-away database and
                // drives headless Chromium. Failure screenshots: reports/screenshots/.
                sh '.venv/bin/pytest -m e2e --junitxml=reports/e2e-tests.xml'
            }
        }

        stage('Package source') {
            steps {
                // Reproducible source artifact: exactly the committed files of
                // this commit (git archive ignores anything uncommitted).
                sh '''
                    mkdir -p dist
                    git archive --format=tar.gz --prefix=hotel-booking-$IMAGE_TAG/ \
                        -o dist/hotel-booking-$IMAGE_TAG.tar.gz HEAD
                    cd dist && sha256sum hotel-booking-$IMAGE_TAG.tar.gz > hotel-booking-$IMAGE_TAG.tar.gz.sha256
                    cat hotel-booking-$IMAGE_TAG.tar.gz.sha256
                '''
            }
        }

        stage('Build images') {
            steps {
                // If this agent trusts extra root certificates (networks with
                // HTTPS inspection - see certs/README.md), give them to the
                // image build too. On a normal network there are none.
                sh '''
                    cp /usr/local/share/ca-certificates/extra/*.crt certs/ 2>/dev/null || true
                    docker build -t ${IMAGE_PREFIX}hotel-booking-app:$IMAGE_TAG \
                        --build-arg APP_VERSION=$APP_VERSION --build-arg GIT_COMMIT=$GIT_SHORT .
                    docker build -f deploy/nginx/Dockerfile -t ${IMAGE_PREFIX}hotel-booking-nginx:$IMAGE_TAG .
                '''
            }
        }

        stage('Publish images') {
            steps {
                script {
                    def push = '''
                        docker push ${IMAGE_PREFIX}hotel-booking-app:$IMAGE_TAG
                        docker push ${IMAGE_PREFIX}hotel-booking-nginx:$IMAGE_TAG
                    '''
                    if (params.REGISTRY.startsWith('localhost')) {
                        sh push                       // local registry: no login needed
                    } else {
                        // Remote registry (e.g. Docker Hub): password/token comes
                        // from Jenkins credentials and is masked in the log.
                        withCredentials([usernamePassword(credentialsId: 'registry-creds',
                                usernameVariable: 'REG_USER', passwordVariable: 'REG_PASS')]) {
                            sh 'echo "$REG_PASS" | docker login -u "$REG_USER" --password-stdin ${REGISTRY%%/*}'
                            sh push
                        }
                    }
                }
            }
        }

        stage('Deploy') {
            steps {
                // The secret is injected only for this block and masked in the log.
                withCredentials([string(credentialsId: 'hotel-secret-key', variable: 'SECRET_KEY')]) {
                    // Pull = deploy exactly what was published; --wait blocks until
                    // the containers are healthy and fails the stage if they never are.
                    sh '''
                        docker compose pull
                        docker compose up -d --no-build --wait --wait-timeout 120
                    '''
                }
            }
        }

        stage('Health check') {
            steps {
                // Smoke test through the whole chain (nginx -> gunicorn -> SQLite)
                // AND check the running release is the one we just built.
                withCredentials([string(credentialsId: 'hotel-secret-key', variable: 'SECRET_KEY')]) {
                    sh '''
                        for i in 1 2 3 4 5; do
                            docker compose exec -T nginx wget -qO- http://127.0.0.1/health > reports/health.json && break
                            sleep 3
                        done
                        cat reports/health.json; echo
                        grep -q "\\"version\\":\\"$APP_VERSION\\"" reports/health.json
                        grep -q "\\"commit\\":\\"$GIT_SHORT\\"" reports/health.json
                    '''
                }
                // Deployment record, archived with the build.
                writeFile file: 'reports/deployment.txt', text: """environment=${params.APP_ENV}
branch=${params.BRANCH}
version=${env.APP_VERSION}
commit=${env.GIT_SHORT}
image_tag=${env.IMAGE_TAG}
app_image=${env.IMAGE_PREFIX}hotel-booking-app:${env.IMAGE_TAG}
nginx_image=${env.IMAGE_PREFIX}hotel-booking-nginx:${env.IMAGE_TAG}
url=http://localhost:${env.HOST_PORT}
jenkins_build=${env.BUILD_URL}
"""
            }
        }
    }

    post {
        always {
            // Publish test results (Jenkins shows pass/fail trends) and keep the
            // reports, failure screenshots, source archive and deployment record.
            junit allowEmptyResults: true, testResults: 'reports/*.xml'
            archiveArtifacts artifacts: 'reports/**, dist/**', allowEmptyArchive: true
        }
        success {
            echo "Deployed ${env.IMAGE_TAG} to ${params.APP_ENV}: http://localhost:${env.HOST_PORT}"
        }
        failure {
            echo 'Pipeline FAILED - see the red stage above and the Test Results page. Nothing was deployed.'
        }
    }
}
