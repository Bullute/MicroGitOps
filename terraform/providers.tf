terraform {
  required_version = ">= 1.5.0"
  required_providers {
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "~> 2.27.0"
    }
  }
}

# Configures access using local Kubeconfig file
provider "kubernetes" {
  config_path = "/home/staj/.kube/config"
}
