variable "gcp_project_id" {
  description = "Google Cloud Project ID for deployment"
  type        = string
  default     = "striking-retina-503305-j2"
}

variable "gcp_region" {
  description = "Google Cloud Region for service deployment"
  type        = string
  default     = "us-central1"
}
