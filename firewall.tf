resource "linode_firewall" "pipeline_fw" {
    label           = "pipeline_firewall"
    inbound_policy  = "DROP"
    outbound_policy = "ACCEPT"

    inbound {
      label    = "ssh"
      action   = "ACCEPT"
      protocol = "TCP"
      ports    = "22"
      ipv4     = ["0.0.0.0/0"]
    }

    inbound {
      label    = "http"
      action   = "ACCEPT"
      protocol = "TCP"
      ports    = "80"
      ipv4     = ["0.0.0.0/0"]
    }

    inbound {
      label    = "https"
      action   = "ACCEPT"
      protocol = "TCP"
      ports    = "443"
      ipv4     = ["0.0.0.0/0"]
    }
    inbound {
      label    = "fastapi"
      action   = "ACCEPT"
      protocol = "TCP"
      ports    = "8000"
      ipv4     = ["0.0.0.0/0"]
    }


    linodes = [linode_instance.pipeline_vm.id]
  }
  