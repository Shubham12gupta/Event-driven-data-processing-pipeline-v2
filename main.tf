resource "linode_instance" "pipeline_vm" {
    label  = "event-pipeline-vm"
    region = "ap-south"
    type   = "g6-standard-2"
    image  = "linode/ubuntu24.04"

    root_pass = var.root_password
  }

