import sys
from cx_Freeze import setup, Executable

# Defina as opções de build
build_exe_options = {
    "packages": ["os", "flask", "flask_sqlalchemy", "blinker", "click", "greenlet",
                 "itsdangerous", "jinja2", "markupsafe", "pyodbc", "sqlalchemy", 
                 "typing_extensions", "werkzeug"],
    "include_files": [
        ("templates", "templates"),
        ("icon.ico", "icon.ico"),
        "requirements.txt"
    ],
    "build_exe": "build_output"  # Define um novo diretório para o build
}


# Define a base para o sistema Windows
base = None
if sys.platform == "win32":
    base = "Win32GUI"

# Configuração do cx_Freeze
setup(
    name="PIM4-Lotus",
    version="1.0",
    description="Projeto PIM4-Lotus",
    options={"build_exe": build_exe_options},
    executables=[Executable("app.py", base=base, icon="icon.ico")]
)
