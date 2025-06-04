pipeline {
    agent any

    stages {
        stage('Inicializando...') {
            steps {
                echo 'Asignando workspace y validando entorno.'
            }
        }
        stage('Entorno de desarrollo') {
            steps {
                sh 'docker compose up -d --build front_web'
                //sh 'chmod +x script_jenkins.sh'
            }
        }
        stage('Flake8 en carpetas externas (host)') {
            steps {
                sh '''
                    # Activar entorno virtual y ejecutar flake8
                    . $HOME/env/bin/activate
                    flake8 --max-complexity=10 --max-line-length=200 --ignore=F811,E402,C901 monitoreo cliente_comandos
                '''
            }
        }
        stage('Flake8 dentro del contenedor Django') {
            steps {
                sh '''
                    docker exec front_web flake8 --max-complexity=10 --max-line-length=200 --ignore=F811,E402,C901 Yoltic
                '''
            }
        }

        stage('Pruebas unitarias') {
            steps {
                timeout(time: 2, unit: 'MINUTES') {
                    sleep time: 20, unit: 'SECONDS'

                    // Ejecutar tests Django
                    sh '''
                        docker exec front_web bash -c "cd /front_web/Yoltic && python3 manage.py test front"
                    '''

                    // Ejecutar tests con coverage
                    sh '''
                        docker exec front_web bash -c "cd /front_web/Yoltic && coverage run --branch --source='.' --omit='*test*,*migrations*,*__init*,*settings*,*apps*,*wsgi*,*admin.py,*asgi.py,manage.py,*urls.py' manage.py test front"
                    '''

                    //Crear HTML
                    sh '''
                        docker exec front_web bash -c "cd /front_web/Yoltic && coverage html"
                    '''

                    // Copiar reporte de cobertura desde el contenedor a Jenkins workspace
                    sh '''
                        docker cp front_web:/front_web/Yoltic/htmlcov .
                    '''

                    // Publicar reporte HTML
                    publishHTML target:[
                        allowMissing: false,
                        alwaysLinkToLastBuild: false,
                        keepAll: true,
                        reportDir: './htmlcov',
                        reportFiles: 'index.html',
                        reportName: 'Reporte de cobertura Yoltic',
                        reportTitles: 'Cobertura de código'
                    ]
                }
            }
        }

    }


    post {
        always {
            //cleanWs()
            sh 'docker compose down -v'
        }
        success {
            echo "El pipeline finalizo correctamente"
        }
        failure {
            echo "El pipeline falló en algún paso."
        }
    }
}
chuckNorris()

