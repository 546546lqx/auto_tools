@echo off
set "Mes=%~1"
if "%Mes%"=="" set "Mes="
git checkout dev
git commit -m "!CommitMessage!"
git push origin dev

git checkout main
git pull origin main
git merge dev
git push origin main

endlocal