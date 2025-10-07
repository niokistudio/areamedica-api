# AreaMédica API - Terraform Infrastructure

Infrastructure as Code (IaC) for deploying AreaMédica API to DigitalOcean.

## 📋 Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Configuration](#configuration)
- [Deployment](#deployment)
- [Outputs](#outputs)
- [Cost Estimation](#cost-estimation)
- [Maintenance](#maintenance)
- [Troubleshooting](#troubleshooting)

## 🏗️ Overview

This Terraform configuration provisions a complete, production-ready infrastructure on DigitalOcean including:

- **VPC**: Isolated network for resources
- **PostgreSQL 15**: Managed database cluster with optional standby
- **Redis 7**: Managed cache cluster
- **Load Balancer**: SSL termination and traffic distribution
- **Droplets**: Application servers (scalable)
- **Monitoring**: Prometheus + Grafana (optional)
- **Storage**: Spaces bucket for backups
- **DNS**: Automated domain configuration (optional)
- **Firewall**: Security rules for all resources

## 🏛️ Architecture

```
┌────────────────────────────────────────────────────────────┐
│                     DigitalOcean VPC                       │
│                                                            │
│  ┌──────────────┐         ┌──────────────┐               │
│  │ Load Balancer│◄────────┤   Internet   │               │
│  │  (SSL/HTTPS) │         └──────────────┘               │
│  └──────┬───────┘                                         │
│         │                                                 │
│  ┌──────▼────────────────────────────┐                    │
│  │   Application Servers (Droplets)  │                    │
│  │  ┌─────┐  ┌─────┐  ┌─────┐       │                    │
│  │  │ API │  │ API │  │ API │       │                    │
│  │  └──┬──┘  └──┬──┘  └──┬──┘       │                    │
│  └─────┼────────┼────────┼───────────┘                    │
│        │        │        │                                │
│  ┌─────▼────────▼────────▼─────┐    ┌──────────────┐     │
│  │  PostgreSQL Cluster (HA)    │    │ Redis Cache  │     │
│  │  Primary + Standby          │    │              │     │
│  └─────────────────────────────┘    └──────────────┘     │
│                                                            │
│  ┌───────────────────────┐     ┌──────────────────┐      │
│  │ Monitoring (Optional) │     │ Spaces (Backups) │      │
│  │ Prometheus + Grafana  │     │                  │      │
│  └───────────────────────┘     └──────────────────┘      │
└────────────────────────────────────────────────────────────┘
```

## ✅ Prerequisites

### Required Software

1. **Terraform**: >= 1.0
   ```bash
   # Download from: https://www.terraform.io/downloads
   terraform --version
   ```

2. **DigitalOcean Account**: Active account with payment method

3. **DigitalOcean API Token**:
   - Go to: https://cloud.digitalocean.com/account/api/tokens
   - Create a new Personal Access Token
   - Save securely (required for deployment)

4. **SSH Key** (for server access):
   ```bash
   # Generate SSH key if you don't have one
   ssh-keygen -t ed25519 -C "your_email@example.com"
   
   # Add to DigitalOcean
   # Go to: https://cloud.digitalocean.com/account/security
   ```

### Optional

- **Domain Name**: For custom domain setup
- **Slack Webhook**: For deployment notifications (CI/CD)

## 🚀 Quick Start

### 1. Clone Repository

```bash
git clone https://github.com/your-org/areamedica-api.git
cd areamedica-api/terraform
```

### 2. Configure Variables

```bash
# Copy example configuration
cp terraform.tfvars.example terraform.tfvars

# Edit with your values
nano terraform.tfvars
```

**Required Variables**:
```hcl
# terraform.tfvars
do_token = "your_digitalocean_api_token"  # Or set as environment variable

ssh_keys = [
  "your-ssh-key-fingerprint"  # Get from: doctl compute ssh-key list
]

domains = [
  "api.yourdomain.com"
]
```

### 3. Initialize Terraform

```bash
terraform init
```

### 4. Review Plan

```bash
terraform plan
```

### 5. Deploy Infrastructure

```bash
terraform apply
```

### 6. Save Outputs

```bash
# Save sensitive outputs to file (keep secure!)
terraform output -json > outputs.json

# Get specific outputs
terraform output load_balancer_ip
terraform output postgres_connection_string
terraform output api_url
```

## ⚙️ Configuration

### Environment Variables

Set sensitive values as environment variables instead of `terraform.tfvars`:

```bash
export TF_VAR_do_token="your_digitalocean_api_token"
export TF_VAR_ssh_keys='["your-ssh-key-fingerprint"]'
```

### Key Variables

| Variable            | Description           | Default          | Production Recommended |
| ------------------- | --------------------- | ---------------- | ---------------------- |
| `environment`       | Environment name      | -                | `production`           |
| `region`            | DigitalOcean region   | `nyc3`           | `nyc3` or nearest      |
| `app_server_count`  | Number of API servers | 2                | 3-5                    |
| `droplet_size`      | Server size           | `s-2vcpu-4gb`    | `s-2vcpu-4gb`          |
| `db_size`           | Database size         | `db-s-1vcpu-1gb` | `db-s-2vcpu-4gb`       |
| `db_node_count`     | DB nodes (HA)         | 1                | 2                      |
| `enable_monitoring` | Prometheus+Grafana    | `true`           | `true`                 |
| `create_domain`     | Configure DNS         | `false`          | `true`                 |

### Sizing Guide

**Development/Staging**:
```hcl
droplet_size     = "s-1vcpu-2gb"   # $12/month each
app_server_count = 1
db_size          = "db-s-1vcpu-1gb"  # $15/month
db_node_count    = 1
redis_size       = "db-s-1vcpu-1gb"  # $15/month
```

**Production**:
```hcl
droplet_size     = "s-2vcpu-4gb"   # $24/month each
app_server_count = 3
db_size          = "db-s-2vcpu-4gb"  # $60/month
db_node_count    = 2               # $120/month (HA)
redis_size       = "db-s-1vcpu-2gb"  # $30/month
```

## 📦 Deployment

### Initial Deployment

```bash
# 1. Validate configuration
terraform validate

# 2. Format code
terraform fmt -recursive

# 3. Plan changes
terraform plan -out=tfplan

# 4. Apply plan
terraform apply tfplan

# 5. Verify deployment
terraform output deployment_summary
```

### Update Deployment

```bash
# Update variables or configuration
nano terraform.tfvars

# Plan and apply changes
terraform plan
terraform apply
```

### Scaling

**Scale Application Servers**:
```bash
# Edit terraform.tfvars
app_server_count = 5

terraform apply
```

**Enable High Availability for Database**:
```bash
# Edit terraform.tfvars
db_node_count = 2  # Adds standby replica

terraform apply
```

### Destroy Infrastructure

```bash
# ⚠️ WARNING: This deletes EVERYTHING
terraform destroy
```

## 📤 Outputs

After deployment, access outputs:

```bash
# All outputs
terraform output

# Specific output
terraform output load_balancer_ip
terraform output postgres_host
terraform output redis_host

# Sensitive outputs
terraform output -raw postgres_password
terraform output -raw redis_password

# JSON format
terraform output -json > outputs.json
```

### Key Outputs

- `load_balancer_ip`: Public IP for API access
- `api_url`: Full API URL (https://...)
- `app_server_ips`: Application server IPs for SSH
- `postgres_connection_string`: Database connection (sensitive)
- `redis_connection_string`: Redis connection (sensitive)
- `prometheus_url`: Metrics dashboard
- `grafana_url`: Grafana dashboard

## 💰 Cost Estimation

### Monthly Costs (Production Setup)

| Resource                | Spec          | Count | Unit Cost | Total        |
| ----------------------- | ------------- | ----- | --------- | ------------ |
| **Application Servers** | 2 vCPU, 4 GB  | 3     | $24/mo    | $72/mo       |
| **PostgreSQL (HA)**     | 2 vCPU, 4 GB  | 2     | $60/mo    | $120/mo      |
| **Redis**               | 1 vCPU, 2 GB  | 1     | $30/mo    | $30/mo       |
| **Load Balancer**       | -             | 1     | $12/mo    | $12/mo       |
| **Monitoring**          | 2 vCPU, 2 GB  | 1     | $18/mo    | $18/mo       |
| **Spaces (100 GB)**     | Storage       | 1     | $5/mo     | $5/mo        |
| **Bandwidth**           | 1 TB included | -     | Free      | $0           |
|                         |               |       | **Total** | **~$257/mo** |

### Development Setup: ~$60/mo
### Staging Setup: ~$120/mo
### Enterprise Setup: ~$500+/mo

## 🔧 Maintenance

### Backups

**Automated Database Backups**:
- Daily backups enabled by default
- 7-day retention
- Stored in DigitalOcean managed service

**Manual Backup**:
```bash
# SSH into app server
ssh root@$(terraform output -raw app_server_ips | jq -r '.[0]')

# Backup database
docker-compose exec api pg_dump -U $POSTGRES_USER $POSTGRES_DB > backup.sql

# Upload to Spaces
aws s3 cp backup.sql s3://$(terraform output -raw spaces_bucket_name)/backups/
```

### Updates

**Application Updates**:
```bash
# SSH to server
ssh root@SERVER_IP

# Run deployment script
/root/deploy.sh
```

**Infrastructure Updates**:
```bash
# Update Terraform configuration
git pull origin main

# Apply changes
terraform apply
```

### Monitoring

**Prometheus**: `http://MONITORING_IP:9090`
**Grafana**: `http://MONITORING_IP:3000` (admin/admin)

### SSL Certificate Renewal

Automatic renewal via Let's Encrypt (managed by DigitalOcean).

## 🐛 Troubleshooting

### Common Issues

**Issue**: `Error creating droplet: invalid size`
```bash
# Solution: Check valid sizes
doctl compute size list --region nyc3
```

**Issue**: `Error: ssh key not found`
```bash
# Solution: List your SSH keys
doctl compute ssh-key list

# Copy fingerprint and update terraform.tfvars
```

**Issue**: `Database cluster creation failed`
```bash
# Solution: Check region availability
doctl databases options regions
doctl databases options sizes
```

**Issue**: `Load balancer health check failing`
```bash
# Solution: Verify application is running
ssh root@$(terraform output -raw app_server_ips | jq -r '.[0]')
curl http://localhost:8000/health
```

### Access Logs

**Application Logs**:
```bash
ssh root@SERVER_IP
cd /opt/areamedica-api
docker-compose logs -f api
```

**Database Logs**: Available in DigitalOcean Control Panel

**Load Balancer Logs**: Contact DigitalOcean support

### State Management

**Remote State** (recommended for teams):
```hcl
# backend.tf
terraform {
  backend "s3" {
    bucket                      = "areamedica-terraform-state"
    key                         = "production/terraform.tfstate"
    region                      = "us-east-1"
    endpoint                    = "nyc3.digitaloceanspaces.com"
    skip_credentials_validation = true
    skip_metadata_api_check     = true
  }
}
```

**State Backup**:
```bash
# Backup state file
cp terraform.tfstate terraform.tfstate.backup

# Or use Terraform Cloud
terraform login
```

## 📚 Additional Resources

- [DigitalOcean Documentation](https://docs.digitalocean.com/)
- [Terraform DigitalOcean Provider](https://registry.terraform.io/providers/digitalocean/digitalocean/latest/docs)
- [AreaMédica API Documentation](../README.md)

## 🤝 Support

For infrastructure issues:
1. Check troubleshooting section
2. Review DigitalOcean status page
3. Open GitHub issue with `infrastructure` label

---

**Version**: 1.0.0
**Last Updated**: 2024-01-XX
**Maintained by**: AreaMédica DevOps Team
