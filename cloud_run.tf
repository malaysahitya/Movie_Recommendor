# Terraform Infrastructure as Code — Cloud Run v2 Service Provisioning

resource "google_cloud_run_v2_service" "movie_recommender_agent" {
  name     = "movie-recommender-agent"
  location = var.gcp_region
  ingress  = "INGRESS_TRAFFIC_ALL"

  template {
    containers {
      image = "gcr.io/${var.gcp_project_id}/movie-recommender-agent:latest"
      
      resources {
        limits = {
          cpu    = "1000m"
          memory = "512Mi"
        }
      }

      # Inject Secret Manager API Keys as Environment Variables
      env {
        name = "TMDB_API_KEY"
        value_source {
          secret_key_ref {
            secret  = google_secret_manager_secret.tmdb_api_key.secret_id
            version = "latest"
          }
        }
      }

      env {
        name = "GEMINI_API_KEY"
        value_source {
          secret_key_ref {
            secret  = google_secret_manager_secret.gemini_api_key.secret_id
            version = "latest"
          }
        }
      }

      env {
        name  = "DEFAULT_RESULT_LIMIT"
        value = "10"
      }
    }
  }
}
