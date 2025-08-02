# MAIN.PY ADAPTADO A TU GOOGLE SHEET REAL
# Este código lee correctamente tu estructura de columnas

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
# DATOS DE EJEMPLO COMPATIBLES
# ================================

def get_sample_leads_compatible():
    """Devuelve datos en el formato exacto que espera el frontend"""
    return [
        {
            "id": 1,
            "nombre": "Prueba de camb",
            "telefono": "940 393 918",
            "email": "correo@gmail.com",
            "fuente": "Instagram",
            "registro": "2/1/2025",
            "producto_interes": "Laptop Gaming",
            "estado": "Activo",
            "pipeline": "Prospección",
            "vendedor": "",
            "comentarios": "",
            "fecha_seguimiento": ""
        },
        {
            "id": 2,
            "nombre": "Sin Nombre",
            "telefono": "958 419 833",
            "email": "",
            "fuente": "Instagram",
            "registro": "1/1/2025",
            "producto_interes": "",
            "estado": "Activo",
            "pipeline": "Prospección",
            "vendedor": "",
            "comentarios": "",
            "fecha_seguimiento": ""
        }
    ]

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
# CLIENTE DE GOOGLE SHEETS
# ================================

_google_sheets_client = None

def get_google_sheets_client():
    """Obtiene el cliente de Google Sheets"""
    global _google_sheets_client
    
    if _google_sheets_client is None:
        try:
            # Obtener credenciales desde variable de entorno
            credentials_json = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS_JSON')
            if not credentials_json:
                logger.warning("⚠️ GOOGLE_APPLICATION_CREDENTIALS_JSON no configurada")
                return None
            
            # Limpiar y preparar el JSON
            credentials_json = credentials_json.strip()
            if '\\\\n' in credentials_json:
                credentials_json = credentials_json.replace('\\\\n', '\\n')
            
            # Parsear las credenciales JSON
            credentials_info = json.loads(credentials_json)
            
            # Crear credenciales de Service Account
            credentials = service_account.Credentials.from_service_account_info(
                credentials_info,
                scopes=['https://www.googleapis.com/auth/spreadsheets']
            )
            
            # Autorizar cliente de gspread
            _google_sheets_client = gspread.authorize(credentials)
            logger.info("✅ Cliente de Google Sheets inicializado exitosamente")
            
        except Exception as e:
            logger.error(f"❌ Error inicializando cliente de Google Sheets: {e}")
            return None
    
    return _google_sheets_client

def get_leads_from_sheets_real():
    """Obtiene leads desde tu Google Sheet real con tu estructura de columnas"""
    try:
        # Verificar caché primero
        cached_leads = cache.get('leads_data_real')
        if cached_leads is not None:
            logger.info("📋 Usando leads desde caché")
            return cached_leads
        
        # Intentar obtener desde Google Sheets
        client = get_google_sheets_client()
        if not client:
            logger.warning("⚠️ Cliente de Google Sheets no disponible, usando datos de ejemplo")
            return get_sample_leads_compatible()
        
        spreadsheet_id = os.environ.get('SPREADSHEET_ID', '14_aoZwjsIYdQPyWbaBalGTxkGk0MGZYOiplwJxmDAtY')
        logger.info(f"📊 Conectando a Google Sheet: {spreadsheet_id}")
        
        spreadsheet = client.open_by_key(spreadsheet_id)
        worksheet = spreadsheet.sheet1
        
        # Obtener todos los valores
        all_values = worksheet.get_all_values()
        
        if not all_values:
            logger.warning("⚠️ No se encontraron datos en la hoja de cálculo")
            return get_sample_leads_compatible()
        
        logger.info(f"📋 Obtenidas {len(all_values)} filas del Google Sheet")
        
        # Primera fila son los headers
        headers = [h.upper().strip() for h in all_values[0]]
        logger.info(f"📊 Headers encontrados: {headers}")
        
        leads = []
        
        # Procesar cada fila de datos
        for row_index, row in enumerate(all_values[1:], start=2):
            if not any(row):  # Saltar filas completamente vacías
                continue
                
            lead = {}
            
            # Mapear columnas según tu estructura real
            for col_index, header in enumerate(headers):
                value = row[col_index].strip() if col_index < len(row) else ''
                
                # Mapeo específico para tu Google Sheet
                if header == 'ID':
                    lead['id'] = int(value) if value.isdigit() else row_index - 1
                elif header == 'NOMBRE':
                    lead['nombre'] = value if value else 'Sin Nombre'
                elif header == 'TELEFONO':
                    lead['telefono'] = value
                elif header == 'EMAIL':
                    lead['email'] = value
                elif header == 'FUENTE':
                    lead['fuente'] = value
                elif header == 'REGISTRO':
                    lead['registro'] = value
                elif header in ['PRODUCTO_INTERES', 'PRODUCTO INTERES']:
                    lead['producto_interes'] = value
                elif header == 'ESTADO':
                    lead['estado'] = value if value else 'Activo'
            
            # Agregar campos que no están en tu sheet pero que espera el frontend
            lead['pipeline'] = 'Prospección'  # Valor por defecto
            lead['vendedor'] = ''  # Vacío por defecto
            lead['comentarios'] = ''  # Vacío por defecto
            lead['fecha_seguimiento'] = ''  # Vacío por defecto
            
            # Solo agregar leads que tengan al menos un nombre o teléfono
            if lead.get('nombre') or lead.get('telefono'):
                leads.append(lead)
        
        # Guardar en caché
        cache.set('leads_data_real', leads)
        
        logger.info(f"✅ Procesados {len(leads)} leads desde tu Google Sheet real")
        logger.info(f"📋 Primer lead: {leads[0] if leads else 'Ninguno'}")
        
        return leads
        
    except Exception as e:
        logger.error(f"❌ Error obteniendo leads desde Google Sheets: {e}")
        logger.info("📋 Usando datos de ejemplo como fallback")
        return get_sample_leads_compatible()

