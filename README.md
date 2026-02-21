# OfficeAI 🤖

Asistente inteligente experto en Microsoft Office con capacidades de búsqueda web y aprendizaje continuo.

## 🚀 Instalación Rápida

### Linux/macOS
1. Crea y activa un entorno virtual: `python3 -m venv venv && source venv/bin/activate`
2. Instala dependencias: `pip install -r requirements.txt`
3. Ejecuta el script de configuración inicial:
```bash
chmod +x setup.sh
./setup.sh
```

### Windows
1. Crea y activa un entorno virtual: `python -m venv venv` y luego `venv\Scripts\activate`
2. Instala dependencias: `pip install -r requirements.txt`
3. Ejecuta el script de configuración inicial:
```batch
setup.bat
```

El script se encargará de:
1. Crear un archivo `.env` basado en la plantilla (si no existe).
2. Asegurar que los directorios de datos existan.

## ⚙️ Configuración

Edita el archivo `.env` generado y añade tu clave de API de Google Gemini:

```env
GEMINI_API_KEY=tu_clave_aqui
```

## 🎮 Cómo Ejecutar

### Linux/macOS
```bash
./run.sh  # (Si existe) o
source venv/bin/activate && python3 run.py
```

### Windows
```batch
run.bat
```

## 🛠️ Comandos Especiales

Dentro del chatbot puedes usar:
* `1001`: Corregir la última respuesta del sistema.
* `historial`: Ver las últimas conversaciones.
* `stats`: Ver estadísticas de aprendizaje.
* `export`: Exportar la base de conocimiento a JSON.
* `salir`: Cerrar la sesión.

## 📂 Estructura del Proyecto

* `src/`: Código fuente del motor de IA y base de datos.
* `data/`: Almacenamiento persistente (SQLite y logs).
* `run.py`: Script de inicio rápido.
* `setup.sh`: Automatización de portabilidad.
