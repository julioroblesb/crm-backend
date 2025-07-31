from flask import Blueprint, request, jsonify
from src.services.google_sheets import sheets_service   # ← ruta correcta

leads_bp = Blueprint('leads', __name__)

# ------------------------- CRUD Leads ------------------------- #

@leads_bp.route('/leads', methods=['GET'])
def get_leads():
    """Obtener todos los leads"""
    try:
        leads = sheets_service.get_all_leads()
        return jsonify({"success": True, "data": leads, "count": len(leads)})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@leads_bp.route('/leads', methods=['POST'])
def create_lead():
    """Crear un nuevo lead"""
    try:
        data = request.get_json()

        # Validar campos requeridos
        for field in ('nombre', 'telefono'):
            if not data.get(field):
                return jsonify({"success": False,
                                "error": f'Campo requerido: {field}'}), 400

        result = sheets_service.create_lead(data)
        status = 201 if result.get('success') else 500
        return jsonify(result), status

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@leads_bp.route('/leads/<int:lead_id>', methods=['PUT'])
def update_lead(lead_id):
    """Actualizar un lead existente"""
    try:
        data = request.get_json()
        result = sheets_service.update_lead(lead_id, data)
        status = 200 if result.get('success') else 500
        return jsonify(result), status
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@leads_bp.route('/leads/<int:lead_id>', methods=['DELETE'])
def delete_lead(lead_id):
    """Marcar un lead como inactivo"""
    try:
        result = sheets_service.delete_lead(lead_id)
        status = 200 if result.get('success') else 500
        return jsonify(result), status
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@leads_bp.route('/leads/<int:lead_id>', methods=['GET'])
def get_lead(lead_id):
    """Obtener un lead específico"""
    try:
        leads = sheets_service.get_all_leads()
        lead = next((l for l in leads if l['id'] == lead_id), None)
        if lead:
            return jsonify({"success": True, "data": lead})
        return jsonify({"success": False, "error": "Lead no encontrado"}), 404
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

# ----------------------- Gestión de Opciones --------------------- #

@leads_bp.route('/options', methods=['GET'])
def get_options():
    """Obtener todas las opciones disponibles para los desplegables"""
    try:
        options = sheets_service.get_all_options()
        return jsonify({"success": True, "data": options})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@leads_bp.route('/options/<field>', methods=['GET'])
def get_field_options(field):
    """Obtener opciones para un campo específico"""
    try:
        if field not in ['fuente', 'pipeline', 'estado', 'vendedor']:
            return jsonify({"success": False, "error": "Campo no válido"}), 400
        
        options = sheets_service.get_field_options(field)
        return jsonify({"success": True, "data": options})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@leads_bp.route('/options/<field>', methods=['POST'])
def add_option(field):
    """Agregar una nueva opción a un campo"""
    try:
        if field not in ['fuente', 'pipeline', 'estado', 'vendedor']:
            return jsonify({"success": False, "error": "Campo no válido"}), 400
        
        data = request.get_json()
        option = data.get('option')
        
        if not option:
            return jsonify({"success": False, "error": "Opción requerida"}), 400
        
        result = sheets_service.add_option(field, option)
        status = 201 if result.get('success') else 500
        return jsonify(result), status
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@leads_bp.route('/options/<field>/<option>', methods=['PUT'])
def update_option(field, option):
    """Actualizar una opción existente"""
    try:
        if field not in ['fuente', 'pipeline', 'estado', 'vendedor']:
            return jsonify({"success": False, "error": "Campo no válido"}), 400
        
        data = request.get_json()
        new_option = data.get('new_option')
        
        if not new_option:
            return jsonify({"success": False, "error": "Nueva opción requerida"}), 400
        
        result = sheets_service.update_option(field, option, new_option)
        status = 200 if result.get('success') else 500
        return jsonify(result), status
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@leads_bp.route('/options/<field>/<option>', methods=['DELETE'])
def delete_option(field, option):
    """Eliminar una opción"""
    try:
        if field not in ['fuente', 'pipeline', 'estado', 'vendedor']:
            return jsonify({"success": False, "error": "Campo no válido"}), 400
        
        result = sheets_service.delete_option(field, option)
        status = 200 if result.get('success') else 500
        return jsonify(result), status
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

# ----------------------- Métricas & Otros --------------------- #

@leads_bp.route('/pipeline/stats', methods=['GET'])
def get_pipeline_stats():
    try:
        stats = sheets_service.get_pipeline_stats()
        return jsonify({"success": True, "data": stats})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@leads_bp.route('/cobranza', methods=['GET'])
def get_cobranza():
    try:
        data = sheets_service.get_cobranza_data()
        return jsonify({"success": True, "data": data, "count": len(data)})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@leads_bp.route('/dashboard/metrics', methods=['GET'])
def get_dashboard_metrics():
    """Métricas generales para el dashboard"""
    try:
        leads = sheets_service.get_all_leads()
        activos = [l for l in leads if l['estado'] == 'Activo']

        total = len(activos)
        pipeline = {}
        fuente = {}
        tareas = []

        for lead in activos:
            pipeline[lead['pipeline']] = pipeline.get(lead['pipeline'], 0) + 1
            fuente[lead['fuente']] = fuente.get(lead['fuente'], 0) + 1
            if lead['fecha_proxima_accion'] and lead['proxima_accion']:
                tareas.append({
                    "lead_id": lead['id'],
                    "lead_name": lead['nombre'],
                    "action": lead['proxima_accion'],
                    "date": lead['fecha_proxima_accion']
                })

        return jsonify({
            "success": True,
            "data": {
                "total_leads": total,
                "pipeline_distribution": pipeline,
                "source_distribution": fuente,
                "upcoming_tasks": tareas[:10]
            }
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

# ---------------------- Configuración API --------------------- #

@leads_bp.route('/config/spreadsheet', methods=['POST'])
def set_spreadsheet_config():
    """Configurar el ID del spreadsheet"""
    try:
        spreadsheet_id = request.get_json().get('spreadsheet_id')
        if not spreadsheet_id:
            return jsonify({"success": False,
                            "error": "spreadsheet_id es requerido"}), 400
        sheets_service.set_spreadsheet_id(spreadsheet_id)
        return jsonify({"success": True,
                        "message": "Spreadsheet configurado correctamente"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@leads_bp.route('/config/auth', methods=['POST'])
def authenticate_sheets():
    """Autenticar con Google Sheets"""
    try:
        if sheets_service.authenticate():
            return jsonify({"success": True,
                            "message": "Autenticación exitosa"})
        return jsonify({"success": False,
                        "error": "Error en la autenticación"}), 500
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

