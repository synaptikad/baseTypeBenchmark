@echo off
REM ===========================================
REM Connexion rapide au VPS OVH
REM Usage: Modifier IP_VPS puis double-cliquer
REM ===========================================

SET IP_VPS=VOTRE_IP_ICI

echo Connexion au VPS: %IP_VPS%
echo.
ssh root@%IP_VPS%

pause
