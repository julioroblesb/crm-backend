# 🚀 CRM Lead Management System - Guía de Configuración Completa

## 📋 Descripción del Sistema

Este CRM es una aplicación completa que funciona como una interfaz visual moderna para tu Google Sheet, permitiendo gestionar leads, pipeline de ventas, tareas, cobranza y mensajería masiva por WhatsApp.

### ✨ Características Principales

- **Dashboard Interactivo**: Métricas en tiempo real con gráficos y KPIs
- **Gestión de Leads**: CRUD completo con filtros y búsqueda avanzada
- **Pipeline Visual**: Vista kanban del proceso de ventas
- **Calendario de Tareas**: Seguimiento de actividades y próximas acciones
- **Módulo de Cobranza**: Gestión de pagos pendientes y a crédito
- **Mensajería Masiva**: Campañas de WhatsApp para leads inactivos
- **Sincronización Automática**: Todos los datos se guardan en Google Sheets

## 🏗️ Arquitectura del Sistema

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │    Backend      │    │  Google Sheets  │
│   (React)       │◄──►│    (Flask)      │◄──►│     (API)       │
│   Port: 5173    │    │   Port: 5000    │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🛠️ Instalación y Configuración

### Paso 1: Configurar Google Sheets API

1. **Crear proyecto en Google Cloud Console**
   - Ve a [Google Cloud Console](https://console.cloud.google.com/)
   - Crea un nuevo proyecto o selecciona uno existente
   - Habilita la **Google Sheets API**

2. **Configurar OAuth 2.0**
   - Ve a "APIs y servicios" > "Credenciales"
   - Crea "ID de cliente de OAuth 2.0" para "Aplicación de escritorio"
   - Descarga el archivo JSON y renómbralo a `credentials.json`
   - Colócalo en `/home/ubuntu/crm-backend/`

3. **Crear Google Sheet**
   - Crea un nuevo Google Sheet
   - Nombra la primera hoja como "Leads"
   - Agrega estos headers en la fila 1:

   ```
   A1: ID                    B1: NOMBRE               C1: TELEFONO
   D1: EMAIL                 E1: FUENTE               F1: REGISTRO
   G1: PRODUCTO_INTERES      H1: ESTADO               I1: PIPELINE
   J1: VENDEDOR              K1: COMENTARIOS          L1: FECHA_ULTIMO_CONTACTO
   M1: PROXIMA_ACCION        N1: FECHA_PROXIMA_ACCION O1: CONVERSACION
   P1: TIPO_PAGO             Q1: MONTO_PENDIENTE      R1: COMPROBANTE
   S1: FECHA_CREACION        T1: FECHA_MODIFICACION
   ```

4. **Obtener Spreadsheet ID**
   - Copia el ID de la URL del sheet (entre `/d/` y `/edit`)
   - Ejemplo: `https://docs.google.com/spreadsheets/d/SPREADSHEET_ID/edit`

### Paso 2: Configurar Backend Flask

1. **Navegar al directorio del backend**
   ```bash
   cd /home/ubuntu/crm-backend
   ```

2. **Activar entorno virtual**
   ```bash
   source venv/bin/activate
   ```

3. **Verificar dependencias**
   ```bash
   pip install -r requirements.txt
   ```

4. **Colocar archivo de credenciales**
   - Asegúrate de que `credentials.json` esté en la raíz del proyecto

5. **Iniciar servidor**
   ```bash
   python src/main.py
   ```
   
   El servidor estará disponible en: `http://localhost:5000`

### Paso 3: Configurar Frontend React

1. **Navegar al directorio del frontend**
   ```bash
   cd /home/ubuntu/crm-lead-management
   ```

2. **Instalar dependencias (si es necesario)**
   ```bash
   pnpm install
   ```

3. **Iniciar servidor de desarrollo**
   ```bash
   pnpm run dev --host
   ```
   
   La aplicación estará disponible en: `http://localhost:5173`

### Paso 4: Configurar la Aplicación

1. **Abrir la aplicación**
   - Ve a `http://localhost:5173`
   - Verás un mensaje de error inicial (esto es normal)

2. **Configurar Spreadsheet ID**
   ```bash
   curl -X POST http://localhost:5000/api/config/spreadsheet \
     -H "Content-Type: application/json" \
     -d '{"spreadsheet_id": "TU_SPREADSHEET_ID_AQUI"}'
   ```

3. **Autenticar con Google**
   ```bash
   curl -X POST http://localhost:5000/api/config/auth
   ```
   - Se abrirá un navegador para autorizar el acceso
   - Acepta los permisos solicitados

4. **Verificar conexión**
   - Recarga la aplicación en el navegador
   - Deberías ver el dashboard funcionando

## 📊 Estructura de Datos en Google Sheets

### Columnas Principales (Visibles en CRM)
- **NOMBRE**: Nombre completo del lead
- **TELEFONO**: Número de teléfono
- **EMAIL**: Correo electrónico
- **FUENTE**: Origen del lead (Facebook, Instagram, etc.)
- **PRODUCTO_INTERES**: Producto o servicio de interés
- **ESTADO**: Activo/Inactivo
- **PIPELINE**: Prospección, Contacto, Negociación, Cierre
- **VENDEDOR**: Vendedor asignado
- **COMENTARIOS**: Notas adicionales

### Columnas de Seguimiento (Para tareas)
- **FECHA_ULTIMO_CONTACTO**: Última vez que se contactó
- **PROXIMA_ACCION**: Acción a realizar
- **FECHA_PROXIMA_ACCION**: Cuándo realizar la acción
- **CONVERSACION**: Historial de conversaciones

### Columnas de Cobranza
- **TIPO_PAGO**: Completo/Crédito
- **MONTO_PENDIENTE**: Cantidad pendiente de pago
- **COMPROBANTE**: Con Comprobante/Sin Comprobante

### Columnas del Sistema
- **FECHA_CREACION**: Cuándo se creó el lead
- **FECHA_MODIFICACION**: Última modificación

## 🎯 Funcionalidades del CRM

### 1. Dashboard
- **KPIs en tiempo real**: Total leads, conversiones, tasa de conversión
- **Gráficos interactivos**: Distribución del pipeline y fuentes
- **Próximas tareas**: Lista de actividades programadas

### 2. Gestión de Leads
- **Crear/Editar/Eliminar** leads
- **Filtros avanzados** por etapa del pipeline
- **Búsqueda** por nombre, email o teléfono
- **Vista de tabla** con toda la información

### 3. Pipeline de Ventas
- **Vista kanban** con 4 etapas:
  - 🔵 Prospección
  - 🟡 Contacto
  - 🟠 Negociación
  - 🟢 Cierre
- **Métricas del pipeline** en tiempo real

### 4. Calendario de Tareas
- **Programar actividades** para cada lead
- **Vista de calendario** con próximas acciones
- **Recordatorios** y seguimiento

### 5. Módulo de Cobranza
- **Gestión de pagos a crédito**
- **Seguimiento de montos pendientes**
- **Control de comprobantes**
- **Alertas de vencimiento**

### 6. Mensajería Masiva
- **Selección de leads inactivos**
- **Plantillas de mensajes** predefinidas
- **Campañas de WhatsApp**
- **Historial de campañas**

## 🔧 API Endpoints

### Leads
- `GET /api/leads` - Obtener todos los leads
- `POST /api/leads` - Crear nuevo lead
- `PUT /api/leads/{id}` - Actualizar lead
- `DELETE /api/leads/{id}` - Eliminar lead (soft delete)

### Dashboard
- `GET /api/dashboard/metrics` - Métricas del dashboard

### Pipeline
- `GET /api/pipeline/stats` - Estadísticas del pipeline

### Cobranza
- `GET /api/cobranza` - Datos de cobranza

### Configuración
- `POST /api/config/spreadsheet` - Configurar Spreadsheet ID
- `POST /api/config/auth` - Autenticar con Google

## 🚀 Despliegue en Producción

### Opción 1: Despliegue Automático
```bash
# Desde el directorio del proyecto
cd /home/ubuntu/crm-backend

# Construir frontend y colocarlo en Flask static
cd ../crm-lead-management
pnpm run build
cp -r dist/* ../crm-backend/src/static/

# Desplegar backend con frontend incluido
cd ../crm-backend
# Usar herramienta de despliegue (se configurará según necesidades)
```

### Opción 2: Servidores Separados
- **Frontend**: Desplegar en Netlify, Vercel, etc.
- **Backend**: Desplegar en Heroku, Railway, etc.
- **Configurar CORS** para permitir comunicación entre dominios

## 🔍 Solución de Problemas

### Error: "Servicio no autenticado"
- Verificar que `credentials.json` esté en la ubicación correcta
- Ejecutar el proceso de autenticación nuevamente
- Verificar que la API de Google Sheets esté habilitada

### Error: "Spreadsheet not found"
- Verificar que el Spreadsheet ID sea correcto
- Asegurar que la cuenta autenticada tenga acceso al sheet
- Verificar que la hoja se llame "Leads"

### Error de CORS
- Verificar que el backend esté configurado con CORS
- Asegurar que las URLs del frontend estén en la lista de orígenes permitidos

### Problemas de conexión
- Verificar que ambos servidores estén ejecutándose
- Comprobar que los puertos 5000 y 5173 estén disponibles
- Revisar la configuración de firewall

## 📝 Notas Importantes

1. **Seguridad**: Nunca subas `credentials.json` a repositorios públicos
2. **Backup**: Google Sheets actúa como backup automático de tus datos
3. **Límites**: Google Sheets API tiene límites de uso (100 requests/100 segundos/usuario)
4. **Escalabilidad**: Para grandes volúmenes, considera migrar a una base de datos

## 🆘 Soporte

Si encuentras problemas:
1. Revisa los logs del backend en la terminal
2. Verifica la consola del navegador para errores del frontend
3. Asegúrate de que Google Sheets esté configurado correctamente
4. Consulta la documentación de Google Sheets API

## 🎉 ¡Listo!

Tu CRM está configurado y listo para usar. Puedes empezar agregando leads y viendo cómo se sincronizan automáticamente con tu Google Sheet.

