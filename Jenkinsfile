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
                        pip install behave behave-html-formatter
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
                        behave -f behave_html_formatter:HTMLFormatter -o behave-report.html
                    '''
                }
            }
        }
    }
    
    post {
        always {
            publishHTML([
                allowMissing: false,
                alwaysLinkToLastBuild: true,
                keepAll: true,
                reportDir: 'novelapp',
                reportFiles: 'behave-report.html',
                reportName: 'Behave Test Report'
            ])
        }
    }
}
