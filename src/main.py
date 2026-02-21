# -*- coding: utf-8 -*-
"""
OfficeAI - Chatbot Inteligente con Búsqueda Web
Versión Refactorizada 2.0
"""
import webbrowser
import time

from config import PERSONALITY, DATA_DIR, DB_PATH
from database import Database
from ai_engine import AIEngine
from utils import setup_logging, print_banner, print_stats


def handle_correction(ai):
    """Maneja una corrección del usuario con opciones avanzadas"""
    if not ai.last_question:
        print(f"\n{PERSONALITY['name']}: No hay pregunta previa para corregir.")
        return
    
    print(f"\n{PERSONALITY['name']}: ¿Cómo prefieres corregir la información?")
    print("  1. Escribir la respuesta a mano")
    print("  2. Proporcionar un link (URL) para que aprenda")
    print("  3. Solo borrar la respuesta anterior (sin añadir nueva)")
    
    try:
        choice = input("\nElige una opción (1/2/3): ").strip()
        
        if choice == "1":
            new_answer = input("\nEscribe la respuesta correcta:\n").strip()
            if new_answer:
                ai.handle_user_correction(new_answer)
                print(f"\n{PERSONALITY['name']}: Gracias, he aprendido la corrección manual.")
        elif choice == "2":
            url = input("\nPega el link de la página web:\n").strip()
            if url:
                print(f"\n{PERSONALITY['name']}: Procesando link... esto puede tardar un momento.")
                if ai.learn_from_url(url):
                    print(f"\n{PERSONALITY['name']}: ¡Hecho! He extraído y aprendido la información del link.")
                else:
                    print(f"\n{PERSONALITY['name']}: Lo siento, no pude extraer información útil de ese link.")
        elif choice == "3":
            print(f"\n{PERSONALITY['name']}: Entendido, la interacción ha sido borrada.")
        else:
            print(f"\n{PERSONALITY['name']}: Opción no válida.")
    except KeyboardInterrupt:
        print("\nOperación cancelada.")


def handle_single_answer(ai, question, answer):
    """Maneja una respuesta única"""
    if not ai.should_ask_feedback(question):
        print(f"\n{PERSONALITY['name']}: {answer}")
        ai.add_to_context(question, answer)
        return False

    print(f"\n{PERSONALITY['name']}: {answer}")
    
    # Añadir al contexto conversacional
    ai.add_to_context(question, answer)
    
    print("\nOpciones de feedback:")
    print("  1. La respuesta es correcta")
    print("  2. La respuesta es incorrecta (escribir corrección)")
    print("  3. No quiero ayudar (evitar preguntar esta sesión)")
    
    choice = input("\nElige una opción (1/2/3): ").strip()
    
    if choice == "1":
        ai.db.update_q_value(question, answer, +2.0)
        print(f"{PERSONALITY['name']}: ¡Perfecto! Aumentaré la confianza en esta respuesta.")
    elif choice == "2":
        new_answer = input("Escribe la respuesta correcta:\n").strip()
        if new_answer:
            ai.handle_user_correction(new_answer, question)
    elif choice == "3":
        ai.skip_question_feedback(question)
        print(f"{PERSONALITY['name']}: Entendido, no te preguntaré más por esta cuestión hoy.")
    
    return False


def handle_multiple_answers(ai, question, answers):
    """Maneja múltiples respuestas posibles"""
    print(f"\n{PERSONALITY['name']}: Por favor, indica cuál de las respuestas proporcionadas es la mejor de todas:")
    
    for idx, ans_dict in enumerate(answers, 1):
        ans = ans_dict['answer']
        print(f"{idx}. {ans}")
    
    print(f"{len(answers) + 1}. Ninguna es correcta / Escribir nueva")
    print(f"{len(answers) + 2}. No quiero ayudar (evitar preguntar esta sesión)")
    
    choice = input(f"\nElige una opción (1-{len(answers) + 2}): ").strip()
    
    if choice.isdigit():
        c_int = int(choice)
        if 1 <= c_int <= len(answers):
            selected = answers[c_int-1]['answer']
            ai.handle_answer_selection(question, selected, is_correct=True)
            ai.add_to_context(question, selected)
            print(f"\n{PERSONALITY['name']}: Perfecto, usaré esta respuesta más a menudo.")
            return True
        elif c_int == len(answers) + 1:
            new_answer = input("Escribe la respuesta correcta:\n").strip()
            if new_answer:
                ai.handle_user_correction(new_answer, question)
            return True
        elif c_int == len(answers) + 2:
            ai.skip_question_feedback(question)
            print(f"{PERSONALITY['name']}: Entendido, no te pediré ayuda con esta pregunta hoy.")
            # Mostrar la primera respuesta al menos
            ai.add_to_context(question, answers[0]['answer'])
            return True
    
    return False


