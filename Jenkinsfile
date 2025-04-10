pipeline {
    agent any

    stages {
        stage('Clone Repo') {
            steps {
                git 'https://github.com/MichaelOffor1999/webServices.git'
            }
        }

        stage('Build Docker Containers') {
            steps {
                sh 'docker-compose build'
            }
        }

        stage('Start Containers') {
            steps {
                sh 'docker-compose up -d'
            }
        }

        stage('Seed Database') {
            steps {
                sh 'docker exec webservicesassignment1-api-1 python load_data.py'
            }
        }

        stage('Run Tests') {
            steps {
                sh 'docker exec webservicesassignment1-api-1 pytest tests/test_app.py > test_results.txt'
            }
        }

        stage('Export MongoDB') {
            steps {
                sh '''
                docker exec webservicesassignment1-mongo-1 mongodump --db=inventory_db --out=/data/dbdump
                docker cp webservicesassignment1-mongo-1:/data/dbdump ./dbdump
                zip -r database.zip dbdump
                '''
            }
        }

        stage('Create Final Zip') {
            steps {
                sh '''
                zip -r complete-$(date +"%Y-%m-%d-%H%M").zip app/ tests/ auto_products.csv test_results.txt database.zip README.txt
                '''
            }
        }
    }

    post {
        always {
            archiveArtifacts artifacts: '*.zip', fingerprint: true
        }
    }
}
