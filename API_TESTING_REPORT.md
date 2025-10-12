# API Endpoints Testing Report

**Fecha**: 12 de Octubre 2025  
**API Version**: 1.0.0  
**Base URL**: `http://localhost:8000`

## 📊 Resumen Ejecutivo

✅ **Endpoints Probados**: 12  
✅ **Tests Exitosos**: 12/12 (100%)  
✅ **Errores Estandarizados**: Implementados  
✅ **Autenticación JWT**: Funcionando correctamente

---

## 🔐 Autenticación

### 1. Login
**Endpoint**: `POST /api/v1/auth/login`

**Request Body**:
```json
{
  "email": "admin@areamedica.com",
  "password": "Admin123!"
}
```

**Response (200 OK)**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**Curl Example**:
```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@areamedica.com","password":"Admin123!"}'
```

---

### 2. Register
**Endpoint**: `POST /api/v1/auth/register`

**Request Body**:
```json
{
  "email": "newuser@test.com",
  "password": "Test123!",
  "full_name": "Test User"
}
```

**Response (201 Created)**:
```json
{
  "id": "e3a77661-f208-4f71-ad2f-3da9c5cc8751",
  "email": "newuser@test.com",
  "full_name": "Test User",
  "is_active": true,
  "permissions": []
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

---

### 3. Get Current User
**Endpoint**: `GET /api/v1/auth/me`

**Headers**: `Authorization: Bearer {token}`

**Response (200 OK)**:
```json
{
  "id": "05e7bf52-4e7f-4a19-b9cc-e549d0187e87",
  "email": "admin@areamedica.com",
  "full_name": "Administrador Sistema",
  "is_active": true,
  "permissions": []
}
```

**Curl Example**:
```bash
TOKEN="your_jwt_token_here"
curl -X GET http://localhost:8000/api/v1/auth/me \
  -H "Authorization: Bearer $TOKEN"
```

---

## 💳 Transacciones

### 4. Get All Transactions
**Endpoint**: `GET /api/v1/transactions`

**Query Parameters**:
- `page` (optional): Page number (default: 1)
- `limit` (optional): Items per page (default: 10)

**Headers**: `Authorization: Bearer {token}`

**Response (200 OK)**:
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
  ]
}
```

**Curl Example**:
```bash
curl -X GET "http://localhost:8000/api/v1/transactions?page=1&limit=10" \
  -H "Authorization: Bearer $TOKEN"
```

---

### 5. Get Transaction by UUID
**Endpoint**: `GET /api/v1/transactions/{id}`

**Path Parameters**:
- `id`: UUID of the transaction

**Headers**: `Authorization: Bearer {token}`

**Response (200 OK)**: Same structure as single transaction above

**Curl Example**:
```bash
curl -X GET "http://localhost:8000/api/v1/transactions/b2cd7a2c-655d-40d0-9cd0-321eddfbba89" \
  -H "Authorization: Bearer $TOKEN"
```

---

### 6. Get Transaction by transaction_id
**Endpoint**: `GET /api/v1/transactions/external/{transaction_id}`

**Path Parameters**:
- `transaction_id`: External transaction ID (e.g., "TRX-2025-001")

**Headers**: `Authorization: Bearer {token}`

**Response (200 OK)**: Same structure as single transaction

**Curl Example**:
```bash
curl -X GET "http://localhost:8000/api/v1/transactions/external/TRX-2025-001" \
  -H "Authorization: Bearer $TOKEN"
```

---

### 7. Get Transaction by Reference
**Endpoint**: `GET /api/v1/transactions/reference/{reference}`

**Path Parameters**:
- `reference`: Transaction reference (e.g., "REF-BANESCO-001")

**Headers**: `Authorization: Bearer {token}`

**Response (200 OK)**: Same structure as single transaction

**Curl Example**:
```bash
curl -X GET "http://localhost:8000/api/v1/transactions/reference/REF-BANESCO-001" \
  -H "Authorization: Bearer $TOKEN"
```

---

### 8. Create Transaction
**Endpoint**: `POST /api/v1/transactions`

**Headers**:
- `Authorization: Bearer {token}`
- `Content-Type: application/json`

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

**Response (201 Created)**:
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

---

## ❌ Manejo de Errores Estandarizado

Todos los errores ahora siguen un formato consistente con `error_code` y `message`:

### Invalid Credentials (401)
```json
{
  "detail": {
    "error_code": "INVALID_CREDENTIALS",
    "message": "Invalid email or password"
  }
}
```

### Unauthorized (401)
```json
{
  "detail": {
    "error_code": "UNAUTHORIZED",
    "message": "Not authenticated"
  }
}
```

### Not Found (404)
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

### Already Exists (409)
```json
{
  "detail": {
    "error_code": "CONFLICT",
    "message": "User already exists",
    "details": {
      "resource": "User",
      "identifier": "user@email.com"
    }
  }
}
```

---

## 🏥 Health Check

### Health Endpoint
**Endpoint**: `GET /health`

**Response (200 OK)**:
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

---

## 📝 Datos de Prueba (Seed Data)

### Usuarios de Prueba

| Email                  | Password  | Role  | Full Name             |
| ---------------------- | --------- | ----- | --------------------- |
| admin@areamedica.com   | Admin123! | Admin | Administrador Sistema |
| usuario@areamedica.com | User123!  | User  | Usuario Regular       |
| test@areamedica.com    | Test123!  | User  | Usuario de Prueba     |

### Transacciones de Prueba

| transaction_id | Reference       | Bank            | Status      | Customer                  |
| -------------- | --------------- | --------------- | ----------- | ------------------------- |
| TRX-2025-001   | REF-BANESCO-001 | BANESCO         | IN_PROGRESS | Juan Pérez García         |
| TRX-2025-002   | REF-BANESCO-002 | BANESCO         | COMPLETED   | María González López      |
| TRX-2025-003   | REF-BANESCO-003 | BANESCO         | IN_PROGRESS | Carlos Rodríguez Martínez |
| TRX-2025-004   | REF-BANESCO-004 | BANESCO         | COMPLETED   | Ana Fernández Silva       |
| TRX-2025-005   | REF-MOBILE-001  | MOBILE_TRANSFER | TO_REVIEW   | Luis Morales Castro       |

---

## 🎯 Enumeraciones

### Bank Types
- `BANESCO`
- `MOBILE_TRANSFER`

### Transaction Types
- `TRANSACTION`
- `COMMISSION`
- `OTHER`

### Transaction Status
- `IN_PROGRESS`
- `WAITING_APPROVAL`
- `APPROVED`
- `COMPLETED`
- `REJECTED`
- `CANCELLED`
- `TO_REVIEW`
- `REVIEWED`

---

## 🔧 Próximos Pasos

1. ✅ **Estandarizar mensajes de error HTTP** - Completado
2. ✅ **Crear seed data para testing** - Completado
3. ✅ **Generar CSV con requests/responses** - Completado
4. ⏳ **Actualizar endpoints de transactions con excepciones estandarizadas**
5. ⏳ **Documentar flujo de autenticación para frontend**
6. ⏳ **Preparar deployment en Render**

---

## 📚 Archivos Generados

- `test_endpoints.sh` - Script bash para pruebas automáticas
- `generate_api_csv.sh` - Script para generar CSV con ejemplos
- `api_requests_responses.csv` - CSV con todos los requests y responses
- `API_TESTING_REPORT.md` - Este documento

---

**Generado el**: 12 de Octubre 2025  
**Estado del Proyecto**: ✅ Testing Phase Completed
