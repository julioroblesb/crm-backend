# CRM Lead Management System - Análisis de Requisitos

## Visión General
Crear un sistema CRM que funcione como una interfaz visual moderna para un Google Sheet existente, permitiendo gestionar leads de manera eficiente con sincronización automática bidireccional.

## Inspiración de Diseño
Basado en las imágenes proporcionadas, el diseño debe incluir:
- **Sidebar de navegación** con iconos y menús claros (Dashboard, Contacts, Companies, Deals, Account Managers)
- **Dashboard principal** con gráficos y métricas visuales
- **Tabla de datos** limpia y organizada con filtros y búsqueda
- **Esquema de colores** moderno con tonos azules/morados como color principal
- **Cards y elementos visuales** para mostrar información de manera atractiva

## Estructura de Datos (Columnas del Google Sheet)

### Columnas Principales (Visibles en la interfaz)
1. **NOMBRE** - Nombre del lead
2. **TELEFONO** - Número de contacto
3. **FUENTE** - Origen del lead (redes sociales, referidos, etc.)
4. **REGISTRO** - Fecha de registro
5. **PRODUCTO_INTERES** - Producto o servicio de interés
6. **EMAIL** - Correo electrónico
7. **ESTADO** - Activo/Inactivo
8. **PIPELINE** - Etapa del proceso de ventas
9. **VENDEDOR** - Asignado responsable
10. **COMENTARIOS** - Notas generales

### Columnas de Seguimiento (Ocultas, accesibles via modal/popup)
11. **FECHA_ULTIMO_CONTACTO** - Última interacción
12. **PROXIMA_ACCION** - Tarea pendiente
13. **FECHA_PROXIMA_ACCION** - Fecha programada para la acción
14. **CONVERSACION** - Historial de conversaciones

## Funcionalidades del Pipeline de Ventas

### Etapas del Pipeline
1. **Prospección** - Lead inicial
2. **Contacto** - Primer contacto realizado
3. **Negociación** - En proceso de negociación
4. **Cierre** - Venta cerrada

### Gestión de Cierre
Cuando un lead llega a "Cierre", debe registrar:
- **Tipo de pago**: Completo o Crédito
- **Monto pendiente** (si es a crédito)
- **Estado del comprobante**: Con/Sin comprobante de pago

## Funcionalidades Principales

### 1. Dashboard Principal
- Gráficos de leads por etapa del pipeline
- Métricas de conversión
- Resumen de ventas por período
- Leads recientes y próximas acciones

### 2. Gestión de Leads
- **Vista de tabla** con todas las columnas principales
- **Filtros** por estado, pipeline, vendedor, fuente
- **Búsqueda** por nombre, teléfono, email
- **Acciones CRUD**: Crear, editar, eliminar leads
- **Modal de detalles** al hacer clic en el nombre del lead

### 3. Sistema de Tareas y Calendario
- **Calendario integrado** para ver tareas programadas
- **Gestión de seguimiento** por lead
- **Recordatorios** de próximas acciones
- **Historial de interacciones**

### 4. Sección de Cobranza
- **Vista especializada** para leads con pagos a crédito
- **Seguimiento de montos pendientes**
- **Estado de comprobantes de pago**
- **Gestión de cobranza**

### 5. Mensajería Masiva WhatsApp
- **Repositorio de leads inactivos** para campañas
- **Selección masiva** de contactos
- **Plantillas de mensajes**
- **Integración con WhatsApp** (a definir método)

### 6. Gestión de Estados
- **Leads activos**: En proceso de venta
- **Leads inactivos**: Archivados pero disponibles para campañas
- **Transición automática** según criterios definidos

## Arquitectura Técnica

### Frontend
- **React.js** con diseño responsive
- **Componentes modulares** para cada sección
- **Estado global** para sincronización de datos
- **UI/UX moderna** basada en las imágenes de inspiración

### Backend
- **Flask API** como middleware
- **Google Sheets API** para sincronización
- **Autenticación OAuth2** para Google Sheets
- **Endpoints RESTful** para operaciones CRUD

### Integración
- **Sincronización bidireccional** automática
- **Manejo de errores** y validaciones
- **Cache local** para mejor rendimiento
- **Logs de actividad** para auditoría

## Consideraciones de Implementación

### Seguridad
- Autenticación segura con Google
- Validación de datos en frontend y backend
- Manejo seguro de tokens de acceso

### Performance
- Carga lazy de datos grandes
- Optimización de consultas a Google Sheets
- Cache inteligente de datos frecuentes

### Usabilidad
- Interfaz intuitiva y responsive
- Feedback visual para todas las acciones
- Manejo de estados de carga y errores

## Próximos Pasos
1. Configurar estructura detallada del Google Sheet
2. Investigar Google Sheets API y autenticación
3. Crear mockups detallados del diseño
4. Desarrollar MVP con funcionalidades básicas
5. Iterar y agregar funcionalidades avanzadas



## Arquitectura Detallada del Sistema

