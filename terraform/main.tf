# AreaMédica API - Terraform Infrastructure
# DigitalOcean Provider
# Version: 1.0.0

terraform {
  required_version = ">= 1.0"

  required_providers {
    digitalocean = {
      source  = "digitalocean/digitalocean"
      version = "~> 2.30"
    }
  }

  # Backend configuration for state management
  backend "s3" {
    bucket                      = "areamedica-terraform-state"
    key                         = "production/terraform.tfstate"
    region                      = "us-east-1"
    endpoint                    = "nyc3.digitaloceanspaces.com"
    skip_credentials_validation = true
    skip_metadata_api_check     = true
  }
}

provider "digitalocean" {
  token = var.do_token
}

# VPC for network isolation
resource "digitalocean_vpc" "main" {
  name     = "${var.project_name}-vpc-${var.environment}"
  region   = var.region
  ip_range = var.vpc_ip_range

  tags = var.tags
}

# PostgreSQL Database Cluster
resource "digitalocean_database_cluster" "postgres" {
  name       = "${var.project_name}-db-${var.environment}"
  engine     = "pg"
  version    = "15"
  size       = var.db_size
  region     = var.region
  node_count = var.db_node_count

  private_network_uuid = digitalocean_vpc.main.id

  tags = var.tags

  # Maintenance window (Sunday 2 AM UTC)
  maintenance_window {
    day  = "sunday"
    hour = "02:00:00"
  }
}

# Database for the application
resource "digitalocean_database_db" "areamedica" {
  cluster_id = digitalocean_database_cluster.postgres.id
  name       = var.db_name
}

# Database user
resource "digitalocean_database_user" "app_user" {
  cluster_id = digitalocean_database_cluster.postgres.id
  name       = var.db_user
}

# Redis Cache Cluster
resource "digitalocean_database_cluster" "redis" {
  name       = "${var.project_name}-redis-${var.environment}"
  engine     = "redis"
  version    = "7"
  size       = var.redis_size
  region     = var.region
  node_count = 1

  private_network_uuid = digitalocean_vpc.main.id

  tags = var.tags
}

# Droplet for application server
resource "digitalocean_droplet" "app_server" {
  count = var.app_server_count

  image    = "ubuntu-22-04-x64"
  name     = "${var.project_name}-app-${var.environment}-${count.index + 1}"
  region   = var.region
  size     = var.droplet_size
  vpc_uuid = digitalocean_vpc.main.id

  ssh_keys = var.ssh_keys

  user_data = templatefile("${path.module}/cloud-init.yml", {
    docker_compose_version = var.docker_compose_version
    project_name           = var.project_name
    environment            = var.environment
    postgres_host          = digitalocean_database_cluster.postgres.private_host
    postgres_port          = digitalocean_database_cluster.postgres.port
    postgres_user          = digitalocean_database_user.app_user.name
    postgres_password      = digitalocean_database_user.app_user.password
    postgres_db            = digitalocean_database_db.areamedica.name
    redis_host             = digitalocean_database_cluster.redis.private_host
    redis_port             = digitalocean_database_cluster.redis.port
    redis_password         = digitalocean_database_cluster.redis.password
  })

  tags = var.tags
}

# Load Balancer
resource "digitalocean_loadbalancer" "app_lb" {
  name   = "${var.project_name}-lb-${var.environment}"
  region = var.region

  vpc_uuid = digitalocean_vpc.main.id

  forwarding_rule {
    entry_port     = 443
    entry_protocol = "https"

    target_port     = 8000
    target_protocol = "http"

    certificate_id = digitalocean_certificate.app_cert.id
  }

  forwarding_rule {
    entry_port     = 80
    entry_protocol = "http"

    target_port     = 8000
    target_protocol = "http"
  }

  healthcheck {
    port     = 8000
    protocol = "http"
    path     = "/health"

    check_interval_seconds   = 10
    response_timeout_seconds = 5
    healthy_threshold        = 3
    unhealthy_threshold      = 3
  }

  droplet_ids = digitalocean_droplet.app_server[*].id

  tags = var.tags
}

