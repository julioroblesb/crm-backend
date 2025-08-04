import os
import json
import base64
import tempfile
from datetime import datetime
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.oauth2 import service_account  


class GoogleSheetsService:
    def __init__(self):
        self.SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
        self.service = None
        self.spreadsheet_id = None

    def authenticate(self):
        """
        Autenticar con Google Sheets API leyendo las credenciales y el token
        desde variables de entorno. Si GOOGLE_TOKEN contiene un token válido,
        se utiliza directamente; si está expirado y tiene refresh token, se
        refresca; y si no existe, se abre un flujo OAuth local (sólo en entornos
        de desarrollo).
        """
        # -------------------------------------------
        # Código anterior (comentado para referencia)
        # -------------------------------------------
        """
        # 1. Leer JSON de las variables de entorno
        creds_json = os.environ.get("GOOGLE_CREDENTIALS")
        token_json = os.environ.get("GOOGLE_TOKEN")

        # Verificar que tengamos al menos las credenciales
        if not creds_json:
            raise Exception("La variable de entorno GOOGLE_CREDENTIALS no está definida")

        # 2. Escribir las credenciales en un archivo temporal
        cred_file = tempfile.NamedTemporaryFile(delete=False, suffix=".json")
        cred_file.write(creds_json.encode())
        cred_file.close()

        # 3. Si hay token, escribirlo también en un archivo temporal
        token_path = None
        if token_json:
            token_file = tempfile.NamedTemporaryFile(delete=False, suffix=".json")
            token_file.write(token_json.encode())
            token_file.close()
            token_path = token_file.name

        # 4. Cargar las credenciales del token si existe
        creds = None
        if token_path and os.path.exists(token_path):
            creds = Credentials.from_authorized_user_file(token_path, self.SCOPES)

        # 5. Si no hay credenciales válidas, refrescarlas o solicitar nuevas
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                # Refrescar token usando el refresh token
                creds.refresh(Request())
            else:
                # No hay token válido: iniciar flujo OAuth (requiere navegador)
                flow = InstalledAppFlow.from_client_secrets_file(cred_file.name, self.SCOPES)
                creds = flow.run_local_server(port=0)

            # Si quieres, puedes persistir el nuevo token en un archivo o subirlo
            # a Railway para no tener que volver a autorizar. Por simplicidad,
            # aquí no lo guardamos.

        # 6. Construir el servicio de Google Sheets
        self.service = build('sheets', 'v4', credentials=creds)
        return True
        """

        # -------------------------------------------
        # Autentica con la API de Google Sheets usando credenciales
        # decodificadas desde una variable de entorno Base64.
        # -------------------------------------------
        try:
            creds_base64 = os.environ.get("GOOGLE_CREDENTIALS_BASE64")
            if not creds_base64:
                raise ValueError(
                    "No se encontraron credenciales. "
                    "Configura la variable de entorno GOOGLE_CREDENTIALS_BASE64."
                )
            creds_json = base64.b64decode(creds_base64).decode("utf-8")
            creds_dict = json.loads(creds_json)
            creds = service_account.Credentials.from_service_account_info(
                creds_dict, scopes=self.SCOPES
            )
            self.service = build("sheets", "v4", credentials=creds)
            print("Autenticado con Google Sheets correctamente.")
        except Exception as e:
            raise Exception(f"Error al autenticar con Google Sheets: {e}")

    def set_spreadsheet_id(self, spreadsheet_id):
        """Establecer el ID del spreadsheet a usar."""
        self.spreadsheet_id = spreadsheet_id

    def get_all_leads(self):
        """Obtener todos los leads del spreadsheet."""
        if not self.service or not self.spreadsheet_id:
            raise Exception("Servicio no autenticado o spreadsheet_id no establecido")

        try:
            range_name = 'Leads!A2:T'
            result = self.service.spreadsheets().values().get(
                spreadsheetId=self.spreadsheet_id,
                range=range_name
            ).execute()

            values = result.get('values', [])

            headers = [
                "id", "nombre", "telefono", "email", "fuente", "registro",
                "producto_interes", "estado", "pipeline", "vendedor", "comentarios",
                "fecha_ultimo_contacto", "proxima_accion", "fecha_proxima_accion",
                "conversacion", "tipo_pago", "monto_pendiente", "comprobante",
                "fecha_creacion", "fecha_modificacion"
            ]

            leads = []
            for row in values:
                while len(row) < len(headers):
                    row.append('')
                lead = {headers[i]: row[i] for i in range(len(headers))}
                leads.append(lead)

            return leads

        except HttpError as error:
            print(f'Error al obtener leads: {error}')
            return []

    def create_lead(self, lead_data):
        """Crear un nuevo lead en el spreadsheet."""
        if not self.service or not self.spreadsheet_id:
            raise Exception("Servicio no autenticado o spreadsheet_id no establecido")

        try:
            existing_leads = self.get_all_leads()
            next_id = len(existing_leads) + 1

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
                now,
                now
            ]

            range_name = 'Leads!A:T'
            body = {'values': [values]}

            self.service.spreadsheets().values().append(
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
        """Actualizar un lead existente."""
        if not self.service or not self.spreadsheet_id:
            raise Exception("Servicio no autenticado o spreadsheet_id no establecido")

        try:
            row_number = int(lead_id) + 1
            current_range = f'Leads!A{row_number}:T{row_number}'
            current_result = self.service.spreadsheets().values().get(
                spreadsheetId=self.spreadsheet_id,
                range=current_range
            ).execute()

            current_values = current_result.get('values', [[]])[0]
            while len(current_values) < 20:
                current_values.append('')

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

            updated_values[19] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            body = {'values': [updated_values]}
            self.service.spreadsheets().values().update(
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
        """Marcar un lead como inactivo (soft delete)."""
        return self.update_lead(lead_id, {'estado': 'Inactivo'})

    def get_pipeline_stats(self):
        """Obtener estadísticas del pipeline."""
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

        return stats

    def get_cobranza_data(self):
        """Obtener datos de cobranza (leads con tipo_pago = Crédito)."""
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
# Asignar automáticamente el spreadsheet_id desde la variable de entorno, si existe
sheets_service.set_spreadsheet_id(os.environ.get("SPREADSHEET_ID"))
