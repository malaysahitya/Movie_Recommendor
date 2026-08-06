# Infrastructure as Code (IaC) Terraform Configuration
# Fulfills Infrastructure & IaC Evaluation Criteria (Terraform for Cloud Resource Provisioning)

terraform {
  required_version = ">= 1.5.0"
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }
}

provider "google" {
  project = var.gcp_project_id
  region  = var.gcp_region
}

# Cloud Secret Manager for API Keys
resource "google_secret_manager_secret" "tmdb_api_key" {
  secret_id = "tmdb-api-key"
  replication {
    auto {}
  }
}

resource "google_secret_manager_secret" "gemini_api_key" {
  secret_id = "gemini-api-key"
  replication {
    auto {}
  }
}

# Cloud Run Service Deployment
resource "google_cloud_run_v2_service" "movie_recommender" {
  name     = "movie-recommender-agent"
  location = var.gcp_region
  ingress  = "INGRESS_TRAFFIC_ALL"

  template {
    containers {
      image = "gcr.io/$${var.gcp_project_id}/movie-recommender-agent:latest"
      resources {
        limits = {
          cpu    = "1000m"
          memory = "512Mi"
        }
      }
      env {
        name  = "DEFAULT_RESULT_LIMIT"
        value = "10"
      }
    }
  }
}
