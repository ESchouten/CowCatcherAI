@echo off
REM Configuratie - pas deze variabelen aan naar jouw situatie
REM Om de conda versie te zien in anaconda prompt = echo %CONDA_PREFIX%
set CONDA_PAD="C:\ProgramData\anaconda3\Scripts\activate.bat"
set PROJECT_SCHIJF=F:
set PROJECT_MAP=jouw_project_map_pad_zonder_schijfnaam
set SCRIPT_NAAM=jouw_script.py

REM Het script uitvoeren
echo Anaconda omgeving activeren...
call %CONDA_PAD%

echo Overschakelen naar project schijf en map...
%PROJECT_SCHIJF%
cd %PROJECT_MAP%

echo Python script starten...
python %SCRIPT_NAAM%

echo.
echo Script voltooid!
pause
