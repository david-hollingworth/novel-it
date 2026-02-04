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
                sh '''
                    python3 -m venv venv
                    . venv/bin/activate
                    pip install --upgrade pip
                    pip install -r requirements.txt
                    pip install behave behave-html-formatter
                '''
            }
        }
        
        stage('Database Setup') {
            steps {
                sh '''
                    . venv/bin/activate
                    python manage.py migrate
                '''
            }
        }
        
        stage('Run BDD Tests') {
            steps {
                sh '''
                    . venv/bin/activate
                    behave --format html --outfile behave-report.html --format plain
                '''
            }
        }
    }
    
    post {
        always {
            publishHTML([
                allowMissing: false,
                alwaysLinkToLastBuild: true,
                keepAll: true,
                reportDir: '.',
                reportFiles: 'behave-report.html',
                reportName: 'Behave Test Report'
            ])
        }
    }
}
