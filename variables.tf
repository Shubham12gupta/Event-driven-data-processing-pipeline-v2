variable "linode_token" {
    description = "Linode API token"
    type = string
    sensitive = true
}

variable "root_password" {
description = "Temporary root password"
type = string
sensitive  = true
}