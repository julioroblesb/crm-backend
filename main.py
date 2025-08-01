# CÓDIGO OPTIMIZADO COMPLETO PARA main.py
# Copia exactamente este código:

import os
import json
import time
import logging
from datetime import datetime, timedelta
from functools import wraps
from typing import Dict, List, Any, Optional

from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import gspread
from google.oauth2 import service_account
import psutil

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

# ================================
# REGISTRO DE BLUEPRINTS - SOLUCIÓN AL ERROR 404
# ================================

try:
    # Importar y registrar blueprint de leads
    from src.routes.leads import leads_bp
    app.register_blueprint(leads_bp, url_prefix='/api')
    
    logger.info("✅ Blueprint de leads registrado correctamente")
    
    # Mostrar todas las rutas para verificar
    logger.info("🔍 Rutas disponibles:")
    for rule in app.url_map.iter_rules():
        logger.info(f"  {rule.rule} -> {rule.endpoint}")
        
except Exception as e:
    logger.error(f"❌ ERROR registrando blueprints: {e}")
    import traceback
    traceback.print_exc()

# Configuración CORS mejorada
CORS(app, origins=[
    'http://localhost:3000',
    'http://localhost:5173',
    'http://127.0.0.1:3000',
    'http://127.0.0.1:5173',
    'https://*.vercel.app',
    'https://crm-frontend-five-ruddy.vercel.app',
    'https://*.netlify.app',
    'https://*.railway.app',
    'https://*.render.com'
])

# Configuración de la aplicación
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///crm.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# ================================
# SISTEMA DE CACHÉ EN MEMORIA
# ================================

class MemoryCache:
    def __init__(self):
        self._cache = {}
        self._timestamps = {}
        self._ttl = 300  # 5 minutos por defecto
    
    def get(self, key: str) -> Optional[Any]:
        if key in self._cache:
            if time.time() - self._timestamps[key] < self._ttl:
                logger.info(f"Cache HIT para clave: {key}")
                return self._cache[key]
            else:
                logger.info(f"Cache EXPIRED para clave: {key}")
                self.delete(key)
        logger.info(f"Cache MISS para clave: {key}")
        return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        self._cache[key] = value
        self._timestamps[key] = time.time()
        if ttl:
            self._ttl = ttl
        logger.info(f"Cache SET para clave: {key}")
    
    def delete(self, key: str) -> None:
        if key in self._cache:
            del self._cache[key]
            del self._timestamps[key]
            logger.info(f"Cache DELETE para clave: {key}")
    
    def clear(self) -> None:
        self._cache.clear()
        self._timestamps.clear()
        logger.info("Cache CLEARED completamente")
    
    def get_stats(self) -> Dict[str, Any]:
        return {
            'total_keys': len(self._cache),
            'cache_size_bytes': sum(len(str(v)) for v in self._cache.values()),
            'oldest_entry': min(self._timestamps.values()) if self._timestamps else None,
            'newest_entry': max(self._timestamps.values()) if self._timestamps else None
        }

# Instancia global del caché
cache = MemoryCache()

# ================================
# CLIENTE DE GOOGLE SHEETS
# ================================

_google_sheets_client = None

def get_google_sheets_client():
    """Obtiene el cliente de Google Sheets con Service Account"""
    global _google_sheets_client
    
    if _google_sheets_client is None:
        try:
            # Obtener credenciales desde variable de entorno
            credentials_json = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS_JSON')
            if not credentials_json:
                raise ValueError("GOOGLE_APPLICATION_CREDENTIALS_JSON no está configurada")
            
            # Parsear las credenciales JSON
            credentials_info = json.loads(credentials_json)
            
            # Crear credenciales de Service Account
            credentials = service_account.Credentials.from_service_account_info(
                credentials_info,
                scopes=['https://www.googleapis.com/auth/spreadsheets']
            )
            
            # Autorizar cliente de gspread
            _google_sheets_client = gspread.authorize(credentials)
            logger.info("Cliente de Google Sheets inicializado exitosamente")
            
        except Exception as e:
            logger.error(f"Error inicializando cliente de Google Sheets: {str(e)}")
            raise
    
    return _google_sheets_client

def get_spreadsheet():
    """Obtiene la hoja de cálculo configurada"""
    try:
        client = get_google_sheets_client()
        spreadsheet_id = os.environ.get('SPREADSHEET_ID')
        
        if not spreadsheet_id:
            raise ValueError("SPREADSHEET_ID no está configurada")
        
        spreadsheet = client.open_by_key(spreadsheet_id)
        logger.info(f"Hoja de cálculo abierta: {spreadsheet.title}")
        return spreadsheet
        
    except Exception as e:
        logger.error(f"Error abriendo hoja de cálculo: {str(e)}")
        raise

# ================================
# DECORADORES Y UTILIDADES
# ================================

