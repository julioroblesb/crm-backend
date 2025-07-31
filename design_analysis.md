# Análisis de Diseño - CRM Lead Management

## Elementos de Diseño Identificados en las Imágenes de Inspiración

### 1. Layout General
- **Sidebar izquierdo** con navegación principal
- **Área de contenido principal** ocupando el resto del espacio
- **Header superior** con título de sección y acciones principales
- **Diseño responsive** que se adapta a diferentes tamaños de pantalla

### 2. Sidebar de Navegación
- **Fondo azul/morado** (#6366F1 aproximadamente)
- **Logo/Branding** en la parte superior ("Lightbox")
- **Menú de navegación** con iconos y texto:
  - Dashboard (icono de cuadrícula)
  - Contacts (icono de personas)
  - Companies (icono de edificio)
  - Deals (icono de gráfico)
  - Account Managers (icono de usuario)
- **Usuario logueado** en la parte inferior con avatar
- **Hover effects** en los elementos del menú

### 3. Dashboard Principal
- **Gráficos de barras** para "Deals by stage" y "Deals by quarter"
- **Colores diferenciados** para cada etapa:
  - Azul para "New Opportunity"
  - Verde para "Proposal" 
  - Amarillo para "Won"
  - Rojo para otras etapas
- **Métricas numéricas** prominentes en cada barra
- **Información contextual** como "Last updated at 11:31"
- **Tabs de navegación** entre diferentes vistas (Accounts, Deals)

### 4. Vista de Tabla (Deals)
- **Header con acciones**:
  - Barra de búsqueda
  - Filtro por "Deal stage"
  - Botón "Add deal" prominente en azul
- **Columnas organizadas**:
  - ID numérico
  - Companies (nombre de la empresa)
  - Deal stage (con badges de colores)
  - Amount (monto con formato de moneda)
  - Account Manager (responsable)
  - Close date (fecha de cierre)
  - Contract (archivos adjuntos)
- **Badges de estado** con colores:
  - Amarillo para "New Opportunity"
  - Verde para "Won"
  - Azul para "Proposal"
- **Acciones por fila** (menú de tres puntos)
- **Paginación** implícita con "Load more"

### 5. Esquema de Colores
- **Primario**: Azul/Morado (#6366F1)
- **Secundario**: Blanco (#FFFFFF)
- **Texto**: Gris oscuro (#374151)
- **Éxito**: Verde (#10B981)
- **Advertencia**: Amarillo (#F59E0B)
- **Error**: Rojo (#EF4444)
- **Fondo**: Gris muy claro (#F9FAFB)

### 6. Tipografía
- **Font family**: Sans-serif moderna (probablemente Inter o similar)
- **Tamaños**:
  - Títulos principales: ~24px
  - Subtítulos: ~18px
  - Texto normal: ~14px
  - Texto pequeño: ~12px
- **Pesos**: Regular (400), Medium (500), Semibold (600)

### 7. Componentes UI
- **Botones**: Redondeados con padding generoso
- **Cards**: Sombra sutil, bordes redondeados
- **Inputs**: Bordes suaves, focus states claros
- **Badges**: Redondeados, colores de fondo suaves
- **Iconos**: Outline style, consistentes en tamaño

## Adaptación para Nuestro CRM

### Estructura de Navegación Propuesta
```
- Dashboard (métricas y gráficos)
- Leads (gestión principal de leads)
- Pipeline (vista kanban del proceso)
- Calendario (tareas y seguimiento)
- Cobranza (gestión de pagos pendientes)
- Mensajería (campañas masivas WhatsApp)
- Configuración (ajustes del sistema)
```

### Componentes Específicos a Desarrollar

#### 1. Dashboard de Leads
- Gráfico de leads por etapa del pipeline
- Métricas de conversión mensual/trimestral
- Leads recientes y próximas acciones
- Resumen de ventas y cobranza

#### 2. Tabla de Leads
- Filtros por: Estado, Pipeline, Vendedor, Fuente
- Búsqueda por: Nombre, Teléfono, Email
- Columnas: Nombre, Teléfono, Fuente, Pipeline, Vendedor, Estado
- Acciones: Ver detalles, Editar, Eliminar, Cambiar estado

#### 3. Modal de Detalles de Lead
- Información completa del lead
- Historial de interacciones
- Programación de tareas
- Notas y comentarios

#### 4. Vista de Pipeline (Kanban)
- Columnas por etapa: Prospección, Contacto, Negociación, Cierre
- Drag & drop para mover leads entre etapas
- Contadores y métricas por columna

#### 5. Calendario de Tareas
- Vista mensual/semanal/diaria
- Tareas programadas por lead
- Recordatorios y notificaciones

#### 6. Sección de Cobranza
- Tabla de ventas a crédito
- Estado de pagos pendientes
- Seguimiento de comprobantes

#### 7. Mensajería Masiva
- Selección de leads inactivos
- Plantillas de mensajes
- Historial de campañas

### Responsive Design
- **Desktop**: Layout completo con sidebar
- **Tablet**: Sidebar colapsable
- **Mobile**: Navegación bottom tab o hamburger menu

### Estados y Feedback
- Loading states para todas las operaciones
- Success/error notifications
- Confirmaciones para acciones destructivas
- Indicadores de sincronización con Google Sheets

Este análisis servirá como base para el desarrollo del frontend, asegurando que el CRM tenga una interfaz moderna, intuitiva y profesional que inspire confianza en los usuarios.

