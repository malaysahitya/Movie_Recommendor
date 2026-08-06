variable "gcp_project_id" {
  description = "Google Cloud Project ID"
  type        = string
  default     = "movie-recommender-agent-prod"
}

variable "gcp_region" {
  description = "GCP deployment region"
  type        = string
  default     = "us-central1"
}
