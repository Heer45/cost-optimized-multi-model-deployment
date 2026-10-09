// =============================================================
// Jenkinsfile - Cost-Optimized Multi-Model Deployment System
// =============================================================
// Declarative CI pipeline for automated testing and Docker build.
//
// Pipeline stages:
//   1. Checkout        - Pull latest code from source control
//   2. Install Deps    - Install Python dependencies
//   3. Run Tests       - Execute automated routing/prediction tests
//   4. Build Docker    - Package the application into a Docker image
// =============================================================

pipeline {
    agent any

    environment {
        // Name of the Docker image produced by this pipeline
        DOCKER_IMAGE = 'cost-optimized-ml-app'

        // Explicit path to the Python interpreter.
        // Jenkins runs as a Windows service and does NOT inherit the
        // interactive user PATH, so bare 'python' is not found.
        // All Python steps below must use this variable.
        PYTHON = 'C:\\Users\\Administrator\\AppData\\Local\\Programs\\Python\\Python313\\python.exe'
    }

    stages {

        // -------------------------------------------------------
        // Stage 1: Checkout
        // Pull the latest source code from the Git repository.
        // Jenkins handles this automatically when a repo is
        // configured in the job, but we keep it explicit.
        // -------------------------------------------------------
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        // -------------------------------------------------------
        // Stage 2: Install Dependencies
        // Install the Python packages listed in requirements.txt.
        // Uses --no-cache-dir to keep the workspace lean.
        // -------------------------------------------------------
        stage('Install Dependencies') {
            steps {
                bat '"C:\\Users\\Administrator\\AppData\\Local\\Programs\\Python\\Python313\\python.exe" -m pip install --no-cache-dir -r requirements.txt'
            }
        }

        // -------------------------------------------------------
        // Stage 3: Run Tests
        // Execute the existing routing and prediction tests.
        // This verifies that SmartRouter, ModelManager, and the
        // trained ML models all work correctly end-to-end.
        //
        // NOTE: bare 'python' is intentionally NOT used here.
        // The full executable path is required because Jenkins
        // runs as a Windows service without the user PATH.
        // -------------------------------------------------------
        stage('Run Tests') {
            steps {
                // Smoke-check: verify all core modules can be imported
                bat '"C:\\Users\\Administrator\\AppData\\Local\\Programs\\Python\\Python313\\python.exe" -c "import router, model_manager, cost_simulator; print(\'Application imports OK\')"'

                // Run the full routing and prediction test suite
                bat '"C:\\Users\\Administrator\\AppData\\Local\\Programs\\Python\\Python313\\python.exe" test_routing.py'
            }
        }

        // -------------------------------------------------------
        // Stage 4: Build Docker Image
        // Build a tagged Docker image containing the Streamlit
        // application, trained models, and all dependencies.
        // The image is tagged with the Jenkins build number
        // for traceability.
        // -------------------------------------------------------
        stage('Build Docker Image') {
            steps {
                // Uses the absolute Docker executable path because Jenkins
                // runs as a Windows service and 'docker' is not on its PATH.
                bat '"C:\\Users\\Administrator\\AppData\\Local\\Programs\\DockerDesktop\\resources\\bin\\docker.exe" build -t cost-optimized-ml-app:%BUILD_NUMBER% .'
            }
        }

        // -------------------------------------------------------
        // Stage 5: Test Docker Container
        // Start a temporary container from the image just built,
        // poll the Streamlit health endpoint on port 8502 (avoids
        // collisions with a live app on 8501), and fail the build
        // if the health check does not pass within 60 seconds.
        // Cleanup is handled in the post-always block below so
        // the container is removed even when the health check
        // or any later stage fails.
        // -------------------------------------------------------
        stage('Test Docker Container') {
            steps {
                // Start the test container in detached mode
                bat '"C:\\Users\\Administrator\\AppData\\Local\\Programs\\DockerDesktop\\resources\\bin\\docker.exe" run -d --name ml-app-test-%BUILD_NUMBER% -p 8502:8501 cost-optimized-ml-app:%BUILD_NUMBER%'

                // Poll the Streamlit health endpoint every 5 s,
                // up to 12 attempts (60 s total).
                bat '''
                    @echo off
                    setlocal enabledelayedexpansion
                    echo Polling Streamlit health endpoint (timeout: 60 s)...
                    for /L %%i in (1,1,12) do (
                        curl.exe -s -o NUL -w "%%{http_code}" http://localhost:8502/_stcore/health > __health_status.txt 2>&1
                        set /p STATUS=<__health_status.txt
                        echo   Attempt %%i/12 - HTTP !STATUS!
                        if "!STATUS!"=="200" (
                            echo Health check passed on attempt %%i.
                            del __health_status.txt 2>NUL
                            exit /b 0
                        )
                        timeout /t 5 /nobreak >NUL
                    )
                    echo Health check timed out after 60 s. Container logs:
                    "C:\\Users\\Administrator\\AppData\\Local\\Programs\\DockerDesktop\\resources\\bin\\docker.exe" logs ml-app-test-%BUILD_NUMBER%
                    del __health_status.txt 2>NUL
                    exit /b 1
                '''
            }
        }
    }

    // -----------------------------------------------------------
    // Post-build actions
    // -----------------------------------------------------------
    post {
        always {
            // Always remove the test container so Jenkins workspace
            // stays clean, even when a stage above failed.
            bat '"C:\\Users\\Administrator\\AppData\\Local\\Programs\\DockerDesktop\\resources\\bin\\docker.exe" stop ml-app-test-%BUILD_NUMBER% 2>NUL & "C:\\Users\\Administrator\\AppData\\Local\\Programs\\DockerDesktop\\resources\\bin\\docker.exe" rm ml-app-test-%BUILD_NUMBER% 2>NUL & exit /b 0'
        }
        success {
            echo "Pipeline completed successfully. Docker image: ${DOCKER_IMAGE}:${BUILD_NUMBER}"
        }
        failure {
            echo 'Pipeline failed. Check the stage logs above for details.'
        }
    }
}
