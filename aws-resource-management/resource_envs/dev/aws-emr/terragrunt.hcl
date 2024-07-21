locals {
    local_env = read_terragrunt_config(find_in_parent_folders("env.hcl"))

    # extract local_env variables
    environment           = local.local_env.locals.environment
    environment_code      = local.local_env.locals.environment_code
    aws_account_id        = local.local_env.locals.aws_account_id
    aws_profile           = local.local_env.locals.aws_profile
    aws_region_code       = local.local_env.locals.aws_region_code
    environment_branch    = local.local_env.locals.environment_branch

}

include {
  path = find_in_parent_folders()
}

terraform {
    source = "../../../modules//aws-emr"
}

dependency "s3" {
    config_path = "../aws-s3"
}

dependency "share_vpc" {
    config_path = "../aws-vpc"
}

inputs = {
    cluster_name        = "${local.aws_profile}-${local.aws_region_code}-${local.environment_code}-emr-cluster"
    emr_release_label   = "emr-6.8.0"
    emr_applications    = ["Spark", "Hive"]
    emr_configurations  = []

    termination_protection = false
    keep_alive_when_no_step = true
    scale_down_behavior     = "TERMINATE_AT_INSTANCE_HOUR"
    scale_down_min_count    = 0
    scale_down_max_count    = 1
    scale_down_period_minutes = 60

    master_instance_type = "m5.large"
    core_instance_type   = "m5.small" # Sử dụng instance nhỏ hơn
    core_instance_count  = 1
    ebs_root_volume_size = 20

    use_spot_instances = true

    vpc_id = dependency.share_vpc.outputs.vpc_id
    private_subnets = dependency.share_vpc.outputs.private_subnets
    vpc_cidr_block = dependency.share_vpc.outputs.vpc_cidr_block
    subnet_cidrs   = dependency.share_vpc.outputs.public_subnets

    emr_service_role   = "EMR_DefaultRole"
    emr_instance_profile = "EMR_EC2_DefaultRole"

    log_uri = "s3://${dependency.s3.outputs.temporary_bucket}/emr_logs"

    tags = {
        "environment_code" : local.local_env.locals.environment_code
        "stage_name": "share-service"
        "function_code": "share-service"
    }
}