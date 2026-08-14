variable "namespace_name" {
  description = "The target Kubernetes namespace"
  type        = string
  default     = "microgitops"
}

variable "environment" {
  description = "Execution environment"
  type        = string
  default     = "production"
}

variable "db_password" {
  description = "Database password (sensitive)"
  type        = string
  default     = "SuperSecretPassword123"
  sensitive   = true
}

