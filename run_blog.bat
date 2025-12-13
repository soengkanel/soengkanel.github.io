@echo off
echo Starting Jekyll site with Docker...
docker run --rm --volume="%cd%:/srv/jekyll" -p 4000:4000 jekyll/jekyll jekyll serve --force_polling
pause
