# Sistema de Gestión de Trabajos

Sistema web desarrollado en Django para la gestión de trabajos, clientes y pagos.

## Requisitos Previos

1. **Python 3.8+**
2. **PostgreSQL 12+**
3. **pip** (gestor de paquetes de Python)

## Configuración de la Base de Datos

### 1. Instalar PostgreSQL
Descarga e instala PostgreSQL desde [postgresql.org](https://www.postgresql.org/download/)

### 2. Crear la Base de Datos
Abre la consola de PostgreSQL (psql) y ejecuta:

\`\`\`sql
CREATE DATABASE sistema_trabajos_db;
CREATE USER postgres WITH PASSWORD 'tu_password';
GRANT ALL PRIVILEGES ON DATABASE sistema_trabajos_db TO postgres;
\`\`\`

### 3. Configurar Credenciales
Edita el archivo `sistema_trabajos/settings.py` y actualiza las credenciales de la base de datos:

\`\`\`python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'sistema_trabajos_db',
        'USER': 'tu_usuario',
        'PASSWORD': 'tu_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
\`\`\`

## Instalación

### 1. Instalar Dependencias
\`\`\`bash
pip install -r requirements.txt
\`\`\`

### 2. Configurar Base de Datos
\`\`\`bash
python setup_database.py
\`\`\`

### 3. Crear Superusuario (Opcional)
\`\`\`bash
python manage.py createsuperuser
\`\`\`

### 4. Ejecutar el Servidor
\`\`\`bash
python manage.py runserver
\`\`\`

## Características de Seguridad

- **Autenticación Obligatoria**: Todas las funciones requieren que el usuario esté autenticado
- **Middleware de Seguridad**: Protege automáticamente todas las rutas excepto login y registro
- **Aislamiento de Datos**: Cada usuario solo puede ver sus propios trabajos y datos

## Uso

1. Accede a `http://localhost:8000`
2. Regístrate o inicia sesión
3. Gestiona clientes, trabajos y pagos desde el dashboard

## Funcionalidades

- ✅ Registro y autenticación de usuarios
- ✅ Gestión de clientes
- ✅ Creación y seguimiento de trabajos
- ✅ Control de pagos y saldos
- ✅ Estados de trabajo (Pendiente, En Proceso, Terminado, Entregado)
- ✅ Facturación electrónica opcional
- ✅ Dashboard con resumen de trabajos

## Estructura del Proyecto

\`\`\`
sistema_trabajos/
├── gestion_trabajos/          # Aplicación principal
│   ├── models.py             # Modelos de datos
│   ├── views.py              # Vistas y lógica
│   ├── forms.py              # Formularios
│   ├── urls.py               # URLs de la aplicación
│   └── middleware.py         # Middleware de autenticación
├── templates/                # Plantillas HTML
├── sistema_trabajos/         # Configuración del proyecto
│   └── settings.py           # Configuración principal
├── requirements.txt          # Dependencias
└── setup_database.py        # Script de configuración