### Estructura de Archivos del Proyecto
```
crm-lead-management/
├── frontend/                 # React Application
│   ├── src/
│   │   ├── components/      # Componentes reutilizables
│   │   ├── pages/          # Páginas principales
│   │   ├── hooks/          # Custom hooks
│   │   ├── services/       # API calls
│   │   ├── utils/          # Utilidades
│   │   └── styles/         # Estilos globales
│   ├── public/
│   └── package.json
├── backend/                 # Flask API
│   ├── app/
│   │   ├── routes/         # Endpoints API
│   │   ├── services/       # Lógica de negocio
│   │   ├── models/         # Modelos de datos
│   │   └── utils/          # Utilidades backend
│   ├── config/             # Configuraciones
│   └── requirements.txt
└── docs/                   # Documentación
```

### Flujo de Datos
1. **Frontend (React)** → Interfaz de usuario
2. **Backend (Flask)** → API middleware y lógica de negocio
3. **Google Sheets API** → Almacenamiento y sincronización
4. **Autenticación OAuth2** → Seguridad y permisos

### Endpoints API Principales
```
GET    /api/leads              # Obtener todos los leads
POST   /api/leads              # Crear nuevo lead
PUT    /api/leads/{id}         # Actualizar lead
DELETE /api/leads/{id}         # Eliminar lead
GET    /api/leads/{id}/tasks   # Obtener tareas del lead
POST   /api/leads/{id}/tasks   # Crear tarea para lead
GET    /api/dashboard/metrics  # Métricas del dashboard
GET    /api/pipeline/stats     # Estadísticas del pipeline
GET    /api/cobranza           # Datos de cobranza
POST   /api/whatsapp/campaign  # Enviar campaña masiva
```

### Estructura de Datos Extendida

#### Tabla Principal (Google Sheet: "Leads")
| Columna | Tipo | Descripción | Visible en UI |
|---------|------|-------------|---------------|
| ID | Número | Identificador único | Sí |
| NOMBRE | Texto | Nombre completo | Sí |
| TELEFONO | Texto | Número de contacto | Sí |
| EMAIL | Email | Correo electrónico | Sí |
| FUENTE | Lista | Origen del lead | Sí |
| REGISTRO | Fecha | Fecha de registro | Sí |
| PRODUCTO_INTERES | Texto | Producto/servicio | Sí |
| ESTADO | Lista | Activo/Inactivo | Sí |
| PIPELINE | Lista | Etapa del proceso | Sí |
| VENDEDOR | Lista | Responsable asignado | Sí |
| COMENTARIOS | Texto | Notas generales | Sí |
| FECHA_ULTIMO_CONTACTO | Fecha | Última interacción | Modal |
| PROXIMA_ACCION | Texto | Tarea pendiente | Modal |
| FECHA_PROXIMA_ACCION | Fecha | Fecha programada | Modal |
| CONVERSACION | Texto | Historial | Modal |
| TIPO_PAGO | Lista | Completo/Crédito | Cierre |
| MONTO_PENDIENTE | Número | Deuda pendiente | Cierre |
| COMPROBANTE | Lista | Con/Sin comprobante | Cierre |
| FECHA_CREACION | Fecha | Timestamp creación | Sistema |
| FECHA_MODIFICACION | Fecha | Última modificación | Sistema |

#### Valores de Listas Predefinidas
- **FUENTE**: Redes Sociales, Referidos, Web, Llamada Fría, Evento, Otro
- **ESTADO**: Activo, Inactivo
- **PIPELINE**: Prospección, Contacto, Negociación, Cierre
- **VENDEDOR**: [Lista configurable de vendedores]
- **TIPO_PAGO**: Completo, Crédito
- **COMPROBANTE**: Con Comprobante, Sin Comprobante

### Configuración de Google Sheets

#### Hoja 1: "Leads" (Principal)
- Contiene todos los datos de leads
- Formato de tabla con headers en fila 1
- Validación de datos para listas desplegables
- Formato condicional para estados del pipeline

#### Hoja 2: "Configuracion" (Opcional)
- Lista de vendedores
- Fuentes de leads personalizadas
- Configuraciones del sistema

#### Hoja 3: "Logs" (Auditoría)
- Registro de cambios
- Timestamp de sincronizaciones
- Errores y eventos del sistema

### Consideraciones de Seguridad

#### Autenticación Google OAuth2
- Scope: `https://www.googleapis.com/auth/spreadsheets`
- Almacenamiento seguro de tokens
- Refresh automático de tokens expirados

#### Validaciones
- Validación de formato de email y teléfono
- Sanitización de inputs
- Verificación de permisos por usuario

#### Manejo de Errores
- Retry automático para fallos de red
- Fallback a cache local
- Notificaciones de errores al usuario

### Performance y Optimización

#### Cache Strategy
- Cache de datos frecuentes en localStorage
- Invalidación inteligente de cache
- Sincronización en background

#### Lazy Loading
- Carga paginada de leads
- Componentes lazy para secciones grandes
- Imágenes y recursos optimizados

#### Sincronización
- Batch updates para múltiples cambios
- Debounce para evitar llamadas excesivas
- Queue de operaciones offline

Esta arquitectura asegura escalabilidad, mantenibilidad y una experiencia de usuario fluida mientras mantiene la sincronización perfecta con Google Sheets.

