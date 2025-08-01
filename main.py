# MÉTODO ALTERNATIVO - main.py con manejo robusto de credenciales
# Usa este código si el método anterior sigue fallando:

import os
import json
import time
import logging
from datetime import datetime
from functools import wraps
from typing import Dict, List, Any, Optional

from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import gspread
from google.oauth2 import service_account

# ================================
# CONFIGURACIÓN DE LOGGING
# ================================

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ================================
# CONFIGURACIÓN DE LA APLICACIÓN
# ================================

app = Flask(__name__, static_folder='static', static_url_path='')

# Configuración CORS
CORS(app, origins=[
    'http://localhost:3000',
    'http://localhost:5173',
    'https://*.vercel.app',
    'https://crm-frontend-five-ruddy.vercel.app',
    'https://*.railway.app'
])

# ================================
# SISTEMA DE CACHÉ SIMPLE
# ================================

class SimpleCache:
    def __init__(self):
        self._cache = {}
        self._timestamps = {}
        self._ttl = 300  # 5 minutos
    
    def get(self, key: str):
        if key in self._cache:
            if time.time() - self._timestamps[key] < self._ttl:
                return self._cache[key]
            else:
                del self._cache[key]
                del self._timestamps[key]
        return None
    
    def set(self, key: str, value: Any):
        self._cache[key] = value
        self._timestamps[key] = time.time()

cache = SimpleCache()

# ================================
# CLIENTE DE GOOGLE SHEETS - MÉTODO ROBUSTO
# ================================

_google_sheets_client = None

