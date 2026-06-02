@echo off
<<<<<<< HEAD
setlocal EnableExtensions EnableDelayedExpansion

set "CommitMessage=%~1"
if /I "%~1"=="-Mes" set "CommitMessage=%~2"
if /I "%~1"=="--message" set "CommitMessage=%~2"
if /I "%~1"=="-m" set "CommitMessage=%~2"
if /I "%~1"=="/m" set "CommitMessage=%~2"
if "%CommitMessage%"=="" set "CommitMessage=完成新功能"

echo 当前提交内容: !CommitMessage!

git checkout dev
git add .
git commit -m "!CommitMessage!"
=======
set "Mes=%~1"
if "%Mes%"=="" set "Mes=完成新功能"

git checkout dev
git add .
git commit -m "%Mes%"
>>>>>>> dev
git push origin dev

git checkout main
git pull origin main
git merge dev
<<<<<<< HEAD
git push origin main

endlocal
=======
git push origin main
>>>>>>> dev
