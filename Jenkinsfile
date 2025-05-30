pipeline {
    agent any

    stages {
        stage('Inicializando...') {
            steps {
                echo 'Asignando workspace y validando entorno.'
            }
        }

        stage('Flake8 en carpetas externas (host)') {
            steps {
                sh '''
                    # Activar entorno virtual y ejecutar flake8
                    . $HOME/env/bin/activate
                    flake8 --max-complexity=10 --max-line-length=200 --ignore=F811,E402 monitoreo cliente_comandos
                '''
            }
        }
        stage('Flake8 dentro del contenedor Django') {
            steps {
                sh '''
                    docker exec front_web flake8 --max-complexity=10 --max-line-length=200 --ignore=F811,E402 Yoltic
                '''
            }
        }

        stage('Pruebas unitarias') {
            steps {
                timeout(time: 2, unit: 'MINUTES') {
                    sleep time: 20, unit: 'SECONDS'
                    sh """docker compose exec front_web sh -c 'cd Yoltic && python3 manage.py test front'"""
                    sh """docker exec front_web bash -c 'cd front_web/Yoltic && coverage run --branch --source=Yoltic --omit="*test*,*migrations*,*__init*,*settings*,*apps*,*wsgi*,*admin.py,*asgi.py,manage.py,*urls.py" manage.py test && coverage html'"""
                    sh 'docker cp front_web:/front_web/Yoltic/htmlcov .'

                    publishHTML target:[
                        allowMissing: false,
                        alwaysLinkToLastBuild: false,
                        keepAll: true,
                        reportDir: './htmlcov',
                        reportFiles: 'index.html',
                        reportName: 'Reporte de cobertura Cargas académicas',
                        reportTitles: 'Cobertura de código'
                    ]
                }
            }
        }


    post {
        always {
            //cleanWs()
            sh 'docker compose down -v'
        }
        success {
            echo "Despliegue completado exitosamente con versión ${VERSION}"
        }
        failure {
            echo "El pipeline falló en algún paso."
        }
    }
}
chuckNorris()
