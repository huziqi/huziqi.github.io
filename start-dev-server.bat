@echo off
echo Starting Jekyll development server...
echo.
echo The website will be available at: http://localhost:4000
echo Press Ctrl+C to stop the server
echo.
bundle exec jekyll serve --livereload --host localhost --port 4000 --config _config.yml
