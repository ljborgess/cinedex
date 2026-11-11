@echo off
chcp 65001 >nul
setlocal
cd /d "%~dp0"

echo.
echo  Catalogo de Filmes
echo  ------------------

if not exist venv\Scripts\python.exe (
    echo  [1/4] Criando o ambiente virtual...
    python -m venv venv || goto :erro
) else (
    echo  [1/4] Ambiente virtual ja existe.
)

echo  [2/4] Conferindo as dependencias...
venv\Scripts\python.exe -m pip install -q -r requirements.txt || goto :erro

echo  [3/4] Aplicando as migrations (banco, seed, conta demo e admin)...
venv\Scripts\python.exe manage.py migrate --noinput || goto :erro

echo  [4/4] Rodando os testes...
venv\Scripts\python.exe manage.py test --verbosity 1 || goto :erro

echo.
echo  Tudo pronto. Abrindo http://127.0.0.1:8000/
echo    Site:  demo  / filmes123
echo    Admin: admin / filmes123  (http://127.0.0.1:8000/admin/)
echo  Para parar o servidor: Ctrl+C
echo.
start "" http://127.0.0.1:8000/
venv\Scripts\python.exe manage.py runserver 127.0.0.1:8000
goto :eof

:erro
echo.
echo  Algo falhou acima. Confira se o Python esta instalado e tente de novo.
pause
exit /b 1
