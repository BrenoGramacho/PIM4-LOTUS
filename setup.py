import sys
from cx_Freeze import setup, Executable

# Opções de build, incluindo as bibliotecas e templates
build_exe_options = {
    "packages": ["os", "flask", "flask_sqlalchemy", "blinker", "click", "greenlet",
                 "itsdangerous", "jinja2", "markupsafe", "pyodbc", "sqlalchemy", 
                 "typing_extensions", "werkzeug"],
    "include_files": [
        ("templates", "templates"),  # Inclui a pasta de templates
        ("icon.ico", "icon.ico"),    # Inclui o ícone, se necessário
        "requirements.txt"           # Inclui o arquivo de dependências
    ],
    
}

base = None
if sys.platform == "win32":
    base = "Win32GUI"

setup(
    name="PIM4-LOTUS",
    version="0.1",
    description="Minha Aplicação PIM4-LOTUS!",
    options={"build_exe": build_exe_options},
    executables=[Executable("app.py", base=base)]
)
