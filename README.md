# FastAPI REST API Template

Una plantilla limpia y moderna para crear APIs REST con FastAPI, lista para producción.

## 🚀 Características

- ⚡ **FastAPI** - Framework web moderno y rápido para APIs
- 🗄️ **SQLModel** - ORM moderno que combina Pydantic + SQLAlchemy
- 🔐 **JWT Authentication** - Autenticación segura con tokens JWT
- 📧 **Email System** - Sistema completo de emails con templates MJML
- 🗃️ **PostgreSQL** - Base de datos robusta con migraciones Alembic
- 🧪 **Testing** - Suite completa de pruebas con Pytest
- 📝 **Auto Documentation** - Documentación automática con OpenAPI/Swagger
- 🔒 **Security** - Hash seguro de contraseñas con bcrypt
- ⚙️ **Environment Config** - Configuración flexible por ambientes

## 📋 Requisitos

- Python 3.10+
- PostgreSQL 12+
- pip o poetry

## 🛠️ Instalación

### 1. Clonar el repositorio

```bash
git clone <tu-repositorio>
cd fastapi-template
```

### 2. Crear entorno virtual

```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt  # Para desarrollo
```

### 4. Configurar variables de entorno

Copia el archivo `.env.example` a `.env` y configura las variables:

```bash
cp .env.example .env
```

Edita `.env` con tus valores:

```env
PROJECT_NAME="Mi API"
SECRET_KEY="tu-clave-secreta-aqui"
POSTGRES_SERVER="localhost"
POSTGRES_PORT=5432
POSTGRES_USER="postgres"
POSTGRES_PASSWORD="tu-password"
POSTGRES_DB="mi_api"
FIRST_SUPERUSER="admin@example.com"
FIRST_SUPERUSER_PASSWORD="admin123"
SMTP_HOST="smtp.gmail.com"
SMTP_USER="tu-email@gmail.com"
SMTP_PASSWORD="tu-password-app"
EMAILS_FROM_EMAIL="tu-email@gmail.com"
```

### 5. Configurar base de datos

```bash
# Crear la base de datos en PostgreSQL
createdb mi_api

# Ejecutar migraciones
alembic upgrade head
```

### 6. Ejecutar la aplicación

**Opción 1: Con uvicorn directamente**
```bash
uvicorn app.main:app --reload
```

**Opción 2: Con el script de inicio**
```bash
python run.py
```

**Opción 3: Con uvicorn y configuración personalizada**
```bash
uvicorn app.main:app --reload --host localhost --port 8000
```

La API estará disponible en: http://localhost:8000

## 📚 Documentación

- **API Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

## 🏗️ Estructura del Proyecto

```
/
├── app/
│   ├── __init__.py
│   ├── main.py                 # Punto de entrada de la aplicación
│   ├── api/                    # Rutas de la API
│   │   ├── __init__.py
│   │   ├── main.py            # Router principal
│   │   ├── deps.py            # Dependencias (auth, DB)
│   │   └── routes/            # Rutas organizadas por funcionalidad
│   │       ├── login.py       # Autenticación
│   │       ├── users.py       # Gestión de usuarios
│   │       ├── items.py       # CRUD de items
│   │       └── utils.py       # Utilidades
│   ├── core/                  # Configuración central
│   │   ├── config.py         # Configuración y variables de entorno
│   │   ├── security.py       # Funciones de seguridad
│   │   └── db.py             # Conexión a base de datos
│   ├── models.py              # Modelos SQLModel
│   ├── crud.py               # Operaciones de base de datos
│   └── utils.py              # Utilidades generales
├── alembic/                  # Migraciones de base de datos
│   ├── env.py               # Configuración de Alembic
│   ├── script.py.mako       # Template para migraciones
│   └── versions/            # Archivos de migración
├── requirements.txt          # Dependencias de producción
├── requirements-dev.txt      # Dependencias de desarrollo
├── alembic.ini              # Configuración de Alembic
├── .env.example             # Ejemplo de variables de entorno
├── run.py                   # Script de inicio
└── README.md
```

