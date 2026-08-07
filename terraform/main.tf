# 1. Namespace Creation
# Isolates our microservices from other cluster apps
resource "kubernetes_namespace" "app_namespace" {
  metadata {
    name = var.namespace_name
    labels = {
      environment = var.environment
      managed_by  = "terraform"
    }
  }
}

# 2. ConfigMap Creation (Non-sensitive variables)
# Inject APP_ENV and APP_PORT into our application pods
resource "kubernetes_config_map" "app_config" {
  metadata {
    name      = "microgitops-config"
    namespace = kubernetes_namespace.app_namespace.metadata[0].name
  }

  data = {
    APP_ENV  = var.environment
    APP_PORT = "8000"
  }
}

# 3. Secret Creation (Sensitive variables)
# Secure database credentials. K8s stores values base64-encoded.
resource "kubernetes_secret" "app_secret" {
  metadata {
    name      = "microgitops-secret"
    namespace = kubernetes_namespace.app_namespace.metadata[0].name
  }

  data = {
    DATABASE_URL = "postgresql://db_user:${var.db_password}@postgres-service:5432/microgitops"
  }

  type = "Opaque"
}
