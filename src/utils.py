# -*- coding: utf-8 -*-
"""
Módulo de utilidades para OfficeAI
Funciones auxiliares, logging y helpers
"""
import logging
from logging.handlers import RotatingFileHandler
from typing import Dict

from config import LOGS_DIR, LOG_LEVEL, LOG_FORMAT, LOG_MAX_BYTES, LOG_BACKUP_COUNT


def setup_logging() -> logging.Logger:
    """Configura el sistema de logging profesional"""
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    
    logger = logging.getLogger('OfficeAI')
    logger.setLevel(getattr(logging, LOG_LEVEL))
    
    log_file = LOGS_DIR / 'office_ai.log'
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=LOG_MAX_BYTES,
        backupCount=LOG_BACKUP_COUNT,
        encoding='utf-8'
    )
    file_handler.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter(LOG_FORMAT)
    file_handler.setFormatter(file_formatter)
    
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.WARNING)
    console_formatter = logging.Formatter('%(levelname)s - %(message)s')
    console_handler.setFormatter(console_formatter)
    
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger


def print_banner(personality: Dict):
    """Imprime el banner de bienvenida"""
    banner = f"""
╔═══════════════════════════════════════════════════════════════════════════╗
║                                                                            ║
║   ██████╗ ███████╗███████╗██╗ ██████╗███████╗     █████╗ ██╗             ║
║  ██╔═══██╗██╔════╝██╔════╝██║██╔════╝██╔════╝    ██╔══██╗██║             ║
║  ██║   ██║█████╗  █████╗  ██║██║     █████╗      ███████║██║             ║
║  ██║   ██║██╔══╝  ██╔══╝  ██║██║     ██╔══╝      ██╔══██║██║             ║
║  ╚██████╔╝██║     ██║     ██║╚██████╗███████╗    ██║  ██║██║             ║
║   ╚═════╝ ╚═╝     ╚═╝     ╚═╝ ╚═════╝╚══════╝    ╚═╝  ╚═╝╚═╝             ║
║                                                                            ║
║                        Versión 2.0 - Refactorizada                        ║
║                                                                            ║
╚═══════════════════════════════════════════════════════════════════════════╝

{personality['intro']}
Estilo: {personality['style']}
"""
    print(banner)
    print("="*80)


def print_stats(stats: Dict):
    """Imprime estadísticas del sistema de forma bonita"""
    print("\n" + "="*80)
    print("ESTADÍSTICAS DEL SISTEMA")
    print("="*80)
    
    print(f"\n📚 BASE DE CONOCIMIENTO:")
    print(f"   Total de entradas: {stats.get('total_knowledge', 0)}")
    print(f"   Temas diferentes: {stats.get('total_topics', 0)}")
    
    print(f"\n💬 INTERACCIONES:")
    print(f"   Total de conversaciones: {stats.get('total_interactions', 0)}")
    
    print(f"\n🌐 BÚSQUEDAS WEB:")
    print(f"   Búsquedas realizadas: {stats.get('total_searches', 0)}")
    print(f"   Hits de caché: {stats.get('cache_hits', 0)}")
    print(f"   Tasa de caché: {stats.get('cache_hit_rate', 0):.1f}%")
    print(f"   Búsquedas cacheadas: {stats.get('cached_searches', 0)}")
    
    print("\n" + "="*80)
