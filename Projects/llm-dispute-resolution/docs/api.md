# API Surface

This document specifies the MVP and near-term Phase 2 REST endpoints, request/response schemas, and error model.

## 1. Conventions
- Base path: `/v1`
- Auth (optional MVP toggle): `X-API-Key: <token>` header
- Content-Type: `application/json`
- Correlation id: Response header `X-Request-ID`

## 2. Endpoints
### 2.1 POST /v1/disputes
Create & process a dispute synchronously (MVP) or enqueue (future flag `async=true`).

Request Body:
```json
{
	"external_ref": "CASE-12345",
	"customer_id": "c-789",
	"merchant_id": "m-456",
	"amount": 2599,
	"currency": "USD",
	"narrative": "I did not authorize this transaction at StoreXYZ yesterday."
}
```
Validation Rules:
- amount > 0; currency ISO-4217 3 chars
- narrative length ≤ 2000 (truncate & flag)

Response 201:
```json
{
	"id": "dsp_123",
	"external_ref": "CASE-12345",
	"classification": {"label": "FRAUD_UNAUTHORIZED", "confidence": 0.88},
	"recommendation": {"action": "REFUND", "confidence": 0.81, "rationale": "..."},
	"truncated": false,
	"latency_ms": 1270
}
```

### 2.2 GET /v1/disputes/{id}
Fetch stored case details.
Response 200:
```json
{
	"id": "dsp_123",
	"external_ref": "CASE-12345",
	"classification": {"label": "FRAUD_UNAUTHORIZED", "confidence": 0.88},
	"recommendation": {"action": "REFUND", "confidence": 0.81, "rationale": "..."},
	"created_at": "2025-10-08T10:10:00Z"
}
```

### 2.3 GET /v1/metrics
Returns JSON counters (MVP). Response 200:
```json
{
	"total_cases": 152,
	"classification_latency_ms_p95": 2310,
	"recommendation_latency_ms_p95": 2875,
	"cases_by_label": {"FRAUD_UNAUTHORIZED": 80, "MERCHANT_ERROR": 40, "OTHER": 32},
	"avg_cost_per_case_usd": 0.37
}
```

### 2.4 (Phase 2) GET /v1/disputes/{id}/audit
List audit events for case.
Response 200:
```json
{
	"case_id": "dsp_123",
	"events": [
		{"step": "classification", "timestamp": "...", "latency_ms": 850},
		{"step": "enrichment", "timestamp": "...", "latency_ms": 620}
	]
}
```

### 2.5 (Phase 2) POST /v1/disputes/{id}/decision
Persist analyst final decision & optional override.
Request:
```json
{
	"final_action": "REFUND",
	"override": false,
	"notes": "Reviewed – aligns with policy"
}
```
Response 202:
```json
{"status": "accepted", "case_id": "dsp_123"}
```

## 3. Error Model
Standard error response:
```json
{
	"error": {
		"code": "VALIDATION_ERROR",
		"message": "currency must be 3 letters",
		"request_id": "6f2e...",
		"details": {"field": "currency"}
	}
}
```

Error Codes (initial):
| Code | HTTP | Meaning |
|------|------|---------|
VALIDATION_ERROR | 400 | Input invalid |
NOT_FOUND | 404 | Resource missing |
UNAUTHORIZED | 401 | Missing/invalid API key |
RATE_LIMITED | 429 | Too many requests (future) |
INTERNAL_ERROR | 500 | Unhandled server error |
UPSTREAM_TIMEOUT | 504 | LLM or external call timeout |

## 4. Pagination & Filtering (Future)
`GET /v1/disputes?status=COMPLETED&limit=50&cursor=...`

## 5. Idempotency
Future: `Idempotency-Key` header for dispute submissions to avoid duplicate creation on retry.

## 6. Versioning
Breaking changes -> /v2; additive fields within same major version allowed. Changelog appended to docs.

## 7. OpenAPI Generation
FastAPI auto docs at `/docs` (Swagger UI) & `/openapi.json`. Commit a frozen spec snapshot per release under `docs/openapi/`.

---
Version: 1.0.0 | Owner: API Engineering | Status: Draft

