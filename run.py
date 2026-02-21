# -*- coding: utf-8 -*-
"""
OfficeAI - Script de Inicio
Ejecuta este archivo desde la raíz del proyecto
"""
import sys
from pathlib import Path

# Añadir el directorio src al path de Python
src_path = Path(__file__).parent / 'src'
sys.path.insert(0, str(src_path))

# Ahora importar y ejecutar
from main import main

if __name__ == "__main__":
    print("Iniciando OfficeAI...")
    main()
