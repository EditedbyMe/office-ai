#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de Prueba para OfficeAI - Búsqueda Web y Síntesis
"""
import sys
sys.path.insert(0, 'src')

from database import Database
from search import WebSearch
from ai_engine import AIEngine

def test_web_synthesis():
    """Prueba la síntesis de búsquedas web"""
    print("="*80)
    print("PRUEBA DE SÍNTESIS DE BÚSQUEDAS WEB")
    print("="*80)
    
    # Inicializar componentes
    print("\n1. Inicializando componentes...")
    db = Database()
    web_search = WebSearch(db)
    ai = AIEngine(db, web_search)
    print("✓ Componentes inicializados")
    
    # Prueba 1: Búsqueda web y síntesis
    print("\n2. Probando búsqueda web y síntesis automática...")
    question = "¿Qué es la fotosíntesis?"
    print(f"   Pregunta: {question}")
    
    synthesis, sources = ai.search_web_and_process(question)
    
    if synthesis:
        print(f"\n   ✓ SÍNTESIS GENERADA:")
        print(f"   {synthesis[:200]}...")
        print(f"\n   ✓ Fuentes: {len(sources)} URLs")
        for i, url in enumerate(sources[:2], 1):
            print(f"      {i}. {url[:60]}...")
    else:
        print("   ✗ No se generó síntesis")
        return False
    
    # Prueba 2: Verificar que se guardó en la base de datos
    print("\n3. Verificando persistencia en base de datos...")
    saved_answers = ai.find_answers(question)
    
    if saved_answers:
        print(f"   ✓ Respuesta guardada automáticamente")
        print(f"   Respuesta: {saved_answers[0]['answer'][:100]}...")
    else:
        print("   ✗ No se guardó en la base de datos")
        return False
    
    # Prueba 3: Segunda pregunta debe usar knowledge base (no web)
    print(f"\n4. Probando recuperación desde knowledge base...")
    print(f"   Haciendo la misma pregunta de nuevo...")
    
    answer, source = ai.process_question(question)
    
    if source == 'local':
        print(f"   ✓ Respuesta obtenida desde knowledge base (sin buscar en web)")
        print(f"   Fuente: {source}")
    else:
        print(f"   ✗ Debería haber usado knowledge base, pero usó: {source}")
    
    # Prueba 4: Contexto conversacional
    print("\n5. Probando contexto conversacional...")
    ai.add_to_context(question, synthesis[:100])
    context_summary = ai.get_context_summary()
    
    if context_summary:
        print(f"   ✓ Contexto conversacional funciona")
        print(f"   Contexto: {context_summary[:80]}...")
    else:
        print("   ✗ No se generó contexto")
        return False
    
    # Estadísticas finales print("\n6. Estadísticas del sistema:")
    stats = ai.get_stats()
    print(f"   Total conocimiento: {stats.get('total_knowledge', 0)}")
    print(f"   Búsquedas web: {stats.get('total_searches', 0)}")
    print(f"   Contexto: {stats.get('context_interactions', 0)} interacciones")
    
    print("\n" + "="*80)
    print("✓ TODAS LAS PRUEBAS PASARON EXITOSAMENTE")
    print("="*80)
    return True

if __name__ == "__main__":
    try:
        success = test_web_synthesis()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n✗ ERROR EN PRUEBAS: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
