# Configuración de Google Sheets API para CRM

## Información Recopilada de la Documentación Oficial

### Conceptos Clave de Google Sheets API

#### Estructura Básica
- **Spreadsheet**: El objeto principal que contiene múltiples hojas
- **Spreadsheet ID**: Identificador único extraído de la URL
- **Sheet**: Página o pestaña individual dentro del spreadsheet
- **Sheet ID**: Identificador numérico único para cada hoja
- **Cell**: Campo individual de datos organizados en filas y columnas

#### Notación A1
- `Sheet1!A1:B2`: Celdas en las primeras dos filas y columnas
- `Sheet1!A:A`: Toda la primera columna
- `Sheet1!1:2`: Las primeras dos filas completas
- `'Hoja con Espacios'!A1:D5`: Hoja con nombre especial

### Configuración de Autenticación OAuth2

#### Pasos de Configuración
1. **Habilitar Google Sheets API** en Google Cloud Console
2. **Configurar OAuth Consent Screen**
3. **Crear credenciales OAuth 2.0** para aplicación de escritorio
4. **Descargar archivo credentials.json**

#### Scopes Necesarios
```python
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",  # Lectura y escritura completa
    # O para solo lectura:
    # "https://www.googleapis.com/auth/spreadsheets.readonly"
]
```

#### Dependencias Python
```bash
pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib
```

### Estructura del Google Sheet para el CRM

#### Configuración de Hojas

##### Hoja 1: "Leads" (Principal)
```
Columna A: ID (Número auto-incrementable)
Columna B: NOMBRE (Texto)
Columna C: TELEFONO (Texto)
Columna D: EMAIL (Email)
Columna E: FUENTE (Lista desplegable)
Columna F: REGISTRO (Fecha)
Columna G: PRODUCTO_INTERES (Texto)
Columna H: ESTADO (Lista: Activo/Inactivo)
Columna I: PIPELINE (Lista: Prospección/Contacto/Negociación/Cierre)
Columna J: VENDEDOR (Lista desplegable)
Columna K: COMENTARIOS (Texto)
Columna L: FECHA_ULTIMO_CONTACTO (Fecha)
Columna M: PROXIMA_ACCION (Texto)
Columna N: FECHA_PROXIMA_ACCION (Fecha)
Columna O: CONVERSACION (Texto largo)
Columna P: TIPO_PAGO (Lista: Completo/Crédito)
Columna Q: MONTO_PENDIENTE (Número)
Columna R: COMPROBANTE (Lista: Con Comprobante/Sin Comprobante)
Columna S: FECHA_CREACION (Fecha/Hora)
Columna T: FECHA_MODIFICACION (Fecha/Hora)
```

##### Hoja 2: "Configuracion"
```
A1: VENDEDORES    B1: FUENTES       C1: PRODUCTOS
A2: Juan Pérez    B2: Facebook      C2: Producto A
A3: María López   B3: Instagram     C3: Producto B
A4: Carlos Ruiz   B4: WhatsApp      C4: Producto C
...               ...               ...
```

##### Hoja 3: "Logs"
```
A1: TIMESTAMP     B1: ACCION        C1: USUARIO       D1: DETALLES
A2: 2025-07-30    B2: CREATE_LEAD   C2: sistema       D2: Lead creado: Juan Pérez
...
```

### Validación de Datos en Google Sheets

#### Listas Desplegables
- **FUENTE**: Facebook, Instagram, WhatsApp, Web, Referido, Llamada Fría, Evento, Otro
- **ESTADO**: Activo, Inactivo
- **PIPELINE**: Prospección, Contacto, Negociación, Cierre
- **TIPO_PAGO**: Completo, Crédito
- **COMPROBANTE**: Con Comprobante, Sin Comprobante

#### Formato Condicional
- **Pipeline Prospección**: Fondo azul claro
- **Pipeline Contacto**: Fondo amarillo claro
- **Pipeline Negociación**: Fondo naranja claro
- **Pipeline Cierre**: Fondo verde claro
- **Estado Inactivo**: Texto gris

