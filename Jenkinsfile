pipeline {

	agent { 
		docker { 
			image '13065729n/centos-python3:latest' 
			args '-u root:root -v $HOME/workspace'
		} 
	}

	triggers {
		cron('*/5 * * * *')
	}

	stages {
		stage('test') {
			steps {
				sh 'python3.6 -u moc-health-check/automate.py'
			}

			post {
				failure {
					load "env.groovy"
					echo "${env.DB_URL}"
					emailext attachmentsPattern: 'moc-health-check/error.log', body: "${env.DB_URL}", subject: 'test', to: '13065729n@gmail.com'
				}
			}
		}
	}
}
