pipeline {
    agent any

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Verificar Código con flake8') {
            steps {
                sh '''
                    # Activar entorno virtual y ejecutar flake8
                    . env/bin/activate
                    flake8 .
                '''
            }
        }
    }

    post {
        always {
            echo 'Pipeline finalizado.'
        }
    }
}
