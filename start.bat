@echo off
echo.
echo  ==========================================
echo   RoadSoS - Emergency AI Assistant
echo   National Road Safety Hackathon 2026
echo  ==========================================
echo.

REM Step 1: Install dependencies
echo [1/4] Installing dependencies...
pip install streamlit requests geopy python-dotenv groq -q
if %errorlevel% neq 0 (
    echo WARNING: Some packages may not have installed. Continuing...
)

REM Step 2: Load environment variables if .env exists
if exist .env (
    echo [2/4] Loading .env configuration...
    for /f "usebackq tokens=1,* delims==" %%A in (".env") do (
        if not "%%A"=="" if not "%%A:~0,1%"=="#" set "%%A=%%B"
    )
) else (
    echo [2/4] No .env file found. App will run in offline mode.
    echo       Copy .env.example to .env and add your GROQ_API_KEY for AI features.
)

REM Step 3: Clean any stale DB journal and re-initialise database
echo [3/4] Initialising database...
if exist roadsos.db-journal del /f roadsos.db-journal 2>nul
python database/init_db.py
if %errorlevel% neq 0 (
    echo ERROR: Database initialisation failed. Please check Python is installed.
    pause
    exit /b 1
)

REM Step 4: Launch app
echo [4/4] Launching RoadSoS...
echo.
echo  ==========================================
echo   App running at: http://localhost:8501
echo   Press Ctrl+C to stop
echo  ==========================================
echo.
streamlit run app.py --server.port 8501 --server.headless false
