@echo off
REM 매일 자동 실행용: 어필리에이트 패널 수집 -> products.csv -> D1 반영.
REM 작업 스케줄러에 등록해서 쓴다. 시작 위치 = C:\lagitren\collector
setlocal enabledelayedexpansion
cd /d "%~dp0"

set "PORT=9223"
set "DATADIR=%LocalAppData%\lagitren-chrome"
set "PANEL=https://partner.tiktokshop.com/affiliate-product-management/affiliate-product-pool/ranking?tab=0&market=4&prePage=product_ranking"
set "PANEL_CDP=http://127.0.0.1:%PORT%"

if not exist "logs" mkdir "logs"
for /f %%d in ('powershell -NoProfile -Command "Get-Date -Format yyyy-MM-dd"') do set "TODAY=%%d"
set "LOG=logs\panel_%TODAY%.log"

echo. >> "%LOG%"
echo ===== %DATE% %TIME% ===== >> "%LOG%"

REM --- 1) Chrome 이 9223 으로 떠 있는지 확인, 없으면 띄운다 -------------------
netstat -ano | findstr /r /c:":%PORT% .*LISTENING" >nul 2>&1
if errorlevel 1 (
  echo [panel] Chrome 기동 중... >> "%LOG%"
  set "CHROME="
  for %%P in (
    "%ProgramFiles%\Google\Chrome\Application\chrome.exe"
    "%ProgramFiles(x86)%\Google\Chrome\Application\chrome.exe"
    "%LocalAppData%\Google\Chrome\Application\chrome.exe"
  ) do if not defined CHROME if exist %%P set "CHROME=%%~P"
  if not defined CHROME (
    echo [panel] ERROR: chrome.exe 를 찾지 못함 >> "%LOG%"
    exit /b 1
  )
  start "" /min "!CHROME!" --remote-debugging-port=%PORT% --user-data-dir="%DATADIR%" --no-first-run --no-default-browser-check --window-size=1360,900 "%PANEL%"
  set "READY="
  for /L %%i in (1,1,30) do (
    if not defined READY (
      timeout /t 1 /nobreak >nul
      netstat -ano | findstr /r /c:":%PORT% .*LISTENING" >nul 2>&1
      if not errorlevel 1 set "READY=1"
    )
  )
  if not defined READY (
    echo [panel] ERROR: 30초 내 포트 %PORT% 열리지 않음 >> "%LOG%"
    exit /b 1
  )
)

REM --- 2) 패널 수집 -> products.csv ----------------------------------------
echo [panel] 수집 시작 >> "%LOG%"
py -u affiliate_panel.py >> "%LOG%" 2>&1
if errorlevel 1 (
  echo [panel] ERROR: 수집 실패 ^(로그인 만료 가능^) >> "%LOG%"
  exit /b 1
)

REM --- 3) D1 반영 ----------------------------------------------------------
py -u main.py shopee >> "%LOG%" 2>&1

REM --- 4) products.csv 만 리포에 반영 (실패해도 넘어감) ---------------------
REM  주의: 공개 리포이므로 products.csv 외 파일은 절대 add 하지 않는다.
pushd ..
git add collector/products.csv >nul 2>&1
git diff --cached --quiet
if errorlevel 1 (
  git -c user.name="lagitren-local" -c user.email="noreply@lagitren.id" commit -m "produk: perbarui daftar dari panel afiliasi (otomatis)" >> "collector\%LOG%" 2>&1
  git pull --rebase >> "collector\%LOG%" 2>&1
  git push >> "collector\%LOG%" 2>&1
) else (
  echo [panel] 변경 없음, 커밋 생략 >> "collector\%LOG%"
)
popd

REM --- 5) 30일 지난 로그 정리 ----------------------------------------------
forfiles /p logs /m panel_*.log /D -30 /C "cmd /c del @path" >nul 2>&1

echo [panel] 완료 >> "%LOG%"
endlocal
