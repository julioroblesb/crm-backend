# 📋 GUÍA ULTRA DETALLADA: Configuración de Google Sheets para CRM

## 🎯 PASO 1: PREPARAR TU GOOGLE SHEET

### 1.1 Crear el Google Sheet
1. Ve a [sheets.google.com](https://sheets.google.com)
2. Haz clic en "Crear" o el botón "+"
3. Se abrirá un nuevo spreadsheet

### 1.2 Configurar el nombre del archivo
1. En la parte superior izquierda, donde dice "Hoja de cálculo sin título"
2. Haz clic y cambia el nombre a: **"CRM Leads Database"**
3. Presiona Enter para guardar

### 1.3 Renombrar la hoja
1. En la parte inferior, verás una pestaña que dice "Hoja 1"
2. Haz clic derecho sobre "Hoja 1"
3. Selecciona "Cambiar nombre"
4. Escribe exactamente: **"Leads"** (sin comillas)
5. Presiona Enter

### 1.4 Configurar los headers (EXACTAMENTE como se muestra)
En la **FILA 1**, escribe estos headers en cada columna:

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

### 1.5 Formatear los headers
1. Selecciona toda la fila 1 (A1:T1)
2. Haz clic en el botón "Negrita" (B) en la barra de herramientas
3. Cambia el color de fondo:
   - Haz clic en el icono de "Color de relleno" (balde de pintura)
   - Selecciona un azul claro
4. Cambia el color del texto a blanco si es necesario

### 1.6 Configurar validación de datos (IMPORTANTE)

#### Para la columna E (FUENTE):
1. Selecciona toda la columna E (haz clic en la letra "E")
2. Ve a "Datos" > "Validación de datos"
3. En "Criterios", selecciona "Lista de elementos"
4. En el campo de texto, escribe exactamente:
   ```
   Facebook,Instagram,WhatsApp,Web,Referido,Llamada Fría,Evento,Otro
   ```
5. Marca "Mostrar lista desplegable en la celda"
6. Haz clic en "Listo"

#### Para la columna H (ESTADO):
1. Selecciona toda la columna H
2. Ve a "Datos" > "Validación de datos"
3. En "Criterios", selecciona "Lista de elementos"
4. Escribe exactamente: `Activo,Inactivo`
5. Marca "Mostrar lista desplegable en la celda"
6. Haz clic en "Listo"

#### Para la columna I (PIPELINE):
1. Selecciona toda la columna I
2. Ve a "Datos" > "Validación de datos"
3. En "Criterios", selecciona "Lista de elementos"
4. Escribe exactamente: `Prospección,Contacto,Negociación,Cierre`
5. Marca "Mostrar lista desplegable en la celda"
6. Haz clic en "Listo"

#### Para la columna P (TIPO_PAGO):
1. Selecciona toda la columna P
2. Ve a "Datos" > "Validación de datos"
3. En "Criterios", selecciona "Lista de elementos"
4. Escribe exactamente: `Completo,Crédito`
5. Marca "Mostrar lista desplegable en la celda"
6. Haz clic en "Listo"

#### Para la columna R (COMPROBANTE):
1. Selecciona toda la columna R
2. Ve a "Datos" > "Validación de datos"
3. En "Criterios", selecciona "Lista de elementos"
4. Escribe exactamente: `Con Comprobante,Sin Comprobante`
5. Marca "Mostrar lista desplegable en la celda"
6. Haz clic en "Listo"

### 1.7 Obtener el Spreadsheet ID
1. Mira la URL de tu Google Sheet
2. Se verá algo así: `https://docs.google.com/spreadsheets/d/1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms/edit#gid=0`
3. Copia la parte entre `/d/` y `/edit`
4. En el ejemplo anterior sería: `1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms`
5. **GUARDA ESTE ID** - lo necesitarás más tarde

---

## 🔧 PASO 2: CONFIGURAR GOOGLE CLOUD CONSOLE

### 2.1 Crear proyecto en Google Cloud
1. Ve a [console.cloud.google.com](https://console.cloud.google.com)
2. Si es tu primera vez, acepta los términos de servicio
3. En la parte superior, haz clic en "Seleccionar proyecto"
4. Haz clic en "PROYECTO NUEVO"
5. Nombre del proyecto: **"CRM Leads Integration"**
6. Haz clic en "CREAR"
7. Espera a que se cree el proyecto (puede tomar 1-2 minutos)

### 2.2 Habilitar Google Sheets API
1. Una vez creado el proyecto, asegúrate de que esté seleccionado
2. En el menú lateral izquierdo, busca "APIs y servicios"
3. Haz clic en "Biblioteca"
4. En el buscador, escribe: **"Google Sheets API"**
5. Haz clic en "Google Sheets API" en los resultados
6. Haz clic en el botón azul "HABILITAR"
7. Espera a que se habilite (aparecerá una pantalla de confirmación)

### 2.3 Crear credenciales OAuth 2.0
1. Ve a "APIs y servicios" > "Credenciales"
2. Haz clic en "+ CREAR CREDENCIALES"
3. Selecciona "ID de cliente de OAuth 2.0"
4. Si aparece una pantalla de "Configurar pantalla de consentimiento":
   - Haz clic en "CONFIGURAR PANTALLA DE CONSENTIMIENTO"
   - Selecciona "Externo"
   - Haz clic en "CREAR"
   - Llena los campos obligatorios:
     - Nombre de la aplicación: **"CRM Leads"**
     - Correo electrónico de asistencia: **tu email**
     - Correo electrónico del desarrollador: **tu email**
   - Haz clic en "GUARDAR Y CONTINUAR"
   - En "Alcances", haz clic en "GUARDAR Y CONTINUAR"
   - En "Usuarios de prueba", haz clic en "GUARDAR Y CONTINUAR"
   - Revisa y haz clic en "VOLVER AL PANEL"

5. Ahora vuelve a "Credenciales" y haz clic en "+ CREAR CREDENCIALES"
6. Selecciona "ID de cliente de OAuth 2.0"
7. Tipo de aplicación: **"Aplicación de escritorio"**
8. Nombre: **"CRM Desktop Client"**
9. Haz clic en "CREAR"

### 2.4 Descargar el archivo de credenciales
1. Aparecerá una ventana con tu ID de cliente creado
2. Haz clic en "DESCARGAR JSON"
3. Se descargará un archivo con un nombre largo como `client_secret_123456789.json`
4. **RENOMBRA** este archivo a exactamente: `credentials.json`
5. **GUARDA** este archivo en un lugar seguro

---

## 🚀 PASO 3: CONFIGURAR EL PROYECTO CRM

### 3.1 Preparar el archivo credentials.json
1. Toma el archivo `credentials.json` que descargaste
2. Ábrelo con un editor de texto para verificar que se ve así:
```json
{
  "installed": {
    "client_id": "tu-client-id.apps.googleusercontent.com",
    "project_id": "tu-proyecto-id",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_secret": "tu-client-secret",
    "redirect_uris": ["http://localhost"]
  }
}
```

### 3.2 Configurar el backend
1. Coloca el archivo `credentials.json` en la carpeta raíz del backend:
   ```
   crm-backend/
   ├── credentials.json  ← AQUÍ
   ├── src/
   ├── requirements.txt
   └── ...
   ```

### 3.3 Configurar variables de entorno
1. Crea un archivo `.env` en la carpeta `crm-backend/`
2. Agrega esta línea (reemplaza con tu Spreadsheet ID real):
   ```
   SPREADSHEET_ID=1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms
   ```

---

## 🔄 PASO 4: PRIMERA CONEXIÓN Y AUTENTICACIÓN

### 4.1 Iniciar el backend
1. Abre una terminal
2. Navega a la carpeta del backend:
   ```bash
   cd crm-backend
   ```
3. Activa el entorno virtual:
   ```bash
   source venv/bin/activate
   ```
4. Inicia el servidor:
   ```bash
   python src/main.py
   ```
5. Deberías ver: `Running on http://127.0.0.1:5000`

### 4.2 Configurar el Spreadsheet ID
1. Abre otra terminal
2. Ejecuta este comando (reemplaza `TU_SPREADSHEET_ID` con el ID real):
   ```bash
   curl -X POST http://localhost:5000/api/config/spreadsheet \
     -H "Content-Type: application/json" \
     -d '{"spreadsheet_id": "TU_SPREADSHEET_ID"}'
   ```
3. Deberías recibir: `{"success": true, "message": "Spreadsheet configurado correctamente"}`

### 4.3 Autenticar con Google
1. Ejecuta este comando:
   ```bash
   curl -X POST http://localhost:5000/api/config/auth
   ```
2. **SE ABRIRÁ AUTOMÁTICAMENTE** tu navegador web
3. Selecciona tu cuenta de Google (la misma que usaste para crear el Sheet)
4. Verás una pantalla que dice "Google hasn't verified this app"
5. Haz clic en "Advanced" (Avanzado)
6. Haz clic en "Go to CRM Leads (unsafe)" (Ir a CRM Leads - no seguro)
7. Haz clic en "Continue" (Continuar)
8. Verás los permisos solicitados
9. Haz clic en "Allow" (Permitir)
10. Verás una página que dice "The authentication flow has completed"
11. **CIERRA** la pestaña del navegador
12. En la terminal deberías ver: `{"success": true, "message": "Autenticación exitosa"}`

### 4.4 Verificar la conexión
1. Ejecuta este comando para probar:
   ```bash
   curl http://localhost:5000/api/leads
   ```
2. Deberías recibir:
   ```json
   {"success": true, "data": [], "count": 0}
   ```
3. Si ves esto, ¡LA CONEXIÓN ESTÁ FUNCIONANDO!

---

## 🧪 PASO 5: PROBAR CON DATOS DE EJEMPLO

### 5.1 Agregar un lead de prueba
1. Ejecuta este comando:
   ```bash
   curl -X POST http://localhost:5000/api/leads \
     -H "Content-Type: application/json" \
     -d '{
       "nombre": "Juan Pérez",
       "telefono": "+1234567890",
       "email": "juan@ejemplo.com",
       "fuente": "Facebook",
       "producto_interes": "Producto A",
       "vendedor": "María López",
       "pipeline": "Prospección",
       "estado": "Activo",
       "comentarios": "Lead de prueba"
     }'
   ```

### 5.2 Verificar en Google Sheets
1. Ve a tu Google Sheet
2. Deberías ver una nueva fila (fila 2) con los datos del lead
3. Las columnas de fecha se llenarán automáticamente

### 5.3 Verificar en el CRM
1. Abre el frontend: `http://localhost:5173`
2. Ve a la sección "Leads"
3. Deberías ver el lead que acabas de crear

---

## 🔧 PASO 6: SOLUCIÓN DE PROBLEMAS COMUNES

### Error: "File credentials.json not found"
- **Solución**: Verifica que el archivo `credentials.json` esté en la carpeta raíz del backend

### Error: "The file token.json has been tampered with"
- **Solución**: Elimina el archivo `token.json` y vuelve a ejecutar la autenticación

### Error: "Spreadsheet not found"
- **Solución**: Verifica que el Spreadsheet ID sea correcto y que tengas acceso al sheet

### Error: "Insufficient permissions"
- **Solución**: Asegúrate de que la API de Google Sheets esté habilitada en tu proyecto

### Error: "Failed to fetch"
- **Solución**: Verifica que el backend esté ejecutándose en el puerto 5000

---

## ✅ CHECKLIST FINAL

Antes de usar el CRM en producción, verifica:

- [ ] Google Sheet creado con el nombre "Leads"
- [ ] Headers configurados exactamente como se especifica
- [ ] Validación de datos configurada para las columnas correspondientes
- [ ] Proyecto de Google Cloud creado
- [ ] Google Sheets API habilitada
- [ ] Credenciales OAuth 2.0 creadas y descargadas
- [ ] Archivo `credentials.json` en la carpeta del backend
- [ ] Spreadsheet ID configurado en el sistema
- [ ] Autenticación completada exitosamente
- [ ] Prueba de creación de lead exitosa
- [ ] Datos aparecen tanto en el CRM como en Google Sheets

---

## 🎉 ¡LISTO!

Si completaste todos estos pasos, tu CRM está completamente conectado con Google Sheets y listo para usar. Todos los cambios que hagas en el CRM se reflejarán automáticamente en tu Google Sheet y viceversa.

