# -*- coding: utf-8 -*-
"""
Script de prueba para Gemini Search Grounding
"""
import sys
import os
from pathlib import Path

# Añadir src al path
sys.path.append(str(Path(__file__).parent / "src"))

from gemini_engine import GeminiEngine
from config import GEMINI_API_KEY

def test_gemini():
    print("--- Testing Gemini Search Grounding ---")
    if not GEMINI_API_KEY:
        print("❌ Error: GEMINI_API_KEY no encontrada en el entorno.")
        print("Asegúrate de tener un archivo .env con la clave.")
        return

    engine = GeminiEngine()
    
    # Prueba 1: Búsqueda sobre Office (actual)
    question = "¿Cuál es la última versión estable de Microsoft Office y qué novedades incluye?"
    print(f"\nPregunta: {question}")
    
    answer, sources = engine.search_and_synthesize(question)
    
    if answer:
        print(f"\n✅ Respuesta de Gemini:\n{answer}")
        if sources:
            print("\nFuentes encontradas:")
            for s in sources:
                print(f"- {s}")
        else:
            print("\n⚠️ No se detectaron fuentes explícitas en los metadatos.")
    else:
        print("\n❌ Error: No se obtuvo respuesta de Gemini.")

    # Prueba 2: Búsqueda sobre algo muy reciente
    question = "¿Qué novedades tecnológicas importantes han ocurrido en la última semana?"
    print(f"\nPregunta: {question}")
    
    answer, sources = engine.search_and_synthesize(question)
    
    if answer:
        print(f"\n✅ Respuesta de Gemini (Actualidad):\n{answer[:300]}...")
    else:
        print("\n❌ Error: No se obtuvo respuesta de actualidad.")

if __name__ == "__main__":
    test_gemini()
