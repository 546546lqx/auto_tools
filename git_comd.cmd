@echo off
setlocal EnableExtensions EnableDelayedExpansion

set "CommitMessage=%~1"
set "ExcludePattern="

if /I "%~1"=="-Mes" set "CommitMessage=%~2"
if /I "%~1"=="--message" set "CommitMessage=%~2"
if /I "%~1"=="-m" set "CommitMessage=%~2"
if /I "%~1"=="/m" set "CommitMessage=%~2"

if /I "%~1"=="-x" set "ExcludePattern=%~2"
if /I "%~1"=="--exclude" set "ExcludePattern=%~2"

if "%CommitMessage%"=="" set "CommitMessage=完成新功能"

if "%ExcludePattern%"=="" (
    set /p "ExcludePattern=请输入要排除的路径或模式（例如 application\\__pycache__\\*；留空表示不排除）: "
)

echo 当前提交内容: !CommitMessage!
if not "%ExcludePattern%"=="" echo 排除路径/模式: !ExcludePattern!

if not "%ExcludePattern%"=="" (
    for /f "delims=" %%F in ('git status --porcelain ^| findstr /R "^[AMRCU?][AMRCU?]"') do (
        echo %%F | findstr /I /R /C:"!ExcludePattern!" >nul
        if errorlevel 1 (
            git add "%%~fF" 2>nul
        ) else (
            echo 已排除: %%F
        )
    )
) else (
    git add .
)

git checkout dev
git commit -m "!CommitMessage!"
git push origin dev

git checkout main
git pull origin main
git merge dev
git push origin main

endlocal