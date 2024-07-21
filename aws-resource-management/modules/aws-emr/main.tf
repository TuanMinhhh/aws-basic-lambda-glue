
resource "aws_emr_cluster" "emr_cluster" {
  name           = var.cluster_name
  release_label  = var.emr_release_label
  applications   = var.emr_applications
  configurations = var.emr_configurations

  termination_protection            = var.termination_protection
  step_concurrency_level            = 1
  scale_down_behavior               = var.scale_down_behavior

  master_instance_group {
    instance_type = var.master_instance_type
    instance_count = 1

    ebs_config {
      size = var.ebs_root_volume_size
      type = "gp2"
    }
  }

  core_instance_group {
    instance_type = var.core_instance_type
    instance_count = var.core_instance_count

    ebs_config {
      size = var.ebs_root_volume_size
      type = "gp2"
    }

    bid_price = var.use_spot_instances ? var.core_instance_bid_price : null
  }

  ec2_attributes {
    instance_profile = var.emr_instance_profile
    subnet_ids = var.private_subnets
  }

  auto_termination_policy {
    idle_timeout = var.auto_termination_idle_timeout
  }

  service_role = var.emr_service_role
  

  log_uri = var.log_uri

  tags = var.tags
}