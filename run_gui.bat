@echo off
echo Starting Google Books Crawler GUI...
echo.

REM Use system Python directly (virtual environment has path issues)
REM If you want to use virtual environment, fix the Python path in Scripts folder
python gui_app.py

REM Pause to see any error messages
pause