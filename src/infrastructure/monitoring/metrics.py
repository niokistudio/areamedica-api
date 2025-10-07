"""Prometheus metrics configuration."""

from prometheus_client import Counter, Gauge, Histogram

# HTTP Request Metrics
http_requests_total = Counter(
    "http_requests_total",
    "Total HTTP requests",
    ["method", "endpoint", "status_code"],
)

http_request_duration_seconds = Histogram(
    "http_request_duration_seconds",
    "HTTP request duration in seconds",
    ["method", "endpoint"],
    buckets=(0.01, 0.025, 0.05, 0.075, 0.1, 0.25, 0.5, 0.75, 1.0, 2.5, 5.0, 7.5, 10.0),
)

http_requests_in_progress = Gauge(
    "http_requests_in_progress",
    "Number of HTTP requests in progress",
    ["method", "endpoint"],
)

# Business Metrics
transactions_total = Counter(
    "transactions_total",
    "Total transactions processed",
    ["status", "bank", "transaction_type"],
)

transactions_in_progress = Gauge(
    "transactions_in_progress",
    "Number of transactions currently in progress",
)

transaction_processing_duration_seconds = Histogram(
    "transaction_processing_duration_seconds",
    "Transaction processing duration",
    ["bank", "transaction_type"],
    buckets=(0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 30.0, 60.0),
)

# Banesco API Metrics
banesco_api_calls_total = Counter(
    "banesco_api_calls_total",
    "Total calls to Banesco API",
    ["operation", "status"],
)

banesco_api_duration_seconds = Histogram(
    "banesco_api_duration_seconds",
    "Banesco API call duration",
    ["operation"],
    buckets=(0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 30.0),
)

banesco_api_errors_total = Counter(
    "banesco_api_errors_total",
    "Total Banesco API errors",
    ["error_type"],
)

banesco_rate_limit_exceeded_total = Counter(
    "banesco_rate_limit_exceeded_total",
    "Total Banesco rate limit violations",
    ["transaction_id"],
)

# Authentication Metrics
auth_attempts_total = Counter(
    "auth_attempts_total",
    "Total authentication attempts",
    ["result"],  # success, failure
)

active_sessions = Gauge(
    "active_sessions",
    "Number of active user sessions",
)

token_validations_total = Counter(
    "token_validations_total",
    "Total JWT token validations",
    ["result"],  # valid, invalid, expired
)

# Database Metrics
db_queries_total = Counter(
    "db_queries_total",
    "Total database queries",
    ["operation", "table"],
)

db_query_duration_seconds = Histogram(
    "db_query_duration_seconds",
    "Database query duration",
    ["operation", "table"],
    buckets=(0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0),
)

db_connection_pool_size = Gauge(
    "db_connection_pool_size",
    "Database connection pool size",
)

db_connection_pool_available = Gauge(
    "db_connection_pool_available",
    "Available database connections in pool",
)

# Cache Metrics
cache_operations_total = Counter(
    "cache_operations_total",
    "Total cache operations",
    ["operation", "result"],  # operation: get, set, delete; result: hit, miss, error
)

cache_hit_ratio = Gauge(
    "cache_hit_ratio",
    "Cache hit ratio (0-1)",
)

# Application Health
app_info = Gauge(
    "app_info",
    "Application information",
    ["version", "environment"],
)

app_up = Gauge(
    "app_up",
    "Application up status (1=up, 0=down)",
)