## 🔐 Autenticación

La API usa JWT (JSON Web Tokens) para autenticación:

1. **Registro**: `POST /api/v1/users/signup`
2. **Login**: `POST /api/v1/login/access-token`
3. **Usar token**: Incluir `Authorization: Bearer <token>` en headers

### Ejemplo de uso:

```bash
# Login
curl -X POST "http://localhost:8000/api/v1/login/access-token" \
     -H "Content-Type: application/x-www-form-urlencoded" \
     -d "username=admin@example.com&password=admin123"

# Usar token
curl -X GET "http://localhost:8000/api/v1/users/me" \
     -H "Authorization: Bearer <tu-token>"
```

## 🧪 Testing

```bash
# Ejecutar todas las pruebas
pytest

# Con cobertura
pytest --cov=app

# Pruebas específicas
pytest tests/api/routes/test_login.py
```

## 🗄️ Base de Datos

### Migraciones

```bash
# Crear nueva migración
alembic revision --autogenerate -m "descripción del cambio"

# Aplicar migraciones
alembic upgrade head

# Revertir migración
alembic downgrade -1
```

### Modelos principales

- **User**: Usuarios del sistema
- **Item**: Items asociados a usuarios
- **Token**: Tokens JWT

## 📧 Sistema de Emails

La aplicación incluye un sistema completo de emails:

- **Registro**: Email de bienvenida
- **Recuperación**: Reset de contraseña
- **Templates**: Emails HTML con MJML

### Configuración SMTP

Configura las variables SMTP en `.env`:

```env
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=tu-email@gmail.com
SMTP_PASSWORD=tu-password-app
EMAILS_FROM_EMAIL=tu-email@gmail.com
```

## 🚀 Despliegue

### Variables de entorno para producción

```env
ENVIRONMENT=production
SECRET_KEY=clave-super-secreta-de-produccion
POSTGRES_PASSWORD=password-super-seguro
FIRST_SUPERUSER_PASSWORD=password-admin-seguro
```

### Comando de producción

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

## 🔧 Desarrollo

### Pre-commit hooks

```bash
pre-commit install
pre-commit run --all-files
```

### Linting

```bash
ruff check .
ruff format .
```

### Type checking

```bash
mypy app/
```

## 📝 API Endpoints

### Autenticación
- `POST /api/v1/login/access-token` - Login
- `POST /api/v1/login/test-token` - Verificar token
- `POST /api/v1/password-recovery/{email}` - Recuperar contraseña
- `POST /api/v1/reset-password/` - Resetear contraseña

### Usuarios
- `GET /api/v1/users/` - Listar usuarios (admin)
- `POST /api/v1/users/` - Crear usuario (admin)
- `GET /api/v1/users/me` - Mi perfil
- `PATCH /api/v1/users/me` - Actualizar mi perfil
- `PATCH /api/v1/users/me/password` - Cambiar contraseña
- `DELETE /api/v1/users/me` - Eliminar mi cuenta
- `POST /api/v1/users/signup` - Registro público
- `GET /api/v1/users/{user_id}` - Obtener usuario por ID
- `PATCH /api/v1/users/{user_id}` - Actualizar usuario (admin)
- `DELETE /api/v1/users/{user_id}` - Eliminar usuario (admin)

### Items
- `GET /api/v1/items/` - Listar mis items
- `POST /api/v1/items/` - Crear item
- `GET /api/v1/items/{item_id}` - Obtener item
- `PATCH /api/v1/items/{item_id}` - Actualizar item
- `DELETE /api/v1/items/{item_id}` - Eliminar item

### Utilidades
- `GET /api/v1/utils/health-check/` - Health check

## 🤝 Contribuir

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.

## 🆘 Soporte

Si tienes problemas o preguntas:

1. Revisa la documentación de FastAPI: https://fastapi.tiangolo.com/
2. Abre un issue en el repositorio
3. Consulta la documentación automática en `/docs`

---

**¡Disfruta construyendo tu API con FastAPI!** 🚀