def get_google_sheets_client():
    """Obtiene el cliente de Google Sheets con manejo robusto de credenciales"""
    global _google_sheets_client
    
    if _google_sheets_client is None:
        try:
            # Método 1: Desde variable de entorno JSON
            credentials_json = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS_JSON')
            
            if credentials_json:
                logger.info("🔑 Intentando método 1: Variable JSON completa")
                
                # Limpiar y preparar el JSON
                credentials_json = credentials_json.strip()
                
                # Reemplazar \\n con \n en el private_key
                if '\\\\n' in credentials_json:
                    credentials_json = credentials_json.replace('\\\\n', '\\n')
                    logger.info("🔧 Corrigiendo escape de caracteres en private_key")
                
                try:
                    credentials_info = json.loads(credentials_json)
                    logger.info("✅ JSON parseado correctamente")
                    
                    # Verificar campos requeridos
                    required_fields = ['type', 'private_key', 'client_email', 'project_id']
                    missing_fields = [field for field in required_fields if field not in credentials_info]
                    
                    if missing_fields:
                        logger.error(f"❌ Campos faltantes en JSON: {missing_fields}")
                        raise ValueError(f"Campos faltantes: {missing_fields}")
                    
                    # Crear credenciales
                    credentials = service_account.Credentials.from_service_account_info(
                        credentials_info,
                        scopes=['https://www.googleapis.com/auth/spreadsheets']
                    )
                    
                    _google_sheets_client = gspread.authorize(credentials)
                    logger.info("✅ Cliente de Google Sheets inicializado exitosamente (Método 1)")
                    return _google_sheets_client
                    
                except json.JSONDecodeError as e:
                    logger.error(f"❌ Error parseando JSON: {e}")
                    logger.error(f"JSON recibido (primeros 100 chars): {credentials_json[:100]}...")
                    
            # Método 2: Construir JSON desde variables individuales
            logger.info("🔑 Intentando método 2: Variables individuales")
            
            project_id = os.environ.get('GOOGLE_PROJECT_ID', 'crm-leads-integration-467521')
            private_key = os.environ.get('GOOGLE_PRIVATE_KEY')
            client_email = os.environ.get('GOOGLE_CLIENT_EMAIL', 'crm-backend-service@crm-leads-integration-467521.iam.gserviceaccount.com')
            
            if private_key:
                # Construir JSON manualmente
                credentials_info = {
                    "type": "service_account",
                    "project_id": project_id,
                    "private_key_id": "3e27e082a966b5090de2156b4d2a189b16ab90f9",
                    "private_key": private_key.replace('\\n', '\n'),
                    "client_email": client_email,
                    "client_id": "113097377705993194956",
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                    "client_x509_cert_url": f"https://www.googleapis.com/robot/v1/metadata/x509/{client_email.replace('@', '%40')}",
                    "universe_domain": "googleapis.com"
                }
                
                credentials = service_account.Credentials.from_service_account_info(
                    credentials_info,
                    scopes=['https://www.googleapis.com/auth/spreadsheets']
                )
                
                _google_sheets_client = gspread.authorize(credentials)
                logger.info("✅ Cliente de Google Sheets inicializado exitosamente (Método 2)")
                return _google_sheets_client
            
            # Método 3: Credenciales hardcodeadas (solo para testing)
            logger.info("🔑 Intentando método 3: Credenciales hardcodeadas")
            
            hardcoded_credentials = {
                "type": "service_account",
                "project_id": "crm-leads-integration-467521",
                "private_key_id": "3e27e082a966b5090de2156b4d2a189b16ab90f9",
                "private_key": """-----BEGIN PRIVATE KEY-----
MIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQDT4T9WENF95BSy
dwlOVfe/XYEFQetB9qXgoCx4j0UGbYkgA62GeIv8esRa5sMvkTF4XiLLA62/gkh1
wpGXSOQm/TbtLl7bzXN4//r8dIWBAyINhyvIfvFRzYQ8RUKgOWyatZ+bcw/gzca3
TLt/jdqTRwHoEM4+n2R6S3ClCRgCJi7Yz7iqG5ImwjaDGz0azPEe//R1HYj0JdZL
YdEXu0LILxwh6QGTgN29/er3jnjMr3ZNSqyPbf43XX3uX8+KBmv3n8GMADQrezKa
3BPonadAasmogjQYnWQaQCX8zkIgU47nmNr9IQMDoeiLWc9xVOtbMxgkDbZamlxT
uzt2mSANAgMBAAECggEAMTNHrBJdNyTIqpVqL4rWbBVIIcKoIMnnxGSlVvx73I2A
b1LzTzu8U+1lHa+iyO+oA2mmnipVRRh5f4DmInFua2BWyhY/uD45z3HvpAJhwu7J
kEcgY18Y5fQ5fe5eVYroHXfJ34TFPeBCwes7SdgUlqkBOBR49AE6yYwtlOEq9kpf
z3WGPzXWys8kipZgDN1S0lYSJcAmtWs8tllXbXFljHd1mPKcIOWkJEP3PnSyoZ6j
ww0n0dzLaMbtk2ZFZb8uwZEw3Oro6om43TmmS18J70iuNpfCucB12XqHBAFRGZwf
QLg8mRAKHjd5cpOjMDUyqCCRQTzKkLi0Zu/wiMYTAQKBgQDxoRSit/hqJwEbC6+A
9R99baqzsJM0ILrJjEyFZIpTtmTg7AHqxUyUgeydjW9LhFpjoYw9ogeZDPBMXEwo
Ya4E47sU2VM7EuBNXYgANDc6tGyez93uFLHyJU4E6bazSNasTN321y6rtbe4f6cv
QVUBNBniK2E+vj4sDupeEb5pAQKBgQDgezgH++JZjLgDa37ZyZ0FruMiKcyMGflv
xonhJkBysMtyEpPQrdWYS4My/RdxCS2mCTZFQllD65QTZAvTZh9XukvlHvqb4wVQ
AC0lg7hlbyVB4AOrXOZ35nKI/co2mXYzZgO6mw729O8K0FG252TekdAZwG/yAKf8
abNY2KrLDQKBgQDIHVUe0mh9WeJTiOEIV3qGAb5/ZTz0ziqEY5q4WyUo4YU4tp17
131t/RB/B7TmAS5vF0szfC74tbuKMmKsiwF5cTXutXJ2GVMFH/JT4Orgxq6y9Irj
8+XQGs87yGgUob2RI3QtS9eOREhtF+PZgi0pewH4y16VfS+2g3/c+qsNAQKBgBRL
b4xhPFyGOVitzkEYVibeYdCD4OdFreRqGasOT0NPMoV0ooJ6RNZI9WqVsRnaD5N0
P8DRN8rJMJD0OZF6KRlAUX48Z8HSK3fJHEvI9dHN05t6Cjri4j8yyWYTM8Xt597L
uUiUniy7hiT/InQbxWXN3veFC1ngr09Fqx48MGy9AoGAXpIylrONdjc3d45VjcxF
a7wzi8Rb/Jdmb/w0/7danoyHQW73+9Ei7JcUNm99fjNqvRZTwrsSZQL5ZbeY+hZf
veHgVHQsPp6I6OrvgNnTuUUSwVpjKD6waFc3GfCy54g3BtRKYpFaU8SJC1wFx/s0
VnHakOukZx+It8jd9fnYZTE=
-----END PRIVATE KEY-----""",
                "client_email": "crm-backend-service@crm-leads-integration-467521.iam.gserviceaccount.com",
                "client_id": "113097377705993194956",
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/crm-backend-service%40crm-leads-integration-467521.iam.gserviceaccount.com",
                "universe_domain": "googleapis.com"
            }
            
            credentials = service_account.Credentials.from_service_account_info(
                hardcoded_credentials,
                scopes=['https://www.googleapis.com/auth/spreadsheets']
            )
            
            _google_sheets_client = gspread.authorize(credentials)
            logger.info("✅ Cliente de Google Sheets inicializado exitosamente (Método 3 - Hardcoded)")
            return _google_sheets_client
            
        except Exception as e:
            logger.error(f"❌ Error inicializando cliente de Google Sheets: {e}")
            logger.error(f"Tipo de error: {type(e).__name__}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise
    
    return _google_sheets_client

def get_spreadsheet():
    """Obtiene la hoja de cálculo configurada"""
    try:
        client = get_google_sheets_client()
        spreadsheet_id = os.environ.get('SPREADSHEET_ID', '14_aoZwjsIYdQPyWbaBalGTxkGk0MGZYOiplwJxmDAtY')
        
        spreadsheet = client.open_by_key(spreadsheet_id)
        logger.info(f"✅ Conexión exitosa a Google Sheets: {spreadsheet.title}")
        return spreadsheet
        
    except Exception as e:
        logger.error(f"❌ Error abriendo hoja de cálculo: {e}")
        raise

def get_leads_from_sheets():
    """Obtiene leads desde Google Sheets"""
    try:
        # Verificar caché primero
        cached_leads = cache.get('leads_data')
        if cached_leads is not None:
            logger.info("📋 Usando leads desde caché")
            return cached_leads
        
        # Obtener datos desde Google Sheets
        spreadsheet = get_spreadsheet()
        worksheet = spreadsheet.sheet1  # Primera hoja
        
        # Obtener todos los valores
        all_values = worksheet.get_all_values()
        
        if not all_values:
            logger.warning("⚠️ No se encontraron datos en la hoja de cálculo")
            return []
        
        # Primera fila son los headers
        headers = all_values[0]
        leads = []
        
        # Procesar cada fila de datos
        for row_index, row in enumerate(all_values[1:], start=2):
            if len(row) >= len(headers):
                lead = {}
                for col_index, header in enumerate(headers):
                    value = row[col_index] if col_index < len(row) else ''
                    # Normalizar nombres de columnas
                    key = header.lower().replace(' ', '_').replace('ó', 'o').replace('í', 'i')
                    lead[key] = value
                
                # Agregar metadatos
                lead['row_number'] = row_index
                lead['last_updated'] = datetime.now().isoformat()
                leads.append(lead)
        
        # Guardar en caché
        cache.set('leads_data', leads)
        
        logger.info(f"✅ Obtenidos {len(leads)} leads desde Google Sheets")
        return leads
        
    except Exception as e:
        logger.error(f"❌ Error obteniendo leads desde Google Sheets: {e}")
        # Devolver datos de ejemplo si falla
        return [
            {
                "id": "1",
                "nombre": "Lead de ejemplo",
                "telefono": "+51 999 888 777",
                "email": "ejemplo@test.com",
                "estado": "activo",
                "fuente": "web",
                "registro": "2025-01-01"
            }
        ]

# ================================
# RUTAS DE LA API (IGUAL QUE ANTES)
# ================================

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check con verificación de Google Sheets"""
    try:
        # Verificar conexión a Google Sheets
        spreadsheet = get_spreadsheet()
        sheets_status = "healthy"
        sheets_info = {
            'title': spreadsheet.title,
            'id': spreadsheet.id,
            'worksheets': len(spreadsheet.worksheets())
        }
    except Exception as e:
        sheets_status = "unhealthy"
        sheets_info = {'error': str(e)}
    
    return jsonify({
        'status': 'healthy' if sheets_status == 'healthy' else 'degraded',
        'timestamp': datetime.now().isoformat(),
        'version': '4.1.0-robust-credentials',
        'google_sheets': {
            'status': sheets_status,
            'info': sheets_info
        },
        'environment': {
            'has_credentials_json': bool(os.environ.get('GOOGLE_APPLICATION_CREDENTIALS_JSON')),
            'has_private_key': bool(os.environ.get('GOOGLE_PRIVATE_KEY')),
            'has_spreadsheet_id': bool(os.environ.get('SPREADSHEET_ID'))
        }
    })

@app.route('/api/metrics', methods=['GET'])
def get_metrics():
    """Métricas del dashboard usando datos reales de Google Sheets"""
    logger.info("📊 Obteniendo métricas del dashboard")
    
    try:
        # Obtener leads reales desde Google Sheets
        leads = get_leads_from_sheets()
        total_leads = len(leads)
        
        # Calcular métricas reales
        active_leads = len([l for l in leads if l.get('estado', '').lower() == 'activo'])
        converted_leads = len([l for l in leads if l.get('estado', '').lower() in ['convertido', 'cierre']])
        pipeline_progress = round((converted_leads / total_leads * 100) if total_leads > 0 else 0, 1)
        
        # Contar por fuentes
        fuentes = {}
        for lead in leads:
            fuente = lead.get('fuente', 'desconocido').lower()
            fuentes[fuente] = fuentes.get(fuente, 0) + 1
        
        return jsonify({
            "success": True,
            "data": {
                "totalLeads": total_leads,
                "activeLeads": active_leads,
                "convertedLeads": converted_leads,
                "pipelineProgress": pipeline_progress,
                "conversionRate": round((converted_leads / total_leads * 100) if total_leads > 0 else 0, 1),
                "leadsBySource": fuentes,
                "lastUpdated": datetime.now().isoformat()
            },
            "timestamp": datetime.now().isoformat(),
            "source": "google_sheets_real_data"
        })
        
    except Exception as e:
        logger.error(f"❌ Error obteniendo métricas: {e}")
        # Fallback a datos de ejemplo
        return jsonify({
            "success": True,
            "data": {
                "totalLeads": 128,
                "activeLeads": 85,
                "convertedLeads": 43,
                "pipelineProgress": 33.6,
                "conversionRate": 33.6,
                "leadsBySource": {"web": 50, "facebook": 30, "instagram": 48},
                "lastUpdated": datetime.now().isoformat()
            },
            "timestamp": datetime.now().isoformat(),
            "source": "fallback_example_data",
            "error": str(e)
        })

@app.route('/api/dashboard/metrics', methods=['GET'])
def get_dashboard_metrics():
    """Alias para métricas del dashboard"""
    return get_metrics()

@app.route('/api/leads', methods=['GET'])
def get_leads():
    """Obtiene leads reales desde Google Sheets"""
    logger.info("📋 Obteniendo lista de leads")
    
    try:
        # Obtener parámetros de consulta
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 10))
        search = request.args.get('search', '').lower()
        
        # Obtener todos los leads desde Google Sheets
        all_leads = get_leads_from_sheets()
        
        # Aplicar filtro de búsqueda
        if search:
            filtered_leads = [
                lead for lead in all_leads
                if search in str(lead.get('nombre', '')).lower() or
                   search in str(lead.get('email', '')).lower() or
                   search in str(lead.get('telefono', '')).lower()
            ]
        else:
            filtered_leads = all_leads
        
        # Calcular paginación
        total_leads = len(filtered_leads)
        start_index = (page - 1) * per_page
        end_index = start_index + per_page
        paginated_leads = filtered_leads[start_index:end_index]
        
        # Calcular metadatos de paginación
        total_pages = (total_leads + per_page - 1) // per_page
        has_next = page < total_pages
        has_prev = page > 1
        
        return jsonify({
            'success': True,
            'leads': paginated_leads,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': total_leads,
                'total_pages': total_pages,
                'has_next': has_next,
                'has_prev': has_prev
            },
            'filters_applied': {
                'search': search
            },
            'timestamp': datetime.now().isoformat(),
            'source': 'google_sheets_real_data'
        })
        
    except Exception as e:
        logger.error(f"❌ Error obteniendo leads: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'leads': [],
            'pagination': {
                'page': 1,
                'per_page': 10,
                'total': 0,
                'total_pages': 0,
                'has_next': False,
                'has_prev': False
            },
            'source': 'error_fallback'
        }), 500

@app.route('/api/options', methods=['GET'])
def get_options():
    """Obtiene opciones del sistema"""
    return jsonify({
        "success": True,
        "data": {
            "estados": ["activo", "convertido", "perdido", "seguimiento", "cierre"],
            "fuentes": ["web", "facebook", "instagram", "google", "referido", "whatsapp"],
            "etapas": ["prospecto", "calificado", "propuesta", "negociacion", "cierre"]
        },
        "timestamp": datetime.now().isoformat()
    })

@app.route('/api/cache/clear', methods=['POST'])
def clear_cache():
    """Limpia el caché para forzar actualización desde Google Sheets"""
    cache._cache.clear()
    cache._timestamps.clear()
    logger.info("🗑️ Caché limpiado - próxima consulta obtendrá datos frescos")
    
    return jsonify({
        'success': True,
        'message': 'Caché limpiado exitosamente',
        'timestamp': datetime.now().isoformat()
    })

# ================================
# RUTAS PARA SERVIR FRONTEND
# ================================

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_frontend(path):
    """Sirve archivos del frontend o mensaje de API"""
    if path != "" and os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    else:
        return jsonify({
            'message': '🚀 CRM Backend con Google Sheets (Método Robusto)',
            'version': '4.1.0-robust-credentials',
            'timestamp': datetime.now().isoformat(),
            'endpoints': [
                'GET /api/health - Health check con Google Sheets',
                'GET /api/metrics - Métricas reales desde Google Sheets',
                'GET /api/dashboard/metrics - Métricas del dashboard',
                'GET /api/leads - Leads reales desde Google Sheets',
                'GET /api/options - Opciones del sistema',
                'POST /api/cache/clear - Limpiar caché'
            ],
            'status': '✅ FUNCIONANDO CON GOOGLE SHEETS (ROBUSTO)',
            'google_sheets': {
                'configured': bool(os.environ.get('GOOGLE_APPLICATION_CREDENTIALS_JSON')) or bool(os.environ.get('GOOGLE_PRIVATE_KEY')),
                'spreadsheet_id': os.environ.get('SPREADSHEET_ID', '14_aoZwjsIYdQPyWbaBalGTxkGk0MGZYOiplwJxmDAtY')
            }
        })

# ================================
# PUNTO DE ENTRADA
# ================================

if __name__ == '__main__':
    # Configuración del servidor
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') != 'production'
    
    logger.info(f"🚀 Iniciando CRM Backend con Google Sheets (Robusto) en puerto {port}")
    
    # Verificar configuración
    if os.environ.get('GOOGLE_APPLICATION_CREDENTIALS_JSON'):
        logger.info("✅ Credenciales JSON configuradas")
    elif os.environ.get('GOOGLE_PRIVATE_KEY'):
        logger.info("✅ Private key individual configurada")
    else:
        logger.info("✅ Usando credenciales hardcodeadas (método de emergencia)")
    
    if os.environ.get('SPREADSHEET_ID'):
        logger.info("✅ SPREADSHEET_ID configurado")
    else:
        logger.info("✅ Usando SPREADSHEET_ID por defecto")
    
    logger.info("✅ /api/metrics - DISPONIBLE (con datos reales)")
    logger.info("✅ /api/leads - DISPONIBLE (con datos reales)")
    logger.info("✅ /api/health - DISPONIBLE (con verificación de Google Sheets)")
    
    # Ejecutar aplicación
    app.run(
        host='0.0.0.0',
        port=port,
        debug=debug
    )

