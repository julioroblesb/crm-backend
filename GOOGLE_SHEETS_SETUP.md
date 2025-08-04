# Configuración de Google Sheets para CRM

## Pasos para configurar la integración con Google Sheets

### 1. Crear un proyecto en Google Cloud Console

1. Ve a [Google Cloud Console](https://console.cloud.google.com/)
2. Crea un nuevo proyecto o selecciona uno existente
3. Habilita la **Google Sheets API**:
   - Ve a "APIs y servicios" > "Biblioteca"
   - Busca "Google Sheets API"
   - Haz clic en "Habilitar"

### 2. Configurar OAuth 2.0

1. Ve a "APIs y servicios" > "Credenciales"
2. Haz clic en "Crear credenciales" > "ID de cliente de OAuth 2.0"
3. Selecciona "Aplicación de escritorio"
4. Dale un nombre a tu aplicación
5. Descarga el archivo JSON de credenciales
6. Renombra el archivo a `credentials.json`
7. Coloca el archivo en la carpeta `/home/ubuntu/crm-backend/`

### 3. Crear el Google Sheet

1. Crea un nuevo Google Sheet
2. Nombra la primera hoja como "Leads"
3. Agrega los siguientes headers en la fila 1:

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

### 4. Configurar validación de datos (Opcional pero recomendado)

#### Columna E (FUENTE):
- Selecciona la columna E
- Ve a Datos > Validación de datos
- Criterio: Lista de elementos
- Elementos: `Facebook,Instagram,WhatsApp,Web,Referido,Llamada Fría,Evento,Otro`

#### Columna H (ESTADO):
- Selecciona la columna H
- Criterio: Lista de elementos
- Elementos: `Activo,Inactivo`

#### Columna I (PIPELINE):
- Selecciona la columna I
- Criterio: Lista de elementos
- Elementos: `Prospección,Contacto,Negociación,Cierre`

#### Columna P (TIPO_PAGO):
- Selecciona la columna P
- Criterio: Lista de elementos
- Elementos: `Completo,Crédito`

#### Columna R (COMPROBANTE):
- Selecciona la columna R
- Criterio: Lista de elementos
- Elementos: `Con Comprobante,Sin Comprobante`

### 5. Obtener el ID del Spreadsheet

1. Abre tu Google Sheet
2. Copia el ID de la URL (la parte entre `/d/` y `/edit`):
   ```
   https://docs.google.com/spreadsheets/d/SPREADSHEET_ID/edit#gid=0
   ```
3. Guarda este ID, lo necesitarás para configurar el CRM

### 6. Configurar formato condicional (Opcional)

Para hacer el sheet más visual, puedes agregar formato condicional:

#### Pipeline:
- Prospección: Fondo azul claro
- Contacto: Fondo amarillo claro
- Negociación: Fondo naranja claro
- Cierre: Fondo verde claro

#### Estado:
- Inactivo: Texto gris

### 7. Permisos del Sheet

Asegúrate de que el sheet tenga los permisos correctos:
- Si es personal: Solo tú necesitas acceso
- Si es compartido: Agrega las cuentas de Google que necesiten acceso

### 8. Iniciar el backend

1. Coloca el archivo `credentials.json` en `/home/ubuntu/crm-backend/`
2. Inicia el servidor Flask:
   ```bash
   cd /home/ubuntu/crm-backend
   source venv/bin/activate
   python src/main.py
   ```

### 9. Configurar el CRM

1. El CRM estará disponible en `http://localhost:5000`
2. La primera vez que uses la API, se abrirá un navegador para autorizar el acceso
3. Configura el Spreadsheet ID usando la API:
   ```bash
   curl -X POST http://localhost:5000/api/config/spreadsheet \
     -H "Content-Type: application/json" \
     -d '{"spreadsheet_id": "TU_SPREADSHEET_ID"}'
   ```

### Estructura de archivos necesaria:

```
crm-backend/
├── credentials.json          # Archivo de credenciales de Google
├── token.json               # Se genera automáticamente
├── src/
│   ├── main.py
│   ├── services/
│   │   └── google_sheets.py
│   └── routes/
│       └── leads.py
└── requirements.txt
```

### Troubleshooting

#### Error: "File credentials.json not found"
- Asegúrate de que el archivo `credentials.json` esté en la carpeta correcta
- Verifica que el archivo tenga el nombre correcto

#### Error: "The file token.json has been tampered with"
- Elimina el archivo `token.json` y vuelve a autenticar

#### Error: "Insufficient permissions"
- Verifica que la API de Google Sheets esté habilitada
- Asegúrate de que el archivo `credentials.json` tenga los permisos correctos

#### Error: "Spreadsheet not found"
- Verifica que el Spreadsheet ID sea correcto
- Asegúrate de que la cuenta autenticada tenga acceso al sheet

