@echo off
REM Chrome을 디버깅 포트로 실행한다 (로컬 수집기 TikTok / Instagram / X / 어필리에이트 패널용).
setlocal enabledelayedexpansion

set "PORT=9222"
set "PROFILE=chrome-lagitren"
set "PANEL=https://partner.tiktokshop.com/affiliate-product-management/affiliate-product-pool/ranking?tab=0&market=4&prePage=product_ranking"

set "CHROME="
for %%P in (
  "%ProgramFiles%\Google\Chrome\Application\chrome.exe"
  "%ProgramFiles(x86)%\Google\Chrome\Application\chrome.exe"
  "%LocalAppData%\Google\Chrome\Application\chrome.exe"
) do if not defined CHROME if exist %%P set "CHROME=%%~P"

if not defined CHROME (
  echo [X] chrome.exe 를 표준 위치에서 찾지 못했습니다.
  echo     Chrome 에서 chrome://version 을 열고 "명령줄" 항목의 경로를 알려주세요.
  pause ^& exit /b 1
)
echo [i] Chrome : "%CHROME%"
echo [i] 프로필 : %PROFILE%
echo.

echo [1/4] 실행 중인 Chrome 전부 종료...
taskkill /IM chrome.exe /F >nul 2>&1
timeout /t 3 /nobreak >nul
tasklist /FI "IMAGENAME eq chrome.exe" 2>nul | find /i "chrome.exe" >nul
if not errorlevel 1 (
  echo     [!] 아직 chrome.exe 가 남아 있습니다. 5초 더 대기...
  timeout /t 5 /nobreak >nul
  taskkill /IM chrome.exe /F >nul 2>&1
  timeout /t 2 /nobreak >nul
)

echo [2/4] --remote-debugging-port=%PORT% 로 Chrome 실행...
start "" "%CHROME%" --remote-debugging-port=%PORT% --profile-directory=%PROFILE% --no-first-run --no-default-browser-check "%PANEL%"

echo [3/4] 포트 %PORT% 준비 대기 (최대 25초)...
set "READY="
for /L %%i in (1,1,25) do (
  if not defined READY (
    timeout /t 1 /nobreak >nul
    netstat -ano | findstr /r /c:":%PORT% .*LISTENING" >nul 2>&1
    if not errorlevel 1 set "READY=1"
  )
)

echo [4/4] 결과:
echo.
if defined READY (
  echo [OK] Chrome 준비 완료 - 127.0.0.1:%PORT%
  echo      1^) partner.tiktokshop.com 이 로그인 상태인지 확인하세요.
  echo      2^) Chrome 을 닫지 마세요.
  echo      3^) 다른 명령창에서 실행:
  echo.
  echo         cd /d C:\lagitren\collector
  echo         python affiliate_panel.py --discover "%PANEL%"
) else (
  echo [X] 25초가 지나도 포트 %PORT% 가 열리지 않았습니다.
  echo.
  echo     진단:
  tasklist /FI "IMAGENAME eq chrome.exe" 2>nul | find /i "chrome.exe" >nul
  if errorlevel 1 (
    echo     - chrome.exe 가 아예 실행되지 않음 -^> Chrome 실행 자체가 실패.
    echo       아래 줄을 직접 실행해서 오류 메시지를 확인하세요:
    echo         "%CHROME%" --remote-debugging-port=%PORT% --profile-directory=%PROFILE%
  ) else (
    echo     - chrome.exe 는 실행 중이지만 디버깅 포트가 없음.
    echo       = 플래그가 무시된 상태. 같은 데이터 폴더를 쓰는 다른 Chrome
    echo         인스턴스가 살아 있다는 뜻입니다 ^(백그라운드 확장, 작업 스케줄러 등^).
    echo       조치: chrome://settings/system 에서
    echo             "Chrome 을 닫아도 백그라운드 앱 계속 실행" 을 끄고 다시 시도.
    echo.
    echo     더 확실한 대안 ^(별도 프로필, 로그인 1회 필요^):
    echo       start_chrome_cdp_isolated.bat
  )
)
echo.
pause
