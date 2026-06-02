@echo off
set "Mes=%~1"
if "%Mes%"=="" set "Mes=完成新功能"

git checkout dev
git add .
git commit -m "%Mes%"
git push origin dev

git checkout main
git pull origin main
git merge dev
git push origin main