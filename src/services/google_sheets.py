import os
import json
import tempfile
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

    def authenticate(self):
        """
        Autenticar con Google Sheets API leyendo las credenciales y el token
        desde variables de entorno. Si GOOGLE_TOKEN contiene un token válido,
        se utiliza directamente; si está expirado y tiene refresh token, se
        refresca; y si no existe, se abre un flujo OAuth local (sólo en entornos
        de desarrollo).
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
            leads = []

            for i, row in enumerate(values):
                # Asegurar que la fila tenga todas las columnas
                while len(row) < 20:
                    row.append('')

                lead = {
                    'id': i + 1,
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

    # ----------------------- Gestión de Opciones --------------------- #

    def get_all_options(self):
        """Obtener todas las opciones disponibles para los desplegables."""
        try:
            # Obtener opciones desde una hoja específica o extraer de los datos existentes
            leads = self.get_all_leads()
            
            options = {
                'fuente': list(set([lead['fuente'] for lead in leads if lead['fuente']])),
                'pipeline': list(set([lead['pipeline'] for lead in leads if lead['pipeline']])),
                'estado': list(set([lead['estado'] for lead in leads if lead['estado']])),
                'vendedor': list(set([lead['vendedor'] for lead in leads if lead['vendedor']]))
            }
            
            # Agregar opciones por defecto si no existen
            if not options['pipeline']:
                options['pipeline'] = ['Prospección', 'Contacto', 'Negociación', 'Cierre']
            if not options['estado']:
                options['estado'] = ['Activo', 'Inactivo']
            
            # Ordenar las opciones
            for key in options:
                options[key] = sorted(options[key])
            
            return options
        except Exception as e:
            print(f'Error al obtener opciones: {e}')
            return {
                'fuente': ['Facebook', 'Instagram', 'WhatsApp', 'Web', 'Referido'],
                'pipeline': ['Prospección', 'Contacto', 'Negociación', 'Cierre'],
                'estado': ['Activo', 'Inactivo'],
                'vendedor': ['María López', 'Carlos Ruiz', 'Ana García', 'Luis Martínez']
            }

    def get_field_options(self, field):
        """Obtener opciones para un campo específico."""
        all_options = self.get_all_options()
        return all_options.get(field, [])

    def add_option(self, field, option):
        """Agregar una nueva opción a un campo."""
        try:
            # En este caso, como las opciones se extraen dinámicamente de los datos,
            # simplemente verificamos que la opción no exista ya
            current_options = self.get_field_options(field)
            
            if option in current_options:
                return {'success': False, 'error': 'La opción ya existe'}
            
            # Para agregar una opción, podríamos crear una hoja de configuración
            # o simplemente permitir que se agregue cuando se use en un lead
            return {'success': True, 'message': f'Opción "{option}" agregada al campo {field}'}
            
        except Exception as e:
            print(f'Error al agregar opción: {e}')
            return {'success': False, 'error': str(e)}

    def update_option(self, field, old_option, new_option):
        """Actualizar una opción existente en todos los leads que la usen."""
        try:
            if not self.service or not self.spreadsheet_id:
                raise Exception("Servicio no autenticado o spreadsheet_id no establecido")

            # Mapeo de campos a columnas
            field_mapping = {
                'fuente': 4,
                'pipeline': 8,
                'estado': 7,
                'vendedor': 9
            }
            
            if field not in field_mapping:
                return {'success': False, 'error': 'Campo no válido'}
            
            column_index = field_mapping[field]
            
            # Obtener todos los datos
            range_name = 'Leads!A2:T'
            result = self.service.spreadsheets().values().get(
                spreadsheetId=self.spreadsheet_id,
                range=range_name
            ).execute()
            
            values = result.get('values', [])
            updated_rows = []
            
            # Buscar y actualizar las filas que contengan la opción antigua
            for i, row in enumerate(values):
                while len(row) < 20:
                    row.append('')
                
                if len(row) > column_index and row[column_index] == old_option:
                    row[column_index] = new_option
                    row[19] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')  # fecha_modificacion
                    
                    # Actualizar la fila específica
                    row_number = i + 2  # +2 porque empezamos en A2
                    update_range = f'Leads!A{row_number}:T{row_number}'
                    body = {'values': [row]}
                    
                    self.service.spreadsheets().values().update(
                        spreadsheetId=self.spreadsheet_id,
                        range=update_range,
                        valueInputOption='USER_ENTERED',
                        body=body
                    ).execute()
                    
                    updated_rows.append(row_number)
            
            return {
                'success': True, 
                'message': f'Opción actualizada en {len(updated_rows)} registros',
                'updated_rows': len(updated_rows)
            }
            
        except Exception as e:
            print(f'Error al actualizar opción: {e}')
            return {'success': False, 'error': str(e)}

    def delete_option(self, field, option):
        """Eliminar una opción (establecer como vacío en todos los leads que la usen)."""
        try:
            if not self.service or not self.spreadsheet_id:
                raise Exception("Servicio no autenticado o spreadsheet_id no establecido")

            # Mapeo de campos a columnas
            field_mapping = {
                'fuente': 4,
                'pipeline': 8,
                'estado': 7,
                'vendedor': 9
            }
            
            if field not in field_mapping:
                return {'success': False, 'error': 'Campo no válido'}
            
            column_index = field_mapping[field]
            
            # Obtener todos los datos
            range_name = 'Leads!A2:T'
            result = self.service.spreadsheets().values().get(
                spreadsheetId=self.spreadsheet_id,
                range=range_name
            ).execute()
            
            values = result.get('values', [])
            updated_rows = []
            
            # Buscar y limpiar las filas que contengan la opción
            for i, row in enumerate(values):
                while len(row) < 20:
                    row.append('')
                
                if len(row) > column_index and row[column_index] == option:
                    row[column_index] = ''  # Limpiar el valor
                    row[19] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')  # fecha_modificacion
                    
                    # Actualizar la fila específica
                    row_number = i + 2  # +2 porque empezamos en A2
                    update_range = f'Leads!A{row_number}:T{row_number}'
                    body = {'values': [row]}
                    
                    self.service.spreadsheets().values().update(
                        spreadsheetId=self.spreadsheet_id,
                        range=update_range,
                        valueInputOption='USER_ENTERED',
                        body=body
                    ).execute()
                    
                    updated_rows.append(row_number)
            
            return {
                'success': True, 
                'message': f'Opción eliminada de {len(updated_rows)} registros',
                'updated_rows': len(updated_rows)
            }
            
        except Exception as e:
            print(f'Error al eliminar opción: {e}')
            return {'success': False, 'error': str(e)}

# Instancia global del servicio
sheets_service = GoogleSheetsService()
# Asignar automáticamente el spreadsheet_id desde la variable de entorno, si existe
sheets_service.set_spreadsheet_id(os.environ.get("SPREADSHEET_ID"))

