@echo off
REM 대안: 완전히 분리된 데이터 폴더 + 별도 포트(9223)로 Chrome 실행.
REM 포트를 9223으로 둬서 기존 TikTok/Instagram/X 수집기(9222)를 건드리지 않는다.
REM 평소 쓰는 Chrome 과 절대 충돌하지 않으므로 디버깅 포트가 항상 열린다.
REM 대신 새 프로필이라 이 창에서 틱톡샵 로그인을 "한 번" 해야 한다 (이후 유지됨).
setlocal enabledelayedexpansion

set "PORT=9223"
set "DATADIR=%LocalAppData%\lagitren-chrome"
set "PANEL=https://partner.tiktokshop.com/affiliate-product-management/affiliate-product-pool/ranking?tab=0&market=4&prePage=product_ranking"

set "CHROME="
for %%P in (
  "%ProgramFiles%\Google\Chrome\Application\chrome.exe"
  "%ProgramFiles(x86)%\Google\Chrome\Application\chrome.exe"
  "%LocalAppData%\Google\Chrome\Application\chrome.exe"
) do if not defined CHROME if exist %%P set "CHROME=%%~P"

if not defined CHROME (
  echo [X] chrome.exe 를 찾지 못했습니다. ^& pause ^& exit /b 1
)

echo [i] 별도 데이터 폴더: %DATADIR%
echo [1/3] Chrome 실행...
start "" "%CHROME%" --remote-debugging-port=%PORT% --user-data-dir="%DATADIR%" --no-first-run --no-default-browser-check "%PANEL%"

echo [2/3] 포트 %PORT% 대기 (최대 25초)...
set "READY="
for /L %%i in (1,1,25) do (
  if not defined READY (
    timeout /t 1 /nobreak >nul
    netstat -ano | findstr /r /c:":%PORT% .*LISTENING" >nul 2>&1
    if not errorlevel 1 set "READY=1"
  )
)

echo [3/3] 결과:
echo.
if defined READY (
  echo [OK] Chrome 준비 완료 - 127.0.0.1:%PORT%
  echo      이 창은 새 프로필이므로 partner.tiktokshop.com 에
  echo      먼저 로그인하세요 ^(최초 1회, 이후 계속 유지됩니다^).
  echo      로그인 후 Chrome 을 닫지 말고 다음을 실행:
  echo.
  echo         cd /d C:\lagitren\collector
  echo         set PANEL_CDP=http://127.0.0.1:%PORT%
  echo         python affiliate_panel.py --discover "%PANEL%"
) else (
  echo [X] 포트 %PORT% 가 여전히 열리지 않았습니다.
  echo     다른 프로세스가 포트를 쓰고 있을 수 있습니다. 확인:
  echo         netstat -ano ^| findstr :%PORT%
)
echo.
pause
