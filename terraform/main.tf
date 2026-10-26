terraform {
  required_providers {
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "~> 2.30"
    }
    kubectl = {
      source  = "gavinbunney/kubectl"
      version = "~> 1.14"
    }
  }
}

provider "kubernetes" {
  config_context = "docker-desktop"
}

provider "kubectl" {
  config_context = "docker-desktop"
}

resource "kubernetes_namespace" "cna" {
  metadata {
    name = "cna"
  }
}

data "kubectl_path_documents" "manifests" {
  pattern = "${path.module}/../k8s/*.yaml"
}

resource "kubectl_manifest" "app" {
  for_each           = data.kubectl_path_documents.manifests.manifests
  yaml_body          = each.value
  override_namespace = kubernetes_namespace.cna.metadata[0].name
}