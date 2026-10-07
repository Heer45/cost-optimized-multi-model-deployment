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
    }

    // -----------------------------------------------------------
    // Post-build actions
    // -----------------------------------------------------------
    post {
        success {
            echo "Pipeline completed successfully. Docker image: ${DOCKER_IMAGE}:${BUILD_NUMBER}"
        }
        failure {
            echo 'Pipeline failed. Check the stage logs above for details.'
        }
    }
}
