from flask import Blueprint, request, jsonify
from src.services.google_sheets import sheets_service

leads_bp = Blueprint('leads', __name__)

@leads_bp.route('/leads', methods=['GET'])
def get_leads():
    """Obtener todos los leads"""
    try:
        leads = sheets_service.get_all_leads()
        return jsonify({
            'success': True,
            'data': leads,
            'count': len(leads)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@leads_bp.route('/leads', methods=['POST'])
def create_lead():
    """Crear un nuevo lead"""
    try:
        data = request.get_json()
        
        # Validar campos requeridos
        required_fields = ['nombre', 'telefono']
        for field in required_fields:
            if not data.get(field):
                return jsonify({
                    'success': False,
                    'error': f'Campo requerido: {field}'
                }), 400
        
        result = sheets_service.create_lead(data)
        
        if result['success']:
            return jsonify(result), 201
        else:
            return jsonify(result), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@leads_bp.route('/leads/<int:lead_id>', methods=['PUT'])
def update_lead(lead_id):
    """Actualizar un lead existente"""
    try:
        data = request.get_json()
        result = sheets_service.update_lead(lead_id, data)
        
        if result['success']:
            return jsonify(result)
        else:
            return jsonify(result), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@leads_bp.route('/leads/<int:lead_id>', methods=['DELETE'])
def delete_lead(lead_id):
    """Eliminar (marcar como inactivo) un lead"""
    try:
        result = sheets_service.delete_lead(lead_id)
        
        if result['success']:
            return jsonify(result)
        else:
            return jsonify(result), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@leads_bp.route('/leads/<int:lead_id>', methods=['GET'])
def get_lead(lead_id):
    """Obtener un lead específico"""
    try:
        leads = sheets_service.get_all_leads()
        lead = next((l for l in leads if l['id'] == lead_id), None)
        
        if lead:
            return jsonify({
                'success': True,
                'data': lead
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Lead no encontrado'
            }), 404
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@leads_bp.route('/pipeline/stats', methods=['GET'])
def get_pipeline_stats():
    """Obtener estadísticas del pipeline"""
    try:
        stats = sheets_service.get_pipeline_stats()
        return jsonify({
            'success': True,
            'data': stats
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@leads_bp.route('/cobranza', methods=['GET'])
def get_cobranza():
    """Obtener datos de cobranza"""
    try:
        cobranza_data = sheets_service.get_cobranza_data()
        return jsonify({
            'success': True,
            'data': cobranza_data,
            'count': len(cobranza_data)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@leads_bp.route('/dashboard/metrics', methods=['GET'])
def get_dashboard_metrics():
    """Obtener métricas para el dashboard"""
    try:
        leads = sheets_service.get_all_leads()
        active_leads = [l for l in leads if l['estado'] == 'Activo']
        
        # Calcular métricas básicas
        total_leads = len(active_leads)
        
        # Leads por pipeline
        pipeline_counts = {}
        for lead in active_leads:
            pipeline = lead['pipeline']
            pipeline_counts[pipeline] = pipeline_counts.get(pipeline, 0) + 1
        
        # Leads por fuente
        source_counts = {}
        for lead in active_leads:
            source = lead['fuente']
            source_counts[source] = source_counts.get(source, 0) + 1
        
        # Próximas tareas (leads con fecha_proxima_accion)
        upcoming_tasks = []
        for lead in active_leads:
            if lead['fecha_proxima_accion'] and lead['proxima_accion']:
                upcoming_tasks.append({
                    'lead_id': lead['id'],
                    'lead_name': lead['nombre'],
                    'action': lead['proxima_accion'],
                    'date': lead['fecha_proxima_accion']
                })
        
        return jsonify({
            'success': True,
            'data': {
                'total_leads': total_leads,
                'pipeline_distribution': pipeline_counts,
                'source_distribution': source_counts,
                'upcoming_tasks': upcoming_tasks[:10]  # Primeras 10 tareas
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@leads_bp.route('/config/spreadsheet', methods=['POST'])
def set_spreadsheet_config():
    """Configurar el ID del spreadsheet"""
    try:
        data = request.get_json()
        spreadsheet_id = data.get('spreadsheet_id')
        
        if not spreadsheet_id:
            return jsonify({
                'success': False,
                'error': 'spreadsheet_id es requerido'
            }), 400
        
        sheets_service.set_spreadsheet_id(spreadsheet_id)
        
        return jsonify({
            'success': True,
            'message': 'Spreadsheet configurado correctamente'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@leads_bp.route('/config/auth', methods=['POST'])
def authenticate_sheets():
    """Autenticar con Google Sheets"""
    try:
        # Por ahora, usar archivos por defecto
        # En producción, esto debería manejar la carga de archivos
        result = sheets_service.authenticate()
        
        if result:
            return jsonify({
                'success': True,
                'message': 'Autenticación exitosa'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Error en la autenticación'
            }), 500
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

