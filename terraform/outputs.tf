# AreaMédica API - Terraform Outputs
# Version: 1.0.0

# ============================================================================
# Network Outputs
# ============================================================================

output "vpc_id" {
  description = "VPC ID"
  value       = digitalocean_vpc.main.id
}

output "vpc_ip_range" {
  description = "VPC IP range"
  value       = digitalocean_vpc.main.ip_range
}

# ============================================================================
# Database Outputs
# ============================================================================

output "postgres_host" {
  description = "PostgreSQL private host"
  value       = digitalocean_database_cluster.postgres.private_host
  sensitive   = true
}

output "postgres_port" {
  description = "PostgreSQL port"
  value       = digitalocean_database_cluster.postgres.port
}

output "postgres_user" {
  description = "PostgreSQL user"
  value       = digitalocean_database_user.app_user.name
}

output "postgres_password" {
  description = "PostgreSQL password"
  value       = digitalocean_database_user.app_user.password
  sensitive   = true
}

output "postgres_database" {
  description = "PostgreSQL database name"
  value       = digitalocean_database_db.areamedica.name
}

output "postgres_connection_string" {
  description = "PostgreSQL connection string"
  value       = "postgresql://${digitalocean_database_user.app_user.name}:${digitalocean_database_user.app_user.password}@${digitalocean_database_cluster.postgres.private_host}:${digitalocean_database_cluster.postgres.port}/${digitalocean_database_db.areamedica.name}"
  sensitive   = true
}

# ============================================================================
# Redis Outputs
# ============================================================================

output "redis_host" {
  description = "Redis private host"
  value       = digitalocean_database_cluster.redis.private_host
  sensitive   = true
}

output "redis_port" {
  description = "Redis port"
  value       = digitalocean_database_cluster.redis.port
}

output "redis_password" {
  description = "Redis password"
  value       = digitalocean_database_cluster.redis.password
  sensitive   = true
}

output "redis_connection_string" {
  description = "Redis connection string"
  value       = "redis://default:${digitalocean_database_cluster.redis.password}@${digitalocean_database_cluster.redis.private_host}:${digitalocean_database_cluster.redis.port}"
  sensitive   = true
}

# ============================================================================
# Compute Outputs
# ============================================================================

output "app_server_ids" {
  description = "Application server droplet IDs"
  value       = digitalocean_droplet.app_server[*].id
}

output "app_server_ips" {
  description = "Application server public IP addresses"
  value       = digitalocean_droplet.app_server[*].ipv4_address
}

output "app_server_private_ips" {
  description = "Application server private IP addresses"
  value       = digitalocean_droplet.app_server[*].ipv4_address_private
}

# ============================================================================
# Load Balancer Outputs
# ============================================================================

output "load_balancer_ip" {
  description = "Load balancer public IP address"
  value       = digitalocean_loadbalancer.app_lb.ip
}

output "load_balancer_id" {
  description = "Load balancer ID"
  value       = digitalocean_loadbalancer.app_lb.id
}

output "api_url" {
  description = "API URL"
  value       = "https://${digitalocean_loadbalancer.app_lb.ip}"
}

# ============================================================================
# SSL Certificate Outputs
# ============================================================================

output "ssl_certificate_id" {
  description = "SSL certificate ID"
  value       = digitalocean_certificate.app_cert.id
}

output "ssl_certificate_domains" {
  description = "SSL certificate domains"
  value       = digitalocean_certificate.app_cert.domains
}

# ============================================================================
# Monitoring Outputs
# ============================================================================

output "monitoring_droplet_id" {
  description = "Monitoring droplet ID"
  value       = var.enable_monitoring ? digitalocean_droplet.monitoring[0].id : null
}

output "monitoring_ip" {
  description = "Monitoring server public IP"
  value       = var.enable_monitoring ? digitalocean_droplet.monitoring[0].ipv4_address : null
}

output "prometheus_url" {
  description = "Prometheus URL"
  value       = var.enable_monitoring ? "http://${digitalocean_droplet.monitoring[0].ipv4_address}:9090" : null
}

output "grafana_url" {
  description = "Grafana URL"
  value       = var.enable_monitoring ? "http://${digitalocean_droplet.monitoring[0].ipv4_address}:3000" : null
}

# ============================================================================
# Storage Outputs
# ============================================================================

output "spaces_bucket_name" {
  description = "Spaces bucket name for backups"
  value       = digitalocean_spaces_bucket.backups.name
}

output "spaces_bucket_endpoint" {
  description = "Spaces bucket endpoint"
  value       = digitalocean_spaces_bucket.backups.bucket_domain_name
}

# ============================================================================
# DNS Outputs
# ============================================================================

output "domain_name" {
  description = "Primary domain name"
  value       = var.create_domain ? digitalocean_domain.main[0].name : null
}

output "api_domain" {
  description = "API domain name"
  value       = var.create_domain ? "api.${digitalocean_domain.main[0].name}" : null
}

output "monitoring_domain" {
  description = "Monitoring domain name"
  value       = var.enable_monitoring && var.create_domain ? "monitoring.${digitalocean_domain.main[0].name}" : null
}

# ============================================================================
# Project Outputs
# ============================================================================

output "project_id" {
  description = "DigitalOcean project ID"
  value       = digitalocean_project.main.id
}

output "project_name" {
  description = "Project name"
  value       = digitalocean_project.main.name
}

# ============================================================================
# Kubernetes Outputs (Optional)
# ============================================================================

output "k8s_cluster_id" {
  description = "Kubernetes cluster ID"
  value       = var.enable_kubernetes ? digitalocean_kubernetes_cluster.main[0].id : null
}

output "k8s_endpoint" {
  description = "Kubernetes API endpoint"
  value       = var.enable_kubernetes ? digitalocean_kubernetes_cluster.main[0].endpoint : null
}

output "k8s_cluster_ca_certificate" {
  description = "Kubernetes cluster CA certificate"
  value       = var.enable_kubernetes ? digitalocean_kubernetes_cluster.main[0].kube_config[0].cluster_ca_certificate : null
  sensitive   = true
}

# ============================================================================
# Summary Output
# ============================================================================

output "deployment_summary" {
  description = "Deployment summary"
  value = {
    environment          = var.environment
    region               = var.region
    app_servers          = var.app_server_count
    load_balancer_ip     = digitalocean_loadbalancer.app_lb.ip
    api_url              = var.create_domain && length(var.domains) > 0 ? "https://${var.domains[0]}" : "https://${digitalocean_loadbalancer.app_lb.ip}"
    monitoring_enabled   = var.enable_monitoring
    kubernetes_enabled   = var.enable_kubernetes
    database_nodes       = var.db_node_count
    vpc_id               = digitalocean_vpc.main.id
  }
}
