@echo off
echo Installing dependencies...
call bundle install
echo Starting Local Blog...
echo Open http://localhost:4000 in your browser
call bundle exec jekyll serve
pause
