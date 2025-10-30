@echo off
REM Format all Python files with Black
echo Running Black formatter...
python -m black .
echo.
echo Formatting complete! Run 'git diff' to see changes.
pause
