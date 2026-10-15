@echo off
SETLOCAL EnableDelayedExpansion
TITLE Bone Fracture AI Detection System - Launcher

echo =====================================================================
echo              BONE FRACTURE AI DETECTION PLATFORM                     
echo           Ultralytics YOLO Clinical Vision - Launcher                
echo =====================================================================
echo.

cd /d "%~dp0"

:: -----------------------------------------------------------------------
:: STEP 1: Python Runtime & Virtual Environment Check
:: -----------------------------------------------------------------------
echo [STEP 1/4] Checking Python Runtime Environment...
IF NOT EXIST "venv\" (
    echo   - Virtual environment not found. Setting up clean workspace...
    py -3.11 -m venv venv >nul 2>&1
    IF !ERRORLEVEL! NEQ 0 (
        echo   - Python 3.11 not found via 'py'. Falling back to system python...
        python -m venv venv
    )
    IF NOT EXIST "venv\Scripts\activate.bat" (
        echo   [ERROR] Failed to initialize virtual environment. Ensure Python is installed.
        pause
        exit /b 1
    )
    echo   - Virtual environment created successfully.
    
    echo [STEP 2/4] Installing Required Packages (Flask, OpenCV, YOLO, PyTorch)...
    call venv\Scripts\activate.bat
    python -m pip install --upgrade pip >nul 2>&1
    pip install -r requirements.txt
) ELSE (
    echo   - Existing virtual environment detected.
    echo [STEP 2/4] Activating Virtual Environment...
    call venv\Scripts\activate.bat
)
echo.

:: -----------------------------------------------------------------------
:: STEP 3: Model Weights and Storage Verification
:: -----------------------------------------------------------------------
echo [STEP 3/4] Verifying Model Weights and Output Storage...
IF NOT EXIST "models\best.pt" (
    echo   [WARNING] Trained weights file 'models\best.pt' not found!
    echo   Please ensure your trained YOLO weights are placed in the models directory.
) ELSE (
    echo   - YOLO weights verified: models\best.pt
)

IF NOT EXIST "static\uploads\" mkdir "static\uploads"
IF NOT EXIST "static\results\" mkdir "static\results"
echo   - Upload and Results directories verified.
echo.

:: -----------------------------------------------------------------------
:: STEP 4: Launch Server & Browser
:: -----------------------------------------------------------------------
echo [STEP 4/4] Starting Flask Web Server...
echo.
echo =====================================================================
echo   FRACTURE DETECTION SERVER ACTIVE
echo   Opening: http://127.0.0.1:5000 in your browser...
echo   Press CTRL+C in this console window to gracefully stop the server.
echo =====================================================================
echo.

start "" http://127.0.0.1:5000
python app.py

pause
