pipeline {
    agent any

    options {
        timeout(time: 20, unit: 'MINUTES')
    }

    triggers {
        pollSCM('H/5 * * * *')
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Set up virtualenv') {
            steps {
                dir('novelapp') {
                    sh '''
                        test -d venv || python3 -m venv venv
                        . venv/bin/activate
                        pip install --upgrade pip
                        pip install -r requirements.txt
                    '''
                }
            }
        }

        stage('Install Playwright browser') {
            steps {
                dir('novelapp') {
                    sh '''
                        . venv/bin/activate
                        playwright install chromium
                    '''
                }
            }
        }

        stage('Run tests') {
            steps {
                dir('novelapp') {
                    withCredentials([string(credentialsId: 'novelit-database-url', variable: 'DATABASE_URL')]) {
                        sh '''
                            . venv/bin/activate
                            pytest -v --junitxml=results.xml
                        '''
                    }
                }
            }
        }
    }

    post {
        always {
            dir('novelapp') {
                junit 'results.xml'
            }
        }
    }
}
