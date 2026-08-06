# Terraform Infrastructure as Code — Secret Manager Provisioning

resource "google_secret_manager_secret" "tmdb_api_key" {
  secret_id = "TMDB_API_KEY"
  replication {
    auto {}
  }
}

resource "google_secret_manager_secret" "gemini_api_key" {
  secret_id = "GEMINI_API_KEY"
  replication {
    auto {}
  }
}

resource "google_secret_manager_secret" "omdb_api_key" {
  secret_id = "OMDB_API_KEY"
  replication {
    auto {}
  }
}
