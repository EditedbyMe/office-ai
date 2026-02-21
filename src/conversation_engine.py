# -*- coding: utf-8 -*-
"""
Motor de Conversación y Clasificación de Intenciones para OfficeAI
Maneja saludos, charla casual y detección de intenciones no técnicas.
"""
import random
import re
import unicodedata

class ConversationEngine:
    """Motor para manejar aspectos conversacionales, clasificación de intenciones y NLP"""
    
    INTENTS = {
        'GREETING': [
            r'\b(hola|hi|hello|buenos\s?dias|buenas\s?tardes|buenas\s?noches|ey|hey|que\s?tal)\b'
        ],
        'FAREWELL': [
            r'\b(adios|bye|hasta\s?luego|nos\s?vemos|chao|cerrar|salir|fin)\b'
        ],
        'IDENTIFICATION': [
            r'\b(quien\s?eres|como\s?te\s?llamas|presentate|que\s?eres)\b',
            r'\b(tu\s?nombre)\b'
        ],
        'CAPABILITIES': [
            r'\b(que\s?haces|que\s?puedes\s?hacer|ayuda|funciones|para\s?que\s?sirves)\b'
        ],
        'FEELING': [
            r'\b(como\s?estas|que\s?tal\s?estas|todo\s?bien|como\s?te\s?sientes)\b'
        ],
        'ACKNOWLEDGEMENT': [
            r'\b(gracias|ok|vale|entendido|perfecto|genial|bien)\b'
        ],
        'DEFINITION_REQUEST': [
            r'\b(que\s?es|definicion\s?de|significado\s?de|define)\b'
        ],
        'OPINION_REQUEST': [
            r'\b(que\s?opinas|tu\s?opinion)\b'
        ],
        'OFFICE_TOPIC': [
            r'\b(excel|word|powerpoint|access|outlook|office|formula|macro|tabla|celda|diapositiva|correo)\b'
        ]
    }
    
    RESPONSES = {
        'GREETING': [
            "¡Hola! ¿En qué puedo ayudarte hoy con Office?",
            "¡Buenos días! Soy tu asistente de Office. ¿Qué necesitas?",
            "¡Hola! Estoy listo para resolver tus dudas sobre Excel, Word y más."
        ],
        'FAREWELL': [
            "¡Hasta luego! Vuelve cuando tengas más dudas de Office.",
            "¡Adiós! Que tengas un excelente día productivo.",
            "Nos vemos. ¡Suerte con tus documentos!"
        ],
        'IDENTIFICATION': [
            "Soy OfficeAI, un asistente inteligente diseñado para ayudarte con Microsoft Office.",
            "Me llamo OfficeAI. Estoy aquí para resolver tus dudas sobre Excel, Word, PowerPoint y más."
        ],
        'CAPABILITIES': [
            "Puedo ayudarte con fórmulas de Excel, formatos de Word, presentaciones de PowerPoint y problemas de Outlook. ¡Pruébame!",
            "Mis capacidades incluyen: resolver dudas de Office, buscar soluciones en la web y aprender de tus correcciones."
        ],
        'FEELING': [
            "¡Estoy funcionando al 100%! Listo para ayudarte.",
            "Todo bien por aquí, procesando datos a máxima velocidad. ¿Y tú?",
            "¡Me siento muy binario hoy! 0s y 1s en perfecta armonía. ¿En qué te ayudo?"
        ],
        'ACKNOWLEDGEMENT': [
            "¡De nada! ¿Alguna otra cosa?",
            "Me alegro de haber ayudado. ¿Más preguntas?",
            "¡Genial! Aquí sigo si necesitas algo más."
        ],
        'UNKNOWN': [
            "No estoy seguro de entender eso, pero puedo buscar información si es sobre Office.",
            "Mmm, eso no me suena a un tema de Office, pero inténtalo de nuevo."
        ]
    }

    INTERNAL_DEFINITIONS = {
        'office': "Microsoft Office es una suite de aplicaciones de productividad de oficina desarrollada por Microsoft. Incluye Word, Excel, PowerPoint, Outlook, Access, entre otros.",
        'microsoft office': "Microsoft Office es una suite de aplicaciones de productividad de oficina desarrollada por Microsoft. Incluye Word, Excel, PowerPoint, Outlook, Access, entre otros.",
        'excel': "Microsoft Excel es una hoja de cálculo desarrollada por Microsoft para Windows, macOS, Android e iOS. Cuenta con herramientas de cálculo, gráficas, tablas dinámicas y un lenguaje de programación de macros llamado Visual Basic para Aplicaciones.",
        'word': "Microsoft Word es un software de procesamiento de textos. Lo creó Microsoft y está integrado en la suite Microsoft Office.",
        'powerpoint': "Microsoft PowerPoint es un programa de presentación, desarrollado por la empresa Microsoft, para sistemas operativos Windows, macOS y últimamente también para Android y iOS.",
        'access': "Microsoft Access es un sistema de gestión de bases de datos incluido en el paquete ofimático Microsoft Office. Es el sucesor de Embedded Basic.",
        'outlook': "Microsoft Outlook es un gestor de información personal de Microsoft, disponible como parte de la suite Microsoft Office. Incluye cliente de correo electrónico, calendario, agenda y control de contactos.",
    }

    STOPWORDS = set([
        "el", "la", "los", "las", "un", "una", "uns", "unas", "y", "o", "pero", "si", "no", 
        "en", "con", "por", "para", "de", "del", "a", "al", "se", "es", "son", "fue", "era",
        "que", "cual", "quien", "cuando", "donde", "como", "cuanto", "porque", "pues", "aunque",
        "mi", "tu", "su", "mis", "tus", "sus", "me", "te", "le", "nos", "os", "les",
        "yo", "tu", "el", "ella", "nosotros", "vosotros", "ellos", "ellas",
        "este", "esta", "ese", "esa", "aquel", "aquella", "esto", "eso", "aquello",
        "hola", "adios", "gracias", "favor", "buenos", "dias", "tardes", "noches",
        "dime", "sabes", "conoces", "opinas", "acerca", "sobre", "tienes", "puedes",
        "lo", "que", "sepas", "hacer", "quiero", "necesito", "gustaria", "dime", "cuenta", "explica"
    ])

    def __init__(self):
        pass

    def _normalize(self, text):
        """Normaliza el texto para facilitar la coincidencia de patrones"""
        # Eliminar acentos
        text = ''.join(c for c in unicodedata.normalize('NFD', text) if unicodedata.category(c) != 'Mn')
        return text.lower().strip()

    def tokenize(self, text):
        """Divide el texto en tokens (palabras) limpias"""
        normalized = self._normalize(text)
        # Eliminar puntuación y caracteres especiales
        clean_text = re.sub(r'[^\w\s]', '', normalized)
        return clean_text.split()

    def extract_keywords(self, text):
        """Extrae palabras clave eliminando stopwords"""
        tokens = self.tokenize(text)
        keywords = [token for token in tokens if token not in self.STOPWORDS and len(token) > 1]
        return keywords

    def refine_search_query(self, text):
        """Genera una consulta de búsqueda refinada basada en palabras clave"""
        keywords = self.extract_keywords(text)
        
        # Temas de Office para añadir contexto si no está presente
        office_map = {
            'excel': 'Microsoft Excel',
            'word': 'Microsoft Word',
            'powerpoint': 'Microsoft PowerPoint',
            'access': 'Microsoft Access',
            'outlook': 'Microsoft Outlook',
            'office': 'Microsoft Office'
        }
        
        refined_keywords = []
        for word in keywords:
            if word in office_map:
                refined_keywords.append(office_map[word])
            else:
                refined_keywords.append(word)
        
        if not refined_keywords:
            return text
            
        return " ".join(refined_keywords)

    def get_internal_definition(self, text):
        """Busca una definición interna basada en el texto"""
        normalized = self._normalize(text)
        
        # Buscar coincidencias exactas o parciales en las definiciones internas
        for key, definition in self.INTERNAL_DEFINITIONS.items():
            # Si la clave está en el texto (ej: "que es excel" -> key="excel")
            if re.search(r'\b' + re.escape(key) + r'\b', normalized):
                return definition
        return None

    def classify_intent(self, text):
        """Clasifica la intención del usuario basándose en patrones regex y keywords"""
        normalized_text = self._normalize(text)
        
        # Prioridad 0: Definiciones explícitas
        # Patrones extendidos para peticiones de información
        definition_phrases = self.INTENTS['DEFINITION_REQUEST'] + [
            r'\b(sabes\s?de|conoces\s?sobre|informacion\s?de|hablame\s?de|dime\s?de|dime\s?lo\s?que\s?sepas\s?de)\b'
        ]
        
        is_definition_request = False
        for pattern in definition_phrases:
            if re.search(pattern, normalized_text):
                is_definition_request = True
                break
        
        if is_definition_request:
            # Verificar si es sobre un tema de Office
            for topic in self.INTENTS['OFFICE_TOPIC']:
                if re.search(topic, normalized_text):
                     return 'DEFINITION_OFFICE'
            return 'DEFINITION_GENERAL'

        # Prioridad 0.5: Opiniones
        for pattern in self.INTENTS['OPINION_REQUEST']:
             if re.search(pattern, normalized_text):
                 return 'OPINION'

        # Prioridad 1: Verificar si es tema técnico de Office (para saltar charla)
        is_office_related = False
        for pattern in self.INTENTS['OFFICE_TOPIC']:
            if re.search(pattern, normalized_text):
                is_office_related = True
                break
                
        # Clasificar otras intenciones conversacionales
        for intent, patterns in self.INTENTS.items():
            if intent in ['OFFICE_TOPIC', 'DEFINITION_REQUEST', 'OPINION_REQUEST']: continue 
            
            for pattern in patterns:
                if re.search(pattern, normalized_text):
                    # Si es un saludo pero tiene mucho contenido técnico, es técnico
                    if is_office_related and len(normalized_text.split()) > 3:
                        return 'TECHNICAL'
                    return intent
        
        # Si no coincide con charla pero tiene palabras de Office, es técnico
        if is_office_related:
            return 'TECHNICAL'
            
        return 'UNKNOWN'

    def get_response(self, intent):
        """Obtiene una respuesta aleatoria para la intención dada"""
        if intent in self.RESPONSES:
            return random.choice(self.RESPONSES[intent])
        return None

    def process(self, text):
        """
        Procesa el texto y devuelve:
        (respuesta_texto, intencion, metadata_extra)
        """
        intent = self.classify_intent(text)
        
        # Manejo especial de definiciones
        if intent == 'DEFINITION_OFFICE':
            definition = self.get_internal_definition(text)
            if definition:
                return definition, 'DEFINITION_FOUND'
            else:
                return None, 'TECHNICAL' # Si no tenemos la definición interna, buscar fuera
        
        if intent == 'OPINION':
             # OfficeAI es neutral/positivo sobre Office
             if self.get_internal_definition(text): # Si es sobre Office
                 return "Como IA, no tengo opiniones personales, pero puedo decirte que es una herramienta muy potente y estándar en la industria.", 'OPINION'
             return "No tengo opiniones sobre eso.", 'OPINION'

        if intent == 'TECHNICAL':
            return None, 'TECHNICAL'
            
        if intent == 'UNKNOWN':
            return None, 'UNKNOWN'
            
        response = self.get_response(intent)
        return response, intent
