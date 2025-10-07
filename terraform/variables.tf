# AreaMédica API - Terraform Variables
# Version: 1.0.0

# ============================================================================
# General Variables
# ============================================================================

variable "do_token" {
  description = "DigitalOcean API Token"
  type        = string
  sensitive   = true
}

variable "project_name" {
  description = "Project name for resource naming"
  type        = string
  default     = "areamedica-api"
}

variable "environment" {
  description = "Environment name (dev, staging, production)"
  type        = string

  validation {
    condition     = contains(["dev", "staging", "production"], var.environment)
    error_message = "Environment must be dev, staging, or production."
  }
}

variable "region" {
  description = "DigitalOcean region"
  type        = string
  default     = "nyc3"
}

variable "tags" {
  description = "Tags to apply to all resources"
  type        = list(string)
  default     = ["areamedica", "api", "backend"]
}

# ============================================================================
# Network Variables
# ============================================================================

variable "vpc_ip_range" {
  description = "IP range for VPC"
  type        = string
  default     = "10.10.0.0/16"
}

# ============================================================================
# Database Variables
# ============================================================================

variable "db_size" {
  description = "Database cluster size"
  type        = string
  default     = "db-s-1vcpu-1gb"

  validation {
    condition     = can(regex("^db-", var.db_size))
    error_message = "Database size must be a valid DigitalOcean database slug."
  }
}

variable "db_node_count" {
  description = "Number of database nodes (1 or 2 for primary-standby)"
  type        = number
  default     = 1

  validation {
    condition     = var.db_node_count >= 1 && var.db_node_count <= 3
    error_message = "Database node count must be between 1 and 3."
  }
}

variable "db_name" {
  description = "Database name"
  type        = string
  default     = "areamedica"
}

variable "db_user" {
  description = "Database user"
  type        = string
  default     = "areamedica_app"
}

# ============================================================================
# Redis Variables
# ============================================================================

variable "redis_size" {
  description = "Redis cluster size"
  type        = string
  default     = "db-s-1vcpu-1gb"
}

# ============================================================================
# Compute Variables
# ============================================================================

variable "droplet_size" {
  description = "Droplet size for application servers"
  type        = string
  default     = "s-2vcpu-4gb"
}

variable "app_server_count" {
  description = "Number of application servers"
  type        = number
  default     = 2

  validation {
    condition     = var.app_server_count >= 1 && var.app_server_count <= 10
    error_message = "Application server count must be between 1 and 10."
  }
}

variable "ssh_keys" {
  description = "List of SSH key IDs or fingerprints"
  type        = list(string)
  default     = []
}

variable "ssh_allowed_ips" {
  description = "IP addresses allowed to SSH"
  type        = list(string)
  default     = ["0.0.0.0/0"]
}

variable "docker_compose_version" {
  description = "Docker Compose version to install"
  type        = string
  default     = "2.23.0"
}

# ============================================================================
# Load Balancer & SSL Variables
# ============================================================================

variable "domains" {
  description = "Domains for SSL certificate"
  type        = list(string)
  default     = ["api.areamedica.example.com"]
}

# ============================================================================
# DNS Variables
# ============================================================================

variable "create_domain" {
  description = "Whether to create DNS domain"
  type        = bool
  default     = false
}

variable "primary_domain" {
  description = "Primary domain name"
  type        = string
  default     = "areamedica.example.com"
}

# ============================================================================
# Monitoring Variables
# ============================================================================

variable "enable_monitoring" {
  description = "Enable dedicated monitoring droplet"
  type        = bool
  default     = true
}

variable "monitoring_droplet_size" {
  description = "Droplet size for monitoring server"
  type        = string
  default     = "s-2vcpu-2gb"
}

variable "monitoring_allowed_ips" {
  description = "IP addresses allowed to access monitoring"
  type        = list(string)
  default     = ["0.0.0.0/0"]
}

# ============================================================================
# Storage Variables
# ============================================================================

variable "spaces_region" {
  description = "DigitalOcean Spaces region"
  type        = string
  default     = "nyc3"
}

# ============================================================================
# Kubernetes Variables (Optional)
# ============================================================================

variable "enable_kubernetes" {
  description = "Enable Kubernetes cluster for future scaling"
  type        = bool
  default     = false
}

variable "k8s_version" {
  description = "Kubernetes version"
  type        = string
  default     = "1.28.2-do.0"
}

variable "k8s_node_size" {
  description = "Kubernetes node size"
  type        = string
  default     = "s-2vcpu-4gb"
}

variable "k8s_node_count" {
  description = "Initial Kubernetes node count"
  type        = number
  default     = 2
}

variable "k8s_min_nodes" {
  description = "Minimum Kubernetes nodes for autoscaling"
  type        = number
  default     = 2
}

variable "k8s_max_nodes" {
  description = "Maximum Kubernetes nodes for autoscaling"
  type        = number
  default     = 5
}
