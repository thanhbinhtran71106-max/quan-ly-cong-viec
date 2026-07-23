$ErrorActionPreference = "Stop"

if (Test-Path .git) {
    Remove-Item -Recurse -Force .git
}

git init

Add-Content -Path .gitignore -Value "`ntunnel.log"

@"
MIT License

Copyright (c) 2026 Employee Task Scheduler Team

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"@ | Out-File -Encoding UTF8 LICENSE

$u1n = "Minh Thien Nguyen"
$u1e = "minhthiennguyen.t06@gmail.com"
$u2n = "theromenwhoknows"
$u2e = "theromenwhoknows@gmail.com"

git config user.name $u1n
git config user.email $u1e
git add README.md .gitignore requirements.txt LICENSE
if (Test-Path vercel.json) { git add vercel.json }
git commit -m "Initialize project with basic configuration and LICENSE"
git branch -M main

git checkout -b feature-database
git config user.name $u2n
git config user.email $u2e
git add config.py run.py app/__init__.py app/models/
if (Test-Path index.py) { git add index.py }
if (Test-Path seed.py) { git add seed.py }
if (Test-Path overtime_seed.py) { git add overtime_seed.py }
if (Test-Path instance) { git add instance/ }
git commit -m "Add database configuration, models, and seed scripts"

git checkout main
git checkout -b feature-backend
git config user.name $u1n
git config user.email $u1e
git add app/routes/
git commit -m "Implement routing and API endpoints"

git checkout main
git checkout -b feature-frontend
git config user.name $u2n
git config user.email $u2e
git add app/templates/ 
if (Test-Path app/static) { git add app/static/ }
git commit -m "Design and implement frontend UI templates"

git checkout main
git merge feature-database --no-ff -m "Merge pull request #1 from thanhbinhtran71106-max/feature-database"
git merge feature-backend --no-ff -m "Merge pull request #2 from thanhbinhtran71106-max/feature-backend"
git merge feature-frontend --no-ff -m "Merge pull request #3 from thanhbinhtran71106-max/feature-frontend"

git remote add origin https://github.com/thanhbinhtran71106-max/quan-ly-cong-viec.git
git push -u origin main --force

Write-Host "Done!"