def measure_time(func):
    """Decorador para medir tiempo de ejecución"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        execution_time = end_time - start_time
        logger.info(f"{func.__name__} ejecutado en {execution_time:.3f} segundos")
        return result
    return wrapper

def handle_errors(func):
    """Decorador para manejo centralizado de errores"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.error(f"Error en {func.__name__}: {str(e)}")
            return jsonify({
                'error': True,
                'message': f'Error interno del servidor: {str(e)}',
                'timestamp': datetime.now().isoformat()
            }), 500
    return wrapper

# ================================
# FUNCIONES DE DATOS
# ================================

@measure_time
def get_leads_from_sheets() -> List[Dict[str, Any]]:
    """Obtiene todos los leads desde Google Sheets"""
    try:
        # Verificar caché primero
        cached_leads = cache.get('leads_data')
        if cached_leads is not None:
            return cached_leads
        
        # Obtener datos desde Google Sheets
        spreadsheet = get_spreadsheet()
        worksheet = spreadsheet.sheet1  # Primera hoja
        
        # Obtener todos los valores
        all_values = worksheet.get_all_values()
        
        if not all_values:
            logger.warning("No se encontraron datos en la hoja de cálculo")
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
                    lead[header.lower().replace(' ', '_')] = value
                
                # Agregar metadatos
                lead['row_number'] = row_index
                lead['last_updated'] = datetime.now().isoformat()
                leads.append(lead)
        
        # Guardar en caché por 5 minutos
        cache.set('leads_data', leads, ttl=300)
        
        logger.info(f"Obtenidos {len(leads)} leads desde Google Sheets")
        return leads
        
    except Exception as e:
        logger.error(f"Error obteniendo leads: {str(e)}")
        raise

@measure_time
def get_system_metrics() -> Dict[str, Any]:
    """Obtiene métricas del sistema"""
    try:
        # Métricas de CPU y memoria
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        # Métricas de caché
        cache_stats = cache.get_stats()
        
        # Métricas de Google Sheets
        try:
            spreadsheet = get_spreadsheet()
            sheets_status = "connected"
            sheets_title = spreadsheet.title
        except:
            sheets_status = "disconnected"
            sheets_title = None
        
        return {
            'timestamp': datetime.now().isoformat(),
            'system': {
                'cpu_percent': cpu_percent,
                'memory_percent': memory.percent,
                'memory_available_mb': memory.available // (1024 * 1024),
                'disk_percent': disk.percent,
                'disk_free_gb': disk.free // (1024 * 1024 * 1024)
            },
            'cache': cache_stats,
            'google_sheets': {
                'status': sheets_status,
                'spreadsheet_title': sheets_title,
                'spreadsheet_id': os.environ.get('SPREADSHEET_ID', 'not_configured')
            },
            'environment': {
                'flask_env': os.environ.get('FLASK_ENV', 'production'),
                'port': os.environ.get('PORT', '5000'),
                'has_credentials': bool(os.environ.get('GOOGLE_APPLICATION_CREDENTIALS_JSON'))
            }
        }
        
    except Exception as e:
        logger.error(f"Error obteniendo métricas: {str(e)}")
        return {
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }

# ================================
# RUTAS DE LA API - FALLBACK DIRECTO
# ================================

@app.route('/api/health', methods=['GET'])
@handle_errors
def health_check():
    """Health check completo con métricas"""
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
    
    # Métricas básicas del sistema
    metrics = get_system_metrics()
    
    return jsonify({
        'status': 'healthy' if sheets_status == 'healthy' else 'degraded',
        'timestamp': datetime.now().isoformat(),
        'version': '2.0.0-optimized',
        'google_sheets': {
            'status': sheets_status,
            'info': sheets_info
        },
        'cache': cache.get_stats(),
        'system': metrics.get('system', {}),
        'uptime_seconds': time.time() - app.start_time if hasattr(app, 'start_time') else 0
    })

