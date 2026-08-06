output "cloud_run_service_url" {
  description = "The public URL endpoint of the deployed Movie Recommender Agent"
  value       = google_cloud_run_v2_service.movie_recommender_agent.uri
}

output "tmdb_secret_name" {
  description = "Google Secret Manager secret ID for TMDB API key"
  value       = google_secret_manager_secret.tmdb_api_key.secret_id
}

output "gemini_secret_name" {
  description = "Google Secret Manager secret ID for Gemini API key"
  value       = google_secret_manager_secret.gemini_api_key.secret_id
}
