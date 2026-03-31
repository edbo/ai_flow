terraform {
  required_version = "~> 1.11.4"
  required_providers {
    spacelift = {
      source  = "spacelift-io/spacelift"
      version = "1.44.0"
    }
  }
}

provider "spacelift" {
  api_key_endpoint = "https://nova-install.app.spacelift.io"
}
