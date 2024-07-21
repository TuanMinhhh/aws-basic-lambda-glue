
variable "cluster_name" {
  description = "Name of the EMR cluster"
}

variable "emr_release_label" {
  description = "EMR release label"
}

variable "emr_applications" {
  description = "List of applications to install on the cluster"
  type        = list(string)
}

variable "emr_configurations" {
  description = "EMR cluster configurations"
  type        = string
  default     = <<EOF
  [
    {
      "Classification": "hadoop-env",
      "Configurations": [
        {
          "Classification": "export",
          "Properties": {
            "JAVA_HOME": "/usr/lib/jvm/java-1.8.0"
          }
        }
      ]
    }
  ]
  EOF
}

variable "termination_protection" {
  description = "Enable termination protection for the EMR cluster"
  type        = bool
}

variable "keep_alive_when_no_step" {
  description = "Keep the EMR cluster alive when no step is running"
  type        = bool
}

variable "scale_down_behavior" {
  description = "Scale down behavior for the EMR cluster"
  type        = string
}

variable "scale_down_min_count" {
  description = "Minimum number of instances to scale down to"
  type        = number
}

variable "scale_down_max_count" {
  description = "Maximum number of instances to scale down to"
  type        = number
}

variable "scale_down_period_minutes" {
  description = "Period in minutes to wait before scaling down the cluster"
  type        = number
}

variable "master_instance_type" {
  description = "Instance type for the master node"
  type        = string
}

variable "core_instance_type" {
  description = "Instance type for the core nodes"
  type        = string
}

variable "core_instance_count" {
  description = "Number of core nodes in the cluster"
  type        = number
}

variable "use_spot_instances" {
  description = "Use Spot Instances for the core nodes"
  type        = bool
  default     = true
}

variable "ebs_root_volume_size" {
  description = "Size of the EBS root volume in GB"
  type        = number
}

variable "vpc_id" {
  description = "vpc id the VPC"
  type        = string
}

variable "private_subnets" {
  description = "private_subnets for the VPC"
  type        = list(string)
}

variable "vpc_cidr_block" {
  description = "CIDR block for the VPC"
  type        = string
}

variable "subnet_cidrs" {
  description = "CIDR blocks for the subnets"
  type        = list(string)
}

variable "emr_service_role" {
  description = "IAM role for the EMR service"
  type        = string
}

variable "emr_instance_profile" {
  description = "IAM instance profile for the EMR instances"
  type        = string
}

variable "log_uri" {
  description = "S3 bucket URI for EMR logs"
  type        = string
}

variable "tags" {
  description = "Common tags to apply to all resources"
  type        = map(string)
}

variable "core_instance_bid_price" {
  description = "Bid price for Spot Instances in the core instance group"
  type        = string
  default     = "0.07"  # Adjust the bid price based on your requirements
}

variable "auto_terminate" {
  description = "Whether to automatically terminate the cluster when no steps are running"
  type        = bool
  default     = false
}

variable "auto_termination_idle_timeout" {
  description = "The idle timeout in seconds after which the cluster automatically terminates"
  type        = number
  default     = 3600
}