# Documentación Completa de la API - AreaMédica

**Fecha**: 12 de Octubre 2025  
**Versión de API**: 1.0.0  
**Base URL**: `http://localhost:8000`

---

## 📋 Tabla de Contenidos

1. [Resumen Ejecutivo](#-resumen-ejecutivo)
2. [Autenticación JWT](#-autenticación-jwt)
3. [Endpoints de Autenticación](#-endpoints-de-autenticación)
4. [Endpoints de Transacciones](#-endpoints-de-transacciones)
5. [Sistema de Errores Estandarizado](#-sistema-de-errores-estandarizado)
6. [Datos de Prueba](#-datos-de-prueba)
7. [Referencia de CSV](#-referencia-de-csv)
8. [Guía de Integración](#-guía-de-integración)

---

## 📊 Resumen Ejecutivo

✅ **Endpoints Probados**: 12  
✅ **Tests Exitosos**: 12/12 (100%)  
✅ **Errores Estandarizados**: ✅ Implementados  
✅ **Autenticación JWT**: ✅ Funcionando  
✅ **Health Check**: ✅ Activo  
✅ **Seed Data**: 3 usuarios + 5 transacciones

**Archivo de Referencia**: [`api_requests_responses.csv`](./api_requests_responses.csv) - Contiene ejemplos completos de todas las peticiones y respuestas probadas.

---

## 🔐 Autenticación JWT

### Arquitectura del Sistema

```
┌──────────┐                ┌──────────┐
│  Client  │  1. Login      │   API    │
│          │───────────────>│          │
│          │  Credentials   │          │
│          │                │          │
│          │  2. JWT Token  │          │
│          │<───────────────│          │
│          │                │          │
│          │  3. Request    │          │
│          │───────────────>│          │
│          │  + Bearer Token│          │
│          │                │          │
│          │  4. Response   │          │
│          │<───────────────│          │
└──────────┘                └──────────┘
```

### Flujo de Autenticación

1. **Login**: Cliente envía credenciales (email + password)
2. **Token JWT**: API retorna `access_token` y `token_type: "bearer"`
3. **Requests Autenticados**: Cliente incluye header `Authorization: Bearer {token}`
4. **Validación**: API valida token en cada request protegido

### Estructura del Token JWT

El token JWT contiene:
```json
{
  "sub": "user_id",           // UUID del usuario
  "email": "user@email.com",  // Email del usuario
  "permissions": [],          // Array de permisos
  "exp": 1760296115           // Timestamp de expiración
}
```

### Uso del Token

**Header requerido en todos los endpoints protegidos**:
```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Ejemplo con curl**:
```bash
# Guardar token en variable
TOKEN=$(curl -s -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@areamedica.com","password":"Admin123!"}' \
  | jq -r '.access_token')

# Usar token en requests
curl -H "Authorization: Bearer $TOKEN" http://localhost:8000/api/v1/auth/me
```

---

## 🔑 Endpoints de Autenticación

### 1. POST /api/v1/auth/login

Autentica un usuario y retorna un token JWT.

**Request Body**:
```json
{
  "email": "admin@areamedica.com",
  "password": "Admin123!"
}
```

**Response Success (200 OK)**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIwNWU3YmY1Mi00ZTdmLTRhMTktYjljYy1lNTQ5ZDAxODdlODciLCJlbWFpbCI6ImFkbWluQGFyZWFtZWRpY2EuY29tIiwicGVybWlzc2lvbnMiOltdLCJleHAiOjE3NjAyOTYxMTV9.K1Ds_yN-r2hJZVhIqycXf4eXwG0YCuC6TwKY89dktBQ",
  "token_type": "bearer"
}
```

**Response Error (401 Unauthorized)**:
```json
{
  "detail": {
    "error_code": "INVALID_CREDENTIALS",
    "message": "Invalid email or password"
  }
}
```

**Curl Example**:
```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@areamedica.com","password":"Admin123!"}'
```

**Status Codes**:
- `200 OK`: Login exitoso, retorna token
- `401 Unauthorized`: Credenciales inválidas

---

### 2. POST /api/v1/auth/register

Registra un nuevo usuario en el sistema.

**Request Body**:
```json
{
  "email": "newuser@test.com",
  "password": "Test123!",
  "full_name": "Test User"
}
```

**Response Success (201 Created)**:
```json
{
  "id": "e3a77661-f208-4f71-ad2f-3da9c5cc8751",
  "email": "newuser@test.com",
  "full_name": "Test User",
  "is_active": true,
  "permissions": []
}
```

**Response Error (409 Conflict)**:
```json
{
  "detail": {
    "error_code": "CONFLICT",
    "message": "User already exists",
    "details": {
      "resource": "User",
      "identifier": "newuser@test.com"
    }
  }
}
```

**Curl Example**:
```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email":"newuser@test.com",
    "password":"Test123!",
    "full_name":"Test User"
  }'
```

**Status Codes**:
- `201 Created`: Usuario creado exitosamente
- `409 Conflict`: El email ya existe
- `422 Unprocessable Entity`: Datos inválidos

---

### 3. GET /api/v1/auth/me

Obtiene la información del usuario autenticado actualmente.

**Headers**: 
```
Authorization: Bearer {token}
```

**Response Success (200 OK)**:
```json
{
  "id": "05e7bf52-4e7f-4a19-b9cc-e549d0187e87",
  "email": "admin@areamedica.com",
  "full_name": "Administrador Sistema",
  "is_active": true,
  "permissions": []
}
```

**Response Error (401 Unauthorized)**:
```json
{
  "detail": "Not authenticated"
}
```

**Curl Example**:
```bash
curl -X GET http://localhost:8000/api/v1/auth/me \
  -H "Authorization: Bearer $TOKEN"
```

**Status Codes**:
- `200 OK`: Usuario retornado correctamente
- `401 Unauthorized`: Token inválido o no proporcionado

---

## 💳 Endpoints de Transacciones

Todos los endpoints de transacciones requieren autenticación JWT.

### 4. GET /api/v1/transactions

Lista todas las transacciones con paginación.

**Query Parameters**:
- `page` (opcional): Número de página (default: 1)
- `limit` (opcional): Items por página (default: 10)

**Headers**:
```
Authorization: Bearer {token}
```

**Response Success (200 OK)**:
```json
{
  "transactions": [
    {
      "id": "b2cd7a2c-655d-40d0-9cd0-321eddfbba89",
      "transaction_id": "TRX-2025-001",
      "reference": "REF-BANESCO-001",
      "bank": "BANESCO",
      "transaction_type": "TRANSACTION",
      "status": "IN_PROGRESS",
      "customer_full_name": "Juan Pérez García",
      "customer_phone": "04121234567",
      "customer_national_id": "V12345678",
      "concept": "Consulta médica general",
      "extra_data": {},
      "created_by": "05e7bf52-4e7f-4a19-b9cc-e549d0187e87",
      "created_at": "2025-10-12T18:29:15.147595+00:00",
      "updated_at": "2025-10-12T18:29:15.147595+00:00"
    }
  ],
  "total": 6,
  "limit": 10,
  "offset": 0
}
```

**Response Error (401 Unauthorized)**:
```json
{
  "detail": "Not authenticated"
}
```

**Curl Example**:
```bash
curl -X GET "http://localhost:8000/api/v1/transactions?page=1&limit=10" \
  -H "Authorization: Bearer $TOKEN"
```

**Status Codes**:
- `200 OK`: Lista de transacciones retornada
- `401 Unauthorized`: Sin autenticación

---

### 5. GET /api/v1/transactions/{id}

Obtiene una transacción específica por su UUID.

**Path Parameters**:
- `id`: UUID de la transacción

**Headers**:
```
Authorization: Bearer {token}
```

**Response Success (200 OK)**:
```json
{
  "id": "b2cd7a2c-655d-40d0-9cd0-321eddfbba89",
  "transaction_id": "TRX-2025-001",
  "reference": "REF-BANESCO-001",
  "bank": "BANESCO",
  "transaction_type": "TRANSACTION",
  "status": "IN_PROGRESS",
  "customer_full_name": "Juan Pérez García",
  "customer_phone": "04121234567",
  "customer_national_id": "V12345678",
  "concept": "Consulta médica general",
  "extra_data": {},
  "created_by": "05e7bf52-4e7f-4a19-b9cc-e549d0187e87",
  "created_at": "2025-10-12T18:29:15.147595+00:00",
  "updated_at": "2025-10-12T18:29:15.147595+00:00"
}
```

**Response Error (404 Not Found)**:
```json
{
  "detail": {
    "error_code": "NOT_FOUND",
    "message": "Transaction with identifier 'b2cd7a2c-...' not found",
    "details": {
      "resource": "Transaction",
      "identifier": "b2cd7a2c-655d-40d0-9cd0-321eddfbba89"
    }
  }
}
```

**Curl Example**:
```bash
curl -X GET "http://localhost:8000/api/v1/transactions/b2cd7a2c-655d-40d0-9cd0-321eddfbba89" \
  -H "Authorization: Bearer $TOKEN"
```

**Status Codes**:
- `200 OK`: Transacción encontrada
- `404 Not Found`: Transacción no existe
- `401 Unauthorized`: Sin autenticación

---

### 6. GET /api/v1/transactions/external/{transaction_id}

Busca una transacción por su `transaction_id` externo (ej: "TRX-2025-001").

**Path Parameters**:
- `transaction_id`: ID externo de la transacción

**Headers**:
```
Authorization: Bearer {token}
```

**Response Success (200 OK)**:
```json
{
  "id": "b2cd7a2c-655d-40d0-9cd0-321eddfbba89",
  "transaction_id": "TRX-2025-001",
  "reference": "REF-BANESCO-001",
  "bank": "BANESCO",
  "transaction_type": "TRANSACTION",
  "status": "IN_PROGRESS",
  "customer_full_name": "Juan Pérez García",
  "customer_phone": "04121234567",
  "customer_national_id": "V12345678",
  "concept": "Consulta médica general",
  "extra_data": {},
  "created_by": "05e7bf52-4e7f-4a19-b9cc-e549d0187e87",
  "created_at": "2025-10-12T18:29:15.147595+00:00",
  "updated_at": "2025-10-12T18:29:15.147595+00:00"
}
```

**Response Error (404 Not Found)**:
```json
{
  "detail": {
    "error_code": "NOT_FOUND",
    "message": "Transaction with identifier 'TRX-XXXX' not found",
    "details": {
      "resource": "Transaction",
      "identifier": "TRX-XXXX"
    }
  }
}
```

**Curl Example**:
```bash
curl -X GET "http://localhost:8000/api/v1/transactions/external/TRX-2025-001" \
  -H "Authorization: Bearer $TOKEN"
```

**Status Codes**:
- `200 OK`: Transacción encontrada
- `404 Not Found`: transaction_id no existe
- `401 Unauthorized`: Sin autenticación

---

### 7. GET /api/v1/transactions/reference/{reference}

Busca una transacción por su número de referencia (ej: "REF-BANESCO-001").

**Path Parameters**:
- `reference`: Número de referencia de la transacción

**Headers**:
```
Authorization: Bearer {token}
```

**Response Success (200 OK)**:
```json
{
  "id": "b2cd7a2c-655d-40d0-9cd0-321eddfbba89",
  "transaction_id": "TRX-2025-001",
  "reference": "REF-BANESCO-001",
  "bank": "BANESCO",
  "transaction_type": "TRANSACTION",
  "status": "IN_PROGRESS",
  "customer_full_name": "Juan Pérez García",
  "customer_phone": "04121234567",
  "customer_national_id": "V12345678",
  "concept": "Consulta médica general",
  "extra_data": {},
  "created_by": "05e7bf52-4e7f-4a19-b9cc-e549d0187e87",
  "created_at": "2025-10-12T18:29:15.147595+00:00",
  "updated_at": "2025-10-12T18:29:15.147595+00:00"
}
```

**Response Error (404 Not Found)**:
```json
{
  "detail": {
    "error_code": "NOT_FOUND",
    "message": "Transaction with identifier 'REF-XXXX' not found",
    "details": {
      "resource": "Transaction",
      "identifier": "REF-XXXX"
    }
  }
}
```

**Curl Example**:
```bash
curl -X GET "http://localhost:8000/api/v1/transactions/reference/REF-BANESCO-001" \
  -H "Authorization: Bearer $TOKEN"
```

**Status Codes**:
- `200 OK`: Transacción encontrada
- `404 Not Found`: Referencia no existe
- `401 Unauthorized`: Sin autenticación

---

### 8. POST /api/v1/transactions

Crea una nueva transacción.

**Headers**:
```
Authorization: Bearer {token}
Content-Type: application/json
```

**Request Body**:
```json
{
  "transaction_id": "TRX-2025-TEST-001",
  "reference": "REF-TEST-001",
  "bank": "BANESCO",
  "transaction_type": "TRANSACTION",
  "customer_full_name": "Test Customer",
  "customer_phone": "04241234567",
  "customer_national_id": "V99999999",
  "concept": "Test transaction from API",
  "extra_data": {
    "test": true,
    "notes": "Additional information"
  }
}
```

**Response Success (201 Created)**:
```json
{
  "id": "4743155f-56ba-44d8-b597-349085f0ae8f",
  "transaction_id": "TRX-2025-TEST-001",
  "reference": "REF-TEST-001",
  "bank": "BANESCO",
  "transaction_type": "TRANSACTION",
  "status": "IN_PROGRESS",
  "customer_full_name": "Test Customer",
  "customer_phone": "04241234567",
  "customer_national_id": "V99999999",
  "concept": "Test transaction from API",
  "extra_data": {},
  "created_by": "05e7bf52-4e7f-4a19-b9cc-e549d0187e87",
  "created_at": "2025-10-12T18:38:36.669563+00:00",
  "updated_at": "2025-10-12T18:38:36.669563+00:00"
}
```

**Response Error (422 Validation Error)**:
```json
{
  "detail": {
    "error_code": "VALIDATION_ERROR",
    "message": "Invalid input data",
    "details": {
      "error": "field is required"
    }
  }
}
```

**Curl Example**:
```bash
curl -X POST http://localhost:8000/api/v1/transactions \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "transaction_id": "TRX-2025-TEST-001",
    "reference": "REF-TEST-001",
    "bank": "BANESCO",
    "transaction_type": "TRANSACTION",
    "customer_full_name": "Test Customer",
    "customer_phone": "04241234567",
    "customer_national_id": "V99999999",
    "concept": "Test transaction",
    "extra_data": {"test": true}
  }'
```

**Status Codes**:
- `201 Created`: Transacción creada exitosamente
- `401 Unauthorized`: Sin autenticación
- `422 Unprocessable Entity`: Datos inválidos

**Nota**: El estado inicial de la transacción es siempre `IN_PROGRESS`.

---

## 🏥 Health Check

### GET /health

Verifica el estado de la API.

**Response Success (200 OK)**:
```json
{
  "status": "healthy",
  "service": "areamedica-api"
}
```

**Curl Example**:
```bash
curl -X GET http://localhost:8000/health
```

**Status Codes**:
- `200 OK`: API funcionando correctamente

**Nota**: Este endpoint NO requiere autenticación.

---

## ❌ Sistema de Errores Estandarizado

Todos los endpoints ahora retornan errores en un formato consistente:

```json
{
  "detail": {
    "error_code": "ERROR_TYPE",
    "message": "Human readable message",
    "details": {
      "additional": "context"
    }
  }
}
```

### Códigos de Error

| Código                   | Status | Descripción                    | Ejemplo de Uso           |
| ------------------------ | ------ | ------------------------------ | ------------------------ |
| `INVALID_CREDENTIALS`    | 401    | Email o contraseña incorrectos | Login fallido            |
| `UNAUTHORIZED`           | 401    | Token inválido o ausente       | Acceso sin token         |
| `FORBIDDEN`              | 403    | Sin permisos para esta acción  | Falta de permisos        |
| `NOT_FOUND`              | 404    | Recurso no encontrado          | Transacción inexistente  |
| `CONFLICT`               | 409    | Recurso ya existe              | Email duplicado          |
| `VALIDATION_ERROR`       | 422    | Datos de entrada inválidos     | Campos faltantes         |
| `BUSINESS_RULE_ERROR`    | 400    | Regla de negocio violada       | Lógica de negocio        |
| `EXTERNAL_SERVICE_ERROR` | 502    | Servicio externo falló         | API de Banesco down      |
| `RATE_LIMIT_EXCEEDED`    | 429    | Demasiadas peticiones          | Límite de rate alcanzado |

### Ejemplos de Errores

#### Invalid Credentials (401)
```json
{
  "detail": {
    "error_code": "INVALID_CREDENTIALS",
    "message": "Invalid email or password"
  }
}
```

#### Unauthorized (401)
```json
{
  "detail": {
    "error_code": "UNAUTHORIZED",
    "message": "Not authenticated"
  }
```

o

```json
{
  "detail": "Not authenticated"
}
```

#### Not Found (404)
```json
{
  "detail": {
    "error_code": "NOT_FOUND",
    "message": "Transaction with identifier 'NONEXISTENT-REF' not found",
    "details": {
      "resource": "Transaction",
      "identifier": "NONEXISTENT-REF"
    }
  }
}
```

#### Conflict / Already Exists (409)
```json
{
  "detail": {
    "error_code": "CONFLICT",
    "message": "User already exists",
    "details": {
      "resource": "User",
      "identifier": "admin@areamedica.com"
    }
  }
}
```

#### Validation Error (422)
```json
{
  "detail": {
    "error_code": "VALIDATION_ERROR",
    "message": "Invalid transaction data",
    "details": {
      "error": "customer_phone is required"
    }
  }
}
```

---

## 📝 Datos de Prueba

### Usuarios de Prueba (Seed Data)

Estos usuarios están disponibles en la base de datos para pruebas:

| Email                  | Password  | Role  | Full Name             | ID                                   |
| ---------------------- | --------- | ----- | --------------------- | ------------------------------------ |
| admin@areamedica.com   | Admin123! | Admin | Administrador Sistema | 05e7bf52-4e7f-4a19-b9cc-e549d0187e87 |
| usuario@areamedica.com | User123!  | User  | Usuario Regular       | 4dbfa0c1-e3f7-47c6-b4e1-b0c03c06b98e |
| test@areamedica.com    | Test123!  | User  | Usuario de Prueba     | 1c2d39d6-df34-478f-a0d9-a2f1cf29e864 |

### Transacciones de Prueba (Seed Data)

| transaction_id | Reference       | Bank            | Type        | Status      | Customer                  |
| -------------- | --------------- | --------------- | ----------- | ----------- | ------------------------- |
| TRX-2025-001   | REF-BANESCO-001 | BANESCO         | TRANSACTION | IN_PROGRESS | Juan Pérez García         |
| TRX-2025-002   | REF-BANESCO-002 | BANESCO         | TRANSACTION | COMPLETED   | María González López      |
| TRX-2025-003   | REF-BANESCO-003 | BANESCO         | TRANSACTION | IN_PROGRESS | Carlos Rodríguez Martínez |
| TRX-2025-004   | REF-BANESCO-004 | BANESCO         | COMMISSION  | COMPLETED   | Ana Fernández Silva       |
| TRX-2025-005   | REF-MOBILE-001  | MOBILE_TRANSFER | TRANSACTION | TO_REVIEW   | Luis Morales Castro       |

---

## 🎯 Enumeraciones

### Bank Types
```python
class Bank(str, Enum):
    BANESCO = "BANESCO"
    MOBILE_TRANSFER = "MOBILE_TRANSFER"
```

### Transaction Types
```python
class TransactionType(str, Enum):
    TRANSACTION = "TRANSACTION"
    COMMISSION = "COMMISSION"
    OTHER = "OTHER"
```

### Transaction Status
```python
class TransactionStatus(str, Enum):
    IN_PROGRESS = "IN_PROGRESS"
    WAITING_APPROVAL = "WAITING_APPROVAL"
    APPROVED = "APPROVED"
    COMPLETED = "COMPLETED"
    REJECTED = "REJECTED"
    CANCELLED = "CANCELLED"
    TO_REVIEW = "TO_REVIEW"
    REVIEWED = "REVIEWED"
```

---

## 📊 Referencia de CSV

El archivo [`api_requests_responses.csv`](./api_requests_responses.csv) contiene ejemplos completos de todas las peticiones y respuestas probadas en la API.

**Estructura del CSV**:
- `Endpoint`: URL del endpoint
- `Method`: Método HTTP (GET, POST, etc.)
- `Description`: Descripción del endpoint
- `Request Body`: Cuerpo de la petición (si aplica)
- `Response Example`: Respuesta de ejemplo
- `Status Code`: Código HTTP de respuesta
- `Notes`: Notas adicionales

**Uso recomendado**: Este archivo es útil para:
- Ver ejemplos rápidos de requests/responses
- Importar en Postman o herramientas similares
- Documentación de referencia rápida
- Testing automatizado

---

## 🔧 Guía de Integración

### Paso 1: Obtener Token JWT

```bash
# Login y guardar token
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@areamedica.com","password":"Admin123!"}' \
  | jq -r '.access_token' > token.txt

# O usar variable de entorno
TOKEN=$(curl -s -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@areamedica.com","password":"Admin123!"}' \
  | jq -r '.access_token')
```

### Paso 2: Usar Token en Requests

```bash
# Opción 1: Desde archivo
curl -H "Authorization: Bearer $(cat token.txt)" \
  http://localhost:8000/api/v1/auth/me

# Opción 2: Desde variable
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/v1/transactions
```

### Paso 3: Manejo de Errores

```bash
# Capturar y mostrar errores
response=$(curl -s -w "\n%{http_code}" \
  -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/v1/transactions/reference/INVALID)

status_code=$(echo "$response" | tail -n1)
body=$(echo "$response" | sed '$d')

if [ "$status_code" != "200" ]; then
  echo "Error $status_code: $body"
  error_code=$(echo "$body" | jq -r '.detail.error_code')
  message=$(echo "$body" | jq -r '.detail.message')
  echo "Error Code: $error_code"
  echo "Message: $message"
fi
```

### Paso 4: Crear Transacciones

```bash
curl -X POST http://localhost:8000/api/v1/transactions \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "transaction_id": "TRX-NEW-001",
    "reference": "REF-NEW-001",
    "bank": "BANESCO",
    "transaction_type": "TRANSACTION",
    "customer_full_name": "Nuevo Cliente",
    "customer_phone": "04241234567",
    "customer_national_id": "V11111111",
    "concept": "Nueva transacción",
    "extra_data": {"source": "api_integration"}
  }'
```

---

## 🔒 Mejores Prácticas

1. **Siempre usar HTTPS en producción**
2. **Nunca exponer tokens en logs o URLs**
3. **Validar expiración de tokens** (campo `exp` en JWT)
4. **Implementar retry logic** para errores 5xx
5. **Respetar rate limits** del servidor
6. **Manejar todos los códigos de error** estandarizados
7. **Usar variables de entorno** para credenciales
8. **Implementar timeout** en requests HTTP

---

## 📚 Recursos Adicionales

- **Frontend Auth Guide**: Ver [`FRONTEND_AUTH_GUIDE.md`](./FRONTEND_AUTH_GUIDE.md) para integración con JavaScript/TypeScript
- **CSV Reference**: Ver [`api_requests_responses.csv`](./api_requests_responses.csv) para ejemplos completos
- **JWT Debugger**: [https://jwt.io/](https://jwt.io/)
- **API Standards**: [RFC 7807 - Problem Details](https://datatracker.ietf.org/doc/html/rfc7807)

---

**Actualizado**: 12 de Octubre 2025  
**Mantenido por**: AreaMédica Development Team