# SSL Certificate
resource "digitalocean_certificate" "app_cert" {
  name    = "${var.project_name}-cert-${var.environment}"
  type    = "lets_encrypt"
  domains = var.domains
}

# Firewall
resource "digitalocean_firewall" "app_firewall" {
  name = "${var.project_name}-firewall-${var.environment}"

  droplet_ids = digitalocean_droplet.app_server[*].id

  # Inbound Rules
  inbound_rule {
    protocol         = "tcp"
    port_range       = "22"
    source_addresses = var.ssh_allowed_ips
  }

  inbound_rule {
    protocol                  = "tcp"
    port_range                = "8000"
    source_load_balancer_uids = [digitalocean_loadbalancer.app_lb.id]
  }

  inbound_rule {
    protocol         = "tcp"
    port_range       = "9090"
    source_addresses = var.monitoring_allowed_ips
  }

  # Outbound Rules
  outbound_rule {
    protocol              = "tcp"
    port_range            = "1-65535"
    destination_addresses = ["0.0.0.0/0", "::/0"]
  }

  outbound_rule {
    protocol              = "udp"
    port_range            = "1-65535"
    destination_addresses = ["0.0.0.0/0", "::/0"]
  }

  outbound_rule {
    protocol              = "icmp"
    destination_addresses = ["0.0.0.0/0", "::/0"]
  }

  tags = var.tags
}

# Monitoring Droplet (Prometheus + Grafana)
resource "digitalocean_droplet" "monitoring" {
  count = var.enable_monitoring ? 1 : 0

  image    = "ubuntu-22-04-x64"
  name     = "${var.project_name}-monitoring-${var.environment}"
  region   = var.region
  size     = var.monitoring_droplet_size
  vpc_uuid = digitalocean_vpc.main.id

  ssh_keys = var.ssh_keys

  user_data = templatefile("${path.module}/monitoring-init.yml", {
    project_name = var.project_name
    environment  = var.environment
  })

  tags = var.tags
}

# Spaces (Object Storage) for backups
resource "digitalocean_spaces_bucket" "backups" {
  name   = "${var.project_name}-backups-${var.environment}"
  region = var.spaces_region

  acl = "private"

  tags = var.tags
}

# DNS Configuration
resource "digitalocean_domain" "main" {
  count = var.create_domain ? 1 : 0

  name = var.primary_domain
}

resource "digitalocean_record" "app_a_record" {
  count = var.create_domain ? 1 : 0

  domain = digitalocean_domain.main[0].name
  type   = "A"
  name   = "api"
  value  = digitalocean_loadbalancer.app_lb.ip
  ttl    = 300
}

resource "digitalocean_record" "monitoring_a_record" {
  count = var.enable_monitoring && var.create_domain ? 1 : 0

  domain = digitalocean_domain.main[0].name
  type   = "A"
  name   = "monitoring"
  value  = digitalocean_droplet.monitoring[0].ipv4_address
  ttl    = 300
}

# Project
resource "digitalocean_project" "main" {
  name        = "${var.project_name}-${var.environment}"
  description = "AreaMédica API Infrastructure - ${title(var.environment)}"
  purpose     = "Web Application"
  environment = title(var.environment)

  resources = concat(
    digitalocean_droplet.app_server[*].urn,
    [
      digitalocean_database_cluster.postgres.urn,
      digitalocean_database_cluster.redis.urn,
      digitalocean_loadbalancer.app_lb.urn,
    ],
    var.enable_monitoring ? [digitalocean_droplet.monitoring[0].urn] : [],
    [digitalocean_spaces_bucket.backups.urn]
  )
}

# Kubernetes Cluster (Optional - for future scaling)
resource "digitalocean_kubernetes_cluster" "main" {
  count = var.enable_kubernetes ? 1 : 0

  name    = "${var.project_name}-k8s-${var.environment}"
  region  = var.region
  version = var.k8s_version

  vpc_uuid = digitalocean_vpc.main.id

  node_pool {
    name       = "worker-pool"
    size       = var.k8s_node_size
    node_count = var.k8s_node_count
    auto_scale = true
    min_nodes  = var.k8s_min_nodes
    max_nodes  = var.k8s_max_nodes

    tags = var.tags
  }

  tags = var.tags
}
