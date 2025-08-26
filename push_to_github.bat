@echo off
setlocal ENABLEDELAYEDEXPANSION

REM ================== CONFIG (edit if needed) ==================
set "GITHUB_USER=aktbaraty"
set "REPO=aktbaraty-ai"
set "REMOTE=https://github.com/%GITHUB_USER%/%REPO%.git"
set "COMMIT_MSG=Initial commit: Aktbaraty AI with FlagEmbedding"
REM =============================================================

echo.
echo ============================================================
echo   Aktbaraty AI — Push to GitHub
echo   Repo: %REMOTE%
echo ============================================================
echo.

REM 1) Check git is installed
where git >nul 2>nul
if errorlevel 1 (
  echo [ERROR] Git is not installed or not in PATH.
  echo Please install Git for Windows: https://git-scm.com/download/win
  exit /b 1
)

REM 2) Ensure we're in a folder (should contain project files)
if not exist backend (
  echo [WARN] Couldn't find 'backend' folder here. Are you in the project root?
  echo Current dir: %CD%
  echo Continuing anyway...
)

REM 3) Init repo if needed
git rev-parse --is-inside-work-tree >nul 2>nul
if errorlevel 1 (
  echo [INFO] Initializing new Git repository...
  git init || (echo [ERROR] git init failed & exit /b 1)
)

REM 4) Set default branch to main
git branch -M main

REM 5) Add or update remote 'origin'
for /f "tokens=*" %%R in ('git remote') do (
  if /I "%%R"=="origin" (
    set "HAS_ORIGIN=1"
  )
)
if defined HAS_ORIGIN (
  echo [INFO] Remote 'origin' exists — updating URL...
  git remote set-url origin %REMOTE% || (echo [ERROR] Failed to set remote URL & exit /b 1)
) else (
  echo [INFO] Adding remote 'origin'...
  git remote add origin %REMOTE% || (echo [ERROR] Failed to add remote & exit /b 1)
)

REM 6) Stage files
echo [INFO] Staging files...
git add -A

REM 7) Commit (if there are staged changes)
git diff --cached --quiet
if errorlevel 1 (
  echo [INFO] Creating commit...
  git commit -m "%COMMIT_MSG%"
) else (
  echo [INFO] Nothing new to commit. Continuing to push...
)

REM 8) Push
echo [INFO] Pushing to origin/main ...
git push -u origin main
if errorlevel 1 (
  echo.
  echo [ERROR] Push failed.
  echo If prompted for password, use a GitHub Personal Access Token (PAT) with 'repo' scope.
  echo Create one here: https://github.com/settings/tokens
  echo.
  exit /b 1
)

echo.
echo [SUCCESS] Pushed successfully to %REMOTE%
echo.

endlocal
