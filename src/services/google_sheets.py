import os
import json
from datetime import datetime
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

class GoogleSheetsService:
    def __init__(self):
        self.SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
        self.service = None
        self.spreadsheet_id = None
        
    def authenticate(self, credentials_path='credentials.json', token_path='token.json'):
        """Autenticar con Google Sheets API"""
        creds = None
        
        # Cargar token existente si existe
        if os.path.exists(token_path):
            creds = Credentials.from_authorized_user_file(token_path, self.SCOPES)
        
        # Si no hay credenciales válidas, obtener nuevas
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not os.path.exists(credentials_path):
                    raise FileNotFoundError(f"Archivo de credenciales no encontrado: {credentials_path}")
                
                flow = InstalledAppFlow.from_client_secrets_file(credentials_path, self.SCOPES)
                creds = flow.run_local_server(port=0)
            
            # Guardar credenciales para la próxima ejecución
            with open(token_path, 'w') as token:
                token.write(creds.to_json())
        
        self.service = build('sheets', 'v4', credentials=creds)
        return True
    
    def set_spreadsheet_id(self, spreadsheet_id):
        """Establecer el ID del spreadsheet a usar"""
        self.spreadsheet_id = spreadsheet_id
    
    def get_all_leads(self):
        """Obtener todos los leads del spreadsheet"""
        if not self.service or not self.spreadsheet_id:
            raise Exception("Servicio no autenticado o spreadsheet_id no establecido")
        
        try:
            # Leer datos desde la fila 2 (saltando headers)
            range_name = 'Leads!A2:T'
            result = self.service.spreadsheets().values().get(
                spreadsheetId=self.spreadsheet_id,
                range=range_name
            ).execute()
            
            values = result.get('values', [])
            leads = []
            
            for i, row in enumerate(values):
                # Asegurar que la fila tenga todas las columnas
                while len(row) < 20:
                    row.append('')
                
                lead = {
                    'id': i + 1,  # ID basado en la posición
                    'nombre': row[1] if len(row) > 1 else '',
                    'telefono': row[2] if len(row) > 2 else '',
                    'email': row[3] if len(row) > 3 else '',
                    'fuente': row[4] if len(row) > 4 else '',
                    'registro': row[5] if len(row) > 5 else '',
                    'producto_interes': row[6] if len(row) > 6 else '',
                    'estado': row[7] if len(row) > 7 else '',
                    'pipeline': row[8] if len(row) > 8 else '',
                    'vendedor': row[9] if len(row) > 9 else '',
                    'comentarios': row[10] if len(row) > 10 else '',
                    'fecha_ultimo_contacto': row[11] if len(row) > 11 else '',
                    'proxima_accion': row[12] if len(row) > 12 else '',
                    'fecha_proxima_accion': row[13] if len(row) > 13 else '',
                    'conversacion': row[14] if len(row) > 14 else '',
                    'tipo_pago': row[15] if len(row) > 15 else '',
                    'monto_pendiente': row[16] if len(row) > 16 else '',
                    'comprobante': row[17] if len(row) > 17 else '',
                    'fecha_creacion': row[18] if len(row) > 18 else '',
                    'fecha_modificacion': row[19] if len(row) > 19 else ''
                }
                leads.append(lead)
            
            return leads
            
        except HttpError as error:
            print(f'Error al obtener leads: {error}')
            return []
    
    def create_lead(self, lead_data):
        """Crear un nuevo lead en el spreadsheet"""
        if not self.service or not self.spreadsheet_id:
            raise Exception("Servicio no autenticado o spreadsheet_id no establecido")
        
        try:
            # Obtener el próximo ID
            existing_leads = self.get_all_leads()
            next_id = len(existing_leads) + 1
            
            # Preparar datos del lead
            now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            values = [
                next_id,
                lead_data.get('nombre', ''),
                lead_data.get('telefono', ''),
                lead_data.get('email', ''),
                lead_data.get('fuente', ''),
                lead_data.get('registro', datetime.now().strftime('%Y-%m-%d')),
                lead_data.get('producto_interes', ''),
                lead_data.get('estado', 'Activo'),
                lead_data.get('pipeline', 'Prospección'),
                lead_data.get('vendedor', ''),
                lead_data.get('comentarios', ''),
                lead_data.get('fecha_ultimo_contacto', ''),
                lead_data.get('proxima_accion', ''),
                lead_data.get('fecha_proxima_accion', ''),
                lead_data.get('conversacion', ''),
                lead_data.get('tipo_pago', ''),
                lead_data.get('monto_pendiente', ''),
                lead_data.get('comprobante', ''),
                now,  # fecha_creacion
                now   # fecha_modificacion
            ]
            
            # Agregar al final del spreadsheet
            range_name = 'Leads!A:T'
            body = {'values': [values]}
            
            result = self.service.spreadsheets().values().append(
                spreadsheetId=self.spreadsheet_id,
                range=range_name,
                valueInputOption='USER_ENTERED',
                body=body
            ).execute()
            
            return {'success': True, 'id': next_id}
            
        except HttpError as error:
            print(f'Error al crear lead: {error}')
            return {'success': False, 'error': str(error)}
    
    def update_lead(self, lead_id, lead_data):
        """Actualizar un lead existente"""
        if not self.service or not self.spreadsheet_id:
            raise Exception("Servicio no autenticado o spreadsheet_id no establecido")
        
        try:
            # Calcular la fila (lead_id + 1 porque la fila 1 son headers)
            row_number = int(lead_id) + 1
            
            # Obtener datos actuales del lead
            current_range = f'Leads!A{row_number}:T{row_number}'
            current_result = self.service.spreadsheets().values().get(
                spreadsheetId=self.spreadsheet_id,
                range=current_range
            ).execute()
            
            current_values = current_result.get('values', [[]])[0]
            while len(current_values) < 20:
                current_values.append('')
            
            # Actualizar solo los campos proporcionados
            updated_values = current_values.copy()
            
            field_mapping = {
                'nombre': 1, 'telefono': 2, 'email': 3, 'fuente': 4,
                'registro': 5, 'producto_interes': 6, 'estado': 7,
                'pipeline': 8, 'vendedor': 9, 'comentarios': 10,
                'fecha_ultimo_contacto': 11, 'proxima_accion': 12,
                'fecha_proxima_accion': 13, 'conversacion': 14,
                'tipo_pago': 15, 'monto_pendiente': 16, 'comprobante': 17
            }
            
            for field, index in field_mapping.items():
                if field in lead_data:
                    updated_values[index] = lead_data[field]
            
            # Actualizar fecha de modificación
            updated_values[19] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            # Actualizar en el spreadsheet
            body = {'values': [updated_values]}
            result = self.service.spreadsheets().values().update(
                spreadsheetId=self.spreadsheet_id,
                range=current_range,
                valueInputOption='USER_ENTERED',
                body=body
            ).execute()
            
            return {'success': True}
            
        except HttpError as error:
            print(f'Error al actualizar lead: {error}')
            return {'success': False, 'error': str(error)}
    
    def delete_lead(self, lead_id):
        """Marcar un lead como inactivo (soft delete)"""
        return self.update_lead(lead_id, {'estado': 'Inactivo'})
    
    def get_pipeline_stats(self):
        """Obtener estadísticas del pipeline"""
        leads = self.get_all_leads()
        
        stats = {
            'Prospección': {'count': 0, 'value': 0},
            'Contacto': {'count': 0, 'value': 0},
            'Negociación': {'count': 0, 'value': 0},
            'Cierre': {'count': 0, 'value': 0}
        }
        
        for lead in leads:
            if lead['estado'] == 'Activo' and lead['pipeline'] in stats:
                stats[lead['pipeline']]['count'] += 1
                # Aquí podrías agregar lógica para calcular valores monetarios
                
        return stats
    
    def get_cobranza_data(self):
        """Obtener datos de cobranza (leads con tipo_pago = Crédito)"""
        leads = self.get_all_leads()
        
        cobranza_leads = []
        for lead in leads:
            if lead['tipo_pago'] == 'Crédito' and lead['monto_pendiente']:
                try:
                    monto_pendiente = float(lead['monto_pendiente']) if lead['monto_pendiente'] else 0
                    if monto_pendiente > 0:
                        cobranza_leads.append(lead)
                except ValueError:
                    continue
                    
        return cobranza_leads

# Instancia global del servicio
sheets_service = GoogleSheetsService()

