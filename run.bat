@echo off
chcp 65001
:start
set input=
set /p input=请输入股票代码（如300270）:
echo 您输入的股票代码是：%input%
.\venv\Scripts\python search.py %input%
choice /c yn /m 请确认您的选择：
if %errorlevel% equ 1 goto y
if %errorlevel% equ 2 goto n
:y
.\venv\Scripts\python data.py %input%
goto date
:n
goto start
:date
set old=%input%
set input=
set /p input=请输入预测日期（如20190909）:
echo 您输入的预测日期是：%input%
choice /c yn /m 请确认您的输入：
if %errorlevel% equ 1 goto yy
if %errorlevel% equ 2 goto nn
:yy
.\venv\Scripts\python analysis.py %old% %input%
goto end
:nn
goto date
:end
pause