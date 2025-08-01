from flask import Blueprint, jsonify

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/dashboard/metrics', methods=['GET'])
def get_dashboard_metrics():
    """Métricas generales para el dashboard"""
    return jsonify({
        "totalLeads": 128,
        "convertedLeads": 48,
        "pipelineProgress": 72
    })
