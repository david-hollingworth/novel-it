pipeline {
    agent any
    
    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }
        
        stage('Setup') {
            steps {
                dir('novelapp') {
                    sh '''
                        python3 -m venv venv
                        . venv/bin/activate
                        pip install --upgrade pip
                        pip install -r requirements.txt
                        pip install behave 
                        pip install allure-behave
                    '''
                }
            }
        }
        
        stage('Database Setup') {
            steps {
                dir('novelapp') {
                    sh '''
                        . venv/bin/activate
                        python manage.py migrate --settings=novelapp.settings_test
                    '''
                }
            }
        }

        stage('Run BDD Tests') {
            steps {
                dir('novelapp') {
                    sh '''
                        . venv/bin/activate
                        export DJANGO_SETTINGS_MODULE=novelapp.settings_test
                        python manage.py behave -f allure_behave.formatter:AllureFormatter -o allure-results
                    '''
                }
            }
        }
    }
    
    post {
        always {
            script {
                allure([
                    includeProperties: false,
                    jdk: '',
                    results: [[path: 'novelapp/allure-results']]
                ])
            }
        }
    }
}
