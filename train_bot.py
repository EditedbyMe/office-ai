#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de Entrenamiento Masivo para OfficeAI
"""
import sys
import time
sys.path.insert(0, 'src')

from database import Database
from search import WebSearch
from ai_engine import AIEngine
from config import DB_PATH

# Lista de preguntas para entrenamiento
TRAINING_QUESTIONS = [
    # Microsoft Excel
    "¿Cómo hacer una tabla dinámica en Excel?",
    "¿Para qué sirve la función BUSCARV?",
    "¿Cómo inmovilizar paneles en Excel?",
    "¿Qué es una macro en Excel?",
    "¿Cómo calcular el promedio en Excel?",
    
    # Microsoft Word
    "¿Cómo crear un índice automático en Word?",
    "¿Cómo hacer correspondencia combinada en Word?",
    "¿Cómo poner la hoja en horizontal en Word?",
    "¿Qué es el control de cambios en Word?",
    
    # Microsoft PowerPoint
    "¿Cómo insertar un video en PowerPoint?",
    "¿Cómo hacer transiciones en PowerPoint?",
    "¿Qué es el patrón de diapositivas?",
    
    # Tecnología General
    "¿Qué es el cloud computing?",
    "¿Qué es la ciberseguridad?",
    "¿Qué es el big data?",
    "¿Qué es el aprendizaje automático?",
    "¿Qué es blockchain?",
    
    # Herramientas de Oficina
    "¿Qué es Microsoft Teams?",
    "¿Para qué sirve Outlook?",
    "¿Qué es OneDrive?",
    "¿Qué es SharePoint?",
    
    # --- FASE 2: PREGUNTAS AVANZADAS ---
    
    # Excel Avanzado
    "¿Diferencia entre BUSCARV y BUSCARX?",
    "¿Cómo proteger una hoja de Excel con contraseña?",
    "¿Cómo usar formato condicional en Excel?",
    "¿Qué son las macros en Excel y son peligrosas?",
    "¿Cómo eliminar duplicados en Excel?",
    
    # Word Avanzado
    "¿Cómo hacer un índice de contenidos en Word?",
    "¿Cómo insertar citas y bibliografía en Word?",
    "¿Cómo dividir un documento en secciones en Word?",
    "¿Cómo recuperar un archivo de Word no guardado?",
    
    # Seguridad y Tecnología
    "¿Qué es el phishing?",
    "¿Cómo crear una contraseña segura?",
    "¿Qué es la autenticación de dos factores?",
    "¿Diferencia entre HTTP y HTTPS?",
    "¿Qué es una VPN?",
    
    # Productividad
    "¿Qué es la técnica Pomodoro?",
    "¿Cómo gestionar mejor el tiempo en el trabajo?",
    "¿Qué es la metodología Kanban?",
    "¿Cómo organizar el correo electrónico eficazmente?"
]

def train_bot():
    print("="*80)
    print("INICIANDO ENTRENAMIENTO MASIVO DE OFFICE-AI")
    print("="*80)
    
    # Inicializar componentes
    db = Database()
    web = WebSearch(db)
    ai = AIEngine(db, web)
    
    initial_count = db.get_knowledge_count()
    print(f"📚 Conocimiento inicial: {initial_count} entradas")
    print(f"🎯 Objetivo: {len(TRAINING_QUESTIONS)} nuevas preguntas")
    print("-" * 80)
    
    success_count = 0
    
    for i, question in enumerate(TRAINING_QUESTIONS, 1):
        print(f"\n[{i}/{len(TRAINING_QUESTIONS)}] Procesando: '{question}'")
        
        # Verificar si ya lo sabe (para no gastar búsqueda)
        answers = ai.find_answers(question)
        if answers:
            print("   ✓ Ya conozco esta respuesta (saltando)")
            continue
            
        try:
            # Forzar búsqueda web y procesamiento
            print("   🔍 Buscando en la web...")
            synthesis, sources = ai.search_web_and_process(question)
            
            if synthesis:
                print(f"   ✅ APRENDIDO: {synthesis[:80]}...")
                print(f"   🔗 Fuente: {sources[0] if sources else 'N/A'}")
                success_count += 1
            else:
                print("   ❌ No se pudo sintetizar una respuesta")
                
            # Pequeña pausa para no saturar
            time.sleep(2)
            
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    print("\n" + "="*80)
    print("RESULTADOS DEL ENTRENAMIENTO")
    print("="*80)
    final_count = db.get_knowledge_count()
    print(f"📚 Conocimiento inicial: {initial_count}")
    print(f"📚 Conocimiento final:   {final_count}")
    print(f"📈 Crecimiento:          +{final_count - initial_count} entradas")
    print(f"✅ Éxito:                {success_count} respuestas aprendidas")
    print("="*80)

if __name__ == "__main__":
    train_bot()