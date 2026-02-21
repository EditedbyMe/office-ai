# -*- coding: utf-8 -*-
"""
Configuración centralizada del sistema OfficeAI
"""
import os
from pathlib import Path
from typing import Final
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Rutas del proyecto
BASE_DIR: Final[Path] = Path(__file__).parent.parent
DATA_DIR: Final[Path] = BASE_DIR / "data"
LOGS_DIR: Final[Path] = DATA_DIR / "logs"
DB_PATH: Final[Path] = DATA_DIR / "office_ai.db"

# Crear directorios si no existen
DATA_DIR.mkdir(exist_ok=True)
LOGS_DIR.mkdir(exist_ok=True)

# Configuración de la personalidad del bot
PERSONALITY: Final[dict] = {
    "name": "OfficeAI",
    "style": "amigable, profesional y reflexivo",
    "intro": "Soy OfficeAI 🤖, tu asistente experto en Office y conversación general. Tengo búsqueda web en tiempo real y guardo historial."
}

# Frases de corrección
CORRECTION_PHRASES: Final[list] = ["1001"]

# Configuración de búsqueda
FUZZY_CUTOFF: Final[float] = 0.7
MIN_POINTS_FOR_PRIORITY: Final[int] = 10
WEB_SEARCH_RESULTS: Final[int] = 4
CACHE_TTL_HOURS: Final[int] = 24

# Configuración de Q-Learning
Q_LEARNING_RATE: Final[float] = 0.1
Q_DISCOUNT_FACTOR: Final[float] = 0.9
Q_INITIAL_VALUE: Final[float] = 0.0

# Configuración de logging
LOG_LEVEL: Final[str] = os.getenv("LOG_LEVEL", "INFO")
LOG_FORMAT: Final[str] = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_MAX_BYTES: Final[int] = 10 * 1024 * 1024  # 10MB
LOG_BACKUP_COUNT: Final[int] = 5

# Síntesis de resultados web
MAX_CONTEXT_TURNS: Final[int] = 5  # Últimas N interacciones para contexto
MIN_RESULT_LENGTH: Final[int] = 50  # Longitud mínima de resultado útil
MAX_SYNTHESIS_LENGTH: Final[int] = 600  # Longitud máxima de respuesta sintetizada (aumentada para Gemini)
AUTO_SAVE_WEB_ANSWERS: Final[bool] = True  # Guardar respuestas web automáticamente

# Configuración de Gemini
GEMINI_API_KEY: Final[str] = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL: Final[str] = "gemini-flash-latest"  # Cambiado a flash-latest para mejor estabilidad de cuota
USE_GEMINI_SEARCH: Final[bool] = True if GEMINI_API_KEY else False

# Datos iniciales para base de conocimiento
INITIAL_DATA: Final[dict] = {
    "base_office": {
        "que es microsoft office": ["Microsoft Office es una suite de aplicaciones de productividad desarrollada por Microsoft. Incluye Word, Excel, PowerPoint, Outlook y Access, entre otras."],
        "para que sirve microsoft office": ["Sirve para crear documentos, hojas de cálculo, presentaciones, gestionar correos y bases de datos."],
        "que aplicaciones incluye microsoft office": ["Incluye Word, Excel, PowerPoint, Outlook, Access y otras aplicaciones según la versión."],
        "diferencia entre office 365 y office 2021": ["Office 365 es una suscripción con actualizaciones continuas. Office 2021 es una licencia de pago único sin nuevas funciones futuras."]
    },
    "access": {
        "que es access": ["Access es un gestor de bases de datos relacional de Microsoft."],
        "para que sirve access": ["Sirve para crear y gestionar bases de datos con tablas, consultas y formularios."],
        "que es una clave primaria": ["Una clave primaria identifica de forma única cada registro de una tabla."],
        "que es una tabla en access": ["Una tabla almacena datos organizados en filas y columnas."]
    },
    "word": {
        "que es word": ["Word es un procesador de textos para crear documentos como cartas, informes o trabajos."],
        "para que sirve word": ["Sirve para redactar, editar y dar formato a documentos de texto."],
        "que son los estilos en word": ["Los estilos permiten aplicar formatos predefinidos para títulos y texto."],
        "como hacer un indice en word": ["Se crea usando estilos de título y la opción Referencias > Tabla de contenido."]
    },
    "excel": {
        "que es excel": ["Excel es una hoja de cálculo que permite realizar cálculos, análisis de datos y gráficos."],
        "para que sirve excel": ["Sirve para trabajar con datos numéricos, crear tablas, fórmulas, gráficos y tablas dinámicas."],
        "que es una celda en excel": ["Una celda es la intersección entre una fila y una columna donde se introducen datos."],
        "que es una formula en excel": ["Una fórmula es una expresión que realiza cálculos y siempre empieza por el signo ="],
        "que es una tabla dinamica": ["Una tabla dinámica permite resumir y analizar grandes cantidades de datos fácilmente."],
        "que es buscarv": ["BUSCARV es una función que busca un valor en la primera columna de una tabla."]
    },
    "powerpoint": {
        "que es powerpoint": ["PowerPoint es una herramienta para crear presentaciones con diapositivas."],
        "para que sirve powerpoint": ["Sirve para presentar información de forma visual mediante texto, imágenes y gráficos."],
        "que es una diapositiva": ["Es cada una de las páginas que componen una presentación."],
        "atajos de powerpoint": ["F5 inicia la presentación. Ctrl + M crea una nueva diapositiva."]
    },
    "outlook": {
        "que es outlook": ["Outlook es una aplicación para gestionar correo electrónico, calendarios y contactos."],
        "para que sirve outlook": ["Sirve para enviar y recibir correos y organizar citas y tareas."],
        "que son las reglas en outlook": ["Las reglas automatizan acciones sobre los correos entrantes."]
    },
    "general": {
        "hola": ["¡Hola! ¿Cómo estás? 😄"],
        "buenos dias": ["¡Buenos días! Espero que tengas un día excelente."],
        "buenas tardes": ["¡Buenas tardes! ¿Cómo va tu día hasta ahora?"],
        "buenas noches": ["¡Buenas noches! Espero que hayas tenido un buen día."],
        "como estas": ["Estoy funcionando perfectamente, gracias por preguntar. ¿Y tú?"],
        "que tal": ["Todo bien, gracias. ¿Y tú cómo te encuentras?"],
        "que es python": ["Python es un lenguaje de programación muy popular, fácil de aprender y usado en desarrollo web, ciencia de datos e inteligencia artificial."],
        "que es inteligencia artificial": ["La inteligencia artificial es la simulación de procesos inteligentes por máquinas y programas."],
        "que es la tierra": ["La Tierra es el tercer planeta del sistema solar y el único conocido que tiene vida."],
        "que es la luna": ["La Luna es el satélite natural de la Tierra y controla, entre otras cosas, las mareas."],
        "cuantos continentes hay": ["Hay siete continentes: África, América, Asia, Europa, Oceanía y Antártida."],
        "cual es el oceano mas grande": ["El océano Pacífico es el más grande del planeta."],
        "quien fue albert einstein": ["Albert Einstein fue un físico alemán, famoso por la teoría de la relatividad y sus contribuciones a la física moderna."],
        "cual es la capital de francia": ["La capital de Francia es París."],
        "cual es la capital de españa": ["La capital de España es Madrid."]
    }
}