def handle_web_search(ai, question):
    """Maneja búsqueda web cuando no hay respuesta local"""
    print(f"\n{PERSONALITY['name']}: Analizando la pregunta, espera un momento...")
    
    synthesis, sources = ai.search_web_and_process(question)
    
    if synthesis:
        # Mostrar respuesta sintetizada automáticamente
        print(f"\n{PERSONALITY['name']}: {synthesis}\n")
        
        # Añadir al contexto conversacional
        ai.add_to_context(question, synthesis)
        
        # Mostrar fuentes
        if sources:
            print(f"📚 Información extraída de {len(sources)} fuente(s) web")
        
        # Preguntar si quiere ver las fuentes detalladas
        if sources:
            show_sources = input("\n¿Quieres ver las fuentes detalladas? (si/no): ").strip().lower()
            if show_sources in ["si", "sí", "s", "yes", "y"]:
                print("\n🔗 Fuentes:")
                for i, url in enumerate(sources, 1):
                    print(f"   {i}. {url}")
                
                # Opción de abrir enlace
                open_link = input("\n¿Abrir algún enlace? (1/2/3 o no): ").strip()
                if open_link.isdigit() and 1 <= int(open_link) <= len(sources):
                    webbrowser.open(sources[int(open_link)-1])
                    print("✓ Abriendo en tu navegador...")
    else:
        print(f"{PERSONALITY['name']}: Lo siento, la búsqueda no devolvió resultados útiles.")


def show_history(db):
    """Muestra el historial de conversaciones"""
    history = db.get_history(limit=20)
    
    if not history:
        print("\nNo hay historial aún.")
        return
    
    print("\n" + "="*80)
    print("HISTORIAL DE CONVERSACIONES (últimas 20)")
    print("="*80)
    
    for entry in reversed(history):
        timestamp = entry['timestamp']
        question = entry['question']
        answer = entry['answer']
        source = entry['source']
        was_correct = entry.get('was_correct')
        
        print(f"\n[{timestamp}]")
        print(f"Tú: {question}")
        print(f"{PERSONALITY['name']}: {answer}")
        print(f"Fuente: {source}", end="")
        
        if was_correct is not None:
            status = "✓ Correcta" if was_correct else "✗ Incorrecta"
            print(f" | {status}")
        else:
            print()
    
    print("\n" + "="*80)


def main():
    """Función principal del chatbot"""
    logger = setup_logging()
    logger.info("Iniciando OfficeAI v2.0")
    
    print_banner(PERSONALITY)
    time.sleep(2)  # Pequeño retraso para que se aprecie la presentación
    
    try:
        db = Database()
        ai = AIEngine(db)
        
        logger.info("Componentes inicializados correctamente")
        print(f"Base de datos: {DB_PATH}")
        print(f"Conocimiento cargado: {db.get_knowledge_count()} entradas")
        print("\nComandos especiales:")
        print("  '1001' - Corregir última respuesta del sistema")
        print("  'historial' - Ver conversaciones anteriores")
        print("  'stats' - Ver estadísticas del sistema")
        print("  'export' - Exportar base de datos a JSON")
        print("  'contexto' - Ver contexto conversacional actual")
        print("  'salir' - Terminar programa")
        print("="*80)
        
    except Exception as e:
        print(f"ERROR CRÍTICO: No se pudo inicializar el sistema: {e}")
        logger.error(f"Error de inicialización: {e}")
        return
    
    while True:
        try:
            q = input("\nTú: ").strip()
            
            if not q:
                continue
            
            if q.lower() == "salir":
                print(f"\n{PERSONALITY['name']}: ¡Hasta luego! Que tengas un excelente día.")
                logger.info("Usuario cerró sesión")
                break
            
            if q.lower() == "historial":
                show_history(db)
                continue
            
            if q.lower() == "stats":
                print_stats(ai.get_stats())
                continue
            
            if q.lower() == "export":
                export_path = DATA_DIR / "backup.json"
                if db.export_to_json(str(export_path)):
                    print(f"✓ Base de datos exportada a: {export_path}")
                else:
                    print("✗ Error al exportar base de datos")
                continue
            
            if q.lower() == "contexto":
                context = ai.get_context_summary()
                if context:
                    print(f"\n📝 Contexto conversacional actual:")
                    print(context)
                else:
                    print("\n📝 No hay contexto conversacional aún.")
                continue
            
            if q == "1001" or (ai.is_correction(q) and ai.last_question):
                result = ai.forget_last_interaction()
                if "No tengo nada" not in result:
                    handle_correction(ai)
                else:
                    print(f"\n{PERSONALITY['name']}: {result}")
                continue
            
            answer, source = ai.process_question(q)
            
            if source == 'local':
                if handle_single_answer(ai, q, answer):
                    alt_answer = input("Escribe la respuesta alternativa:\n").strip()
                    if alt_answer:
                        ai.add_alternative_answer(q, alt_answer)
                        print(f"{PERSONALITY['name']}: Alternativa añadida correctamente.")
            
            elif source == 'local_multi':
                handle_multiple_answers(ai, q, answer)
            
            elif source == 'meta':
                print(f"{PERSONALITY['name']}: {answer}")
            
            elif source == 'conversational':
                print(f"{PERSONALITY['name']}: {answer}")
                # Añadir al contexto también para mantener el hilo
                ai.add_to_context(q, answer)

            elif source == 'unknown':
                handle_web_search(ai, q)
            
        except KeyboardInterrupt:
            print(f"\n\n{PERSONALITY['name']}: Sesión interrumpida. ¡Hasta pronto!")
            logger.info("Sesión interrumpida por usuario (Ctrl+C)")
            break
        
        except Exception as e:
            print(f"\n{PERSONALITY['name']}: Lo siento, ocurrió un error inesperado.")
            logger.error(f"Error en loop principal: {e}", exc_info=True)
            continue


if __name__ == "__main__":
    main()