### Implementación de la API

#### Código Base de Autenticación
```python
import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

def authenticate_sheets():
    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json", SCOPES
            )
            creds = flow.run_local_server(port=0)
        
        with open("token.json", "w") as token:
            token.write(creds.to_json())
    
    return build("sheets", "v4", credentials=creds)
```

#### Operaciones CRUD Básicas

##### Leer Datos
```python
def get_leads(service, spreadsheet_id):
    range_name = "Leads!A2:T"  # Desde fila 2 hasta columna T
    result = service.spreadsheets().values().get(
        spreadsheetId=spreadsheet_id,
        range=range_name
    ).execute()
    return result.get('values', [])
```

##### Crear Lead
```python
def create_lead(service, spreadsheet_id, lead_data):
    range_name = "Leads!A:T"
    values = [lead_data]  # Lista con los datos del lead
    body = {'values': values}
    
    result = service.spreadsheets().values().append(
        spreadsheetId=spreadsheet_id,
        range=range_name,
        valueInputOption='USER_ENTERED',
        body=body
    ).execute()
    return result
```

##### Actualizar Lead
```python
def update_lead(service, spreadsheet_id, row_number, lead_data):
    range_name = f"Leads!A{row_number}:T{row_number}"
    values = [lead_data]
    body = {'values': values}
    
    result = service.spreadsheets().values().update(
        spreadsheetId=spreadsheet_id,
        range=range_name,
        valueInputOption='USER_ENTERED',
        body=body
    ).execute()
    return result
```

##### Eliminar Lead (Marcar como eliminado)
```python
def delete_lead(service, spreadsheet_id, row_number):
    # En lugar de eliminar, marcamos como inactivo
    range_name = f"Leads!H{row_number}"  # Columna ESTADO
    values = [["Inactivo"]]
    body = {'values': values}
    
    result = service.spreadsheets().values().update(
        spreadsheetId=spreadsheet_id,
        range=range_name,
        valueInputOption='USER_ENTERED',
        body=body
    ).execute()
    return result
```

### Consideraciones de Performance

#### Batch Operations
- Usar `batchUpdate` para múltiples operaciones
- Agrupar lecturas y escrituras
- Minimizar llamadas a la API

#### Cache Strategy
- Cache local de datos frecuentes
- Sincronización periódica en background
- Manejo de conflictos de concurrencia

#### Rate Limiting
- Google Sheets API: 100 requests/100 seconds/user
- Implementar retry con backoff exponencial
- Queue de operaciones para manejar límites

### Estructura de URL del Spreadsheet
```
https://docs.google.com/spreadsheets/d/SPREADSHEET_ID/edit#gid=SHEET_ID
```

### Configuración Inicial del Sheet

#### Headers de la Hoja Principal
```
A1: ID
B1: NOMBRE
C1: TELEFONO
D1: EMAIL
E1: FUENTE
F1: REGISTRO
G1: PRODUCTO_INTERES
H1: ESTADO
I1: PIPELINE
J1: VENDEDOR
K1: COMENTARIOS
L1: FECHA_ULTIMO_CONTACTO
M1: PROXIMA_ACCION
N1: FECHA_PROXIMA_ACCION
O1: CONVERSACION
P1: TIPO_PAGO
Q1: MONTO_PENDIENTE
R1: COMPROBANTE
S1: FECHA_CREACION
T1: FECHA_MODIFICACION
```

### Próximos Pasos
1. Crear el spreadsheet de prueba con la estructura definida
2. Configurar validaciones y formato condicional
3. Implementar el backend Flask con la integración
4. Probar operaciones CRUD básicas
5. Optimizar para performance y manejo de errores

Esta configuración asegura una integración robusta y escalable entre el CRM y Google Sheets, manteniendo la sincronización bidireccional y la integridad de los datos.