# RUTA FALLBACK PARA MÉTRICAS (por si los blueprints fallan)
@app.route('/api/metrics', methods=['GET'])
@handle_errors
def get_metrics_fallback():
    """Endpoint fallback para métricas del dashboard"""
    try:
        # Intentar obtener leads reales desde Google Sheets
        leads = get_leads_from_sheets()
        total_leads = len(leads)
        
        # Calcular métricas básicas
        active_leads = len([l for l in leads if l.get('estado', '').lower() == 'activo'])
        converted_leads = len([l for l in leads if l.get('estado', '').lower() == 'convertido'])
        
        return jsonify({
            "success": True,
            "data": {
                "totalLeads": total_leads,
                "activeLeads": active_leads,
                "convertedLeads": converted_leads,
                "pipelineProgress": round((converted_leads / total_leads * 100) if total_leads > 0 else 0, 1),
                "conversionRate": round((converted_leads / total_leads * 100) if total_leads > 0 else 0, 1)
            },
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"Error en métricas fallback: {e}")
        # Devolver datos de ejemplo si falla
        return jsonify({
            "success": True,
            "data": {
                "totalLeads": 128,
                "activeLeads": 80,
                "convertedLeads": 48,
                "pipelineProgress": 72,
                "conversionRate": 37.5
            },
            "timestamp": datetime.now().isoformat(),
            "note": "Datos de ejemplo - Error conectando a Google Sheets"
        })

@app.route('/api/leads', methods=['GET'])
@handle_errors
@measure_time
def get_leads():
    """Obtiene leads con paginación y filtros"""
    try:
        # Obtener parámetros de consulta
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 10))
        search = request.args.get('search', '').lower()
        stage = request.args.get('stage', '')
        status = request.args.get('status', '')
        source = request.args.get('source', '')
        
        # Obtener todos los leads
        all_leads = get_leads_from_sheets()
        
        # Aplicar filtros
        filtered_leads = all_leads
        
        if search:
            filtered_leads = [
                lead for lead in filtered_leads
                if search in str(lead.get('nombre', '')).lower() or
                   search in str(lead.get('email', '')).lower() or
                   search in str(lead.get('telefono', '')).lower()
            ]
        
        if stage:
            filtered_leads = [
                lead for lead in filtered_leads
                if str(lead.get('etapa', '')).lower() == stage.lower()
            ]
        
        if status:
            filtered_leads = [
                lead for lead in filtered_leads
                if str(lead.get('estado', '')).lower() == status.lower()
            ]
        
        if source:
            filtered_leads = [
                lead for lead in filtered_leads
                if str(lead.get('fuente', '')).lower() == source.lower()
            ]
        
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
                'search': search,
                'stage': stage,
                'status': status,
                'source': source
            },
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error en get_leads: {str(e)}")
        return jsonify({
            'error': True,
            'message': str(e),
            'leads': [],
            'pagination': {
                'page': 1,
                'per_page': 10,
                'total': 0,
                'total_pages': 0,
                'has_next': False,
                'has_prev': False
            }
        }), 500

@app.route('/api/cache/clear', methods=['POST'])
@handle_errors
def clear_cache():
    """Limpia el caché manualmente"""
    cache.clear()
    return jsonify({
        'message': 'Caché limpiado exitosamente',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/cache/stats', methods=['GET'])
@handle_errors
def get_cache_stats():
    """Obtiene estadísticas del caché"""
    stats = cache.get_stats()
    return jsonify(stats)

# ================================
# RUTAS PARA SERVIR FRONTEND
# ================================

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_frontend(path):
    """Sirve archivos del frontend"""
    if path != "" and os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    else:
        # Para SPAs, servir index.html para rutas no encontradas
        index_path = os.path.join(app.static_folder, 'index.html')
        if os.path.exists(index_path):
            return send_from_directory(app.static_folder, 'index.html')
        else:
            return jsonify({
                'message': 'CRM Backend API está funcionando',
                'version': '2.0.0-optimized',
                'timestamp': datetime.now().isoformat(),
                'endpoints': [
                    '/api/health',
                    '/api/leads',
                    '/api/metrics',
                    '/api/cache/clear',
                    '/api/cache/stats'
                ]
            })

# ================================
# INICIALIZACIÓN DE LA APLICACIÓN
# ================================

def initialize_app():
    """Inicializa la aplicación y sus componentes"""
    try:
        # Registrar tiempo de inicio
        app.start_time = time.time()
        
        # Verificar variables de entorno críticas
        required_env_vars = ['GOOGLE_APPLICATION_CREDENTIALS_JSON', 'SPREADSHEET_ID']
        missing_vars = [var for var in required_env_vars if not os.environ.get(var)]
        
        if missing_vars:
            logger.warning(f"Variables de entorno faltantes: {missing_vars}")
        else:
            logger.info("Todas las variables de entorno están configuradas")
        
        # Inicializar cliente de Google Sheets
        try:
            client = get_google_sheets_client()
            spreadsheet = get_spreadsheet()
            logger.info(f"Conexión exitosa a Google Sheets: {spreadsheet.title}")
        except Exception as e:
            logger.error(f"Error conectando a Google Sheets: {str(e)}")
        
        logger.info("Aplicación inicializada exitosamente")
        
    except Exception as e:
        logger.error(f"Error inicializando aplicación: {str(e)}")

# ================================
# PUNTO DE ENTRADA
# ================================

if __name__ == '__main__':
    # Inicializar aplicación
    initialize_app()
    
    # Configuración del servidor
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') != 'production'
    
    logger.info(f"Iniciando servidor en puerto {port}, debug={debug}")
    
    # Ejecutar aplicación
    app.run(
        host='0.0.0.0',
        port=port,
        debug=debug
    )