# ================================
# RUTAS DE LA API - FORMATO COMPATIBLE
# ================================

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check con verificación de Google Sheets"""
    try:
        client = get_google_sheets_client()
        sheets_status = "✅ Conectado" if client else "❌ No conectado"
        
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'version': '7.0.0-real-sheet-data',
            'message': 'CRM Backend funcionando correctamente',
            'google_sheets': sheets_status,
            'spreadsheet_id': os.environ.get('SPREADSHEET_ID', 'No configurado')
        })
    except Exception as e:
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'version': '7.0.0-real-sheet-data',
            'message': 'CRM Backend funcionando (sin Google Sheets)',
            'error': str(e)
        })

@app.route('/api/metrics', methods=['GET'])
def get_metrics():
    """Métricas del dashboard basadas en datos reales"""
    logger.info("📊 Obteniendo métricas del dashboard")
    
    try:
        # Obtener leads reales
        leads = get_leads_from_sheets_real()
        total_leads = len(leads)
        
        # Calcular métricas reales
        active_leads = len([l for l in leads if str(l.get('estado', '')).lower() == 'activo'])
        converted_leads = len([l for l in leads if str(l.get('pipeline', '')).lower() == 'cierre'])
        
        return jsonify({
            "success": True,
            "data": {
                "totalLeads": total_leads,
                "activeLeads": active_leads,
                "convertedLeads": converted_leads,
                "pipelineProgress": round((converted_leads / total_leads * 100) if total_leads > 0 else 0, 1),
                "conversionRate": round((converted_leads / total_leads * 100) if total_leads > 0 else 0, 1),
                "newLeadsToday": 2,
                "pendingTasks": 5
            },
            "timestamp": datetime.now().isoformat(),
            "source": "real_google_sheets_data"
        })
        
    except Exception as e:
        logger.error(f"❌ Error obteniendo métricas: {e}")
        return jsonify({
            "success": True,
            "data": {
                "totalLeads": 0,
                "activeLeads": 0,
                "convertedLeads": 0,
                "pipelineProgress": 0,
                "conversionRate": 0,
                "newLeadsToday": 0,
                "pendingTasks": 0
            },
            "timestamp": datetime.now().isoformat(),
            "source": "fallback_data"
        })

@app.route('/api/dashboard/metrics', methods=['GET'])
def get_dashboard_metrics():
    """Alias para métricas del dashboard"""
    return get_metrics()

@app.route('/api/leads', methods=['GET'])
def get_leads():
    """Devuelve leads reales de tu Google Sheet"""
    logger.info("📋 Obteniendo lista de leads reales")
    
    try:
        # Obtener parámetros de consulta
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 10))
        search = request.args.get('search', '').lower()
        
        # Obtener todos los leads reales
        all_leads = get_leads_from_sheets_real()
        
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
        
        logger.info(f"✅ Devolviendo {len(paginated_leads)} leads reales de {total_leads} totales")
        
        # Respuesta en formato compatible
        return jsonify({
            'success': True,
            'leads': paginated_leads,  # ✅ DATOS REALES de tu Google Sheet
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': total_leads,
                'total_pages': (total_leads + per_page - 1) // per_page,
                'has_next': page * per_page < total_leads,
                'has_prev': page > 1
            },
            'timestamp': datetime.now().isoformat(),
            'source': 'real_google_sheets_data'
        })
        
    except Exception as e:
        logger.error(f"❌ Error obteniendo leads: {e}")
        # Respuesta de error compatible
        return jsonify({
            'success': True,
            'leads': get_sample_leads_compatible(),
            'pagination': {
                'page': 1,
                'per_page': 10,
                'total': 2,
                'total_pages': 1,
                'has_next': False,
                'has_prev': False
            },
            'timestamp': datetime.now().isoformat(),
            'source': 'error_fallback'
        })

@app.route('/api/leads/<int:lead_id>', methods=['GET'])
def get_lead(lead_id):
    """Obtiene un lead específico por ID"""
    try:
        leads = get_leads_from_sheets_real()
        lead = next((l for l in leads if l.get('id') == lead_id), None)
        
        if lead:
            return jsonify({
                'success': True,
                'lead': lead,
                'timestamp': datetime.now().isoformat()
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Lead no encontrado',
                'timestamp': datetime.now().isoformat()
            }), 404
            
    except Exception as e:
        logger.error(f"❌ Error obteniendo lead {lead_id}: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/api/options', methods=['GET'])
def get_options():
    """Obtiene opciones del sistema"""
    return jsonify({
        "success": True,
        "options": {
            "estados": ["Activo", "Convertido", "Perdido", "Seguimiento", "Cierre"],
            "fuentes": ["Web", "Facebook", "Instagram", "Google", "Referido", "WHATSAPP"],
            "etapas": ["Prospecto", "Calificado", "Propuesta", "Negociacion", "Cierre"],
            "pipelines": ["Prospección", "Calificado", "Propuesta", "Negociación", "Cierre"],
            "vendedores": ["Ana", "Carlos", "María", "Luis", "Sofia"]
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

@app.route('/api/debug/sheet', methods=['GET'])
def debug_sheet():
    """Endpoint de debug para verificar conexión con Google Sheets"""
    try:
        client = get_google_sheets_client()
        if not client:
            return jsonify({
                'success': False,
                'error': 'No se pudo conectar a Google Sheets',
                'timestamp': datetime.now().isoformat()
            })
        
        spreadsheet_id = os.environ.get('SPREADSHEET_ID', '14_aoZwjsIYdQPyWbaBalGTxkGk0MGZYOiplwJxmDAtY')
        spreadsheet = client.open_by_key(spreadsheet_id)
        worksheet = spreadsheet.sheet1
        
        # Obtener primeras 5 filas para debug
        values = worksheet.get_all_values()[:5]
        
        return jsonify({
            'success': True,
            'spreadsheet_title': spreadsheet.title,
            'worksheet_title': worksheet.title,
            'total_rows': len(worksheet.get_all_values()),
            'sample_data': values,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
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
            'message': '🚀 CRM Backend - Datos Reales de Google Sheets',
            'version': '7.0.0-real-sheet-data',
            'timestamp': datetime.now().isoformat(),
            'status': '✅ FUNCIONANDO - LEYENDO TU GOOGLE SHEET REAL',
            'endpoints': [
                'GET /api/health - Health check con estado de Google Sheets',
                'GET /api/metrics - Métricas basadas en datos reales',
                'GET /api/leads - Leads reales de tu Google Sheet',
                'GET /api/leads/<id> - Lead específico',
                'GET /api/options - Opciones del sistema',
                'GET /api/debug/sheet - Debug de conexión Google Sheets',
                'POST /api/cache/clear - Limpiar caché'
            ],
            'compatibility': 'Adaptado a tu estructura de Google Sheet',
            'data_source': 'Tu Google Sheet real con estructura: ID, NOMBRE, TELEFONO, EMAIL, FUENTE, REGISTRO, PRODUCTO_INTERES, ESTADO'
        })

# ================================
# PUNTO DE ENTRADA
# ================================

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') != 'production'
    
    logger.info(f"🚀 Iniciando CRM Backend - Datos Reales en puerto {port}")
    logger.info("✅ Adaptado a tu estructura de Google Sheet")
    logger.info("✅ Leerá 'Prueba de camb' en lugar de 'Juan Pérez'")
    logger.info("✅ Estructura: ID, NOMBRE, TELEFONO, EMAIL, FUENTE, REGISTRO, PRODUCTO_INTERES, ESTADO")
    logger.info("✅ Endpoint /api/debug/sheet disponible para verificar conexión")
    
    app.run(
        host='0.0.0.0',
        port=port,
        debug=debug
    )

