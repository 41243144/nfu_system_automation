@echo off
REM 檢查是否已經有虛擬環境
if exist venv (
    echo The virtual environment already exists and is starting the virtual environment...
) else (
    echo Create a new virtual environment...
    python -m venv venv
    echo Upgrading pip...
    call venv\Scripts\activate
    python -m pip install --upgrade pip
)

REM 啟動虛擬環境
call venv\Scripts\activate

REM 檢查是否存在 requirements.txt 文件並安裝
if exist requirements.txt (
    echo Installing packages in requirements.txt...
    pip install -r requirements.txt
) else (
    echo Requirements.txt file not found, skipping package installation.
)

echo Virtual environment setup complete. To activate the environment, run:
echo venv\Scripts\activate
