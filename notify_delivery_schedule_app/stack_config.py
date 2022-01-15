from pathlib import Path

import yaml


# tag paramater
PROJECT_NAME = "NotifyDeliveryScheduleApp"
CREATER = "cdk"

# resource_name
LAMBDA_PREFIX = "lmd"
IAM_PREFIX = "iam"
SQS_PREFIX = "sqs"
RULE_PREFIX = "rul"
DYNAMODB_PREFIX = "dyn"
SNS_PREFIX = "sns"
SNS_SUBSCRIPTION_PREFIX = "sub"

# Lambda paramater
LAMBDA_DEPLOY_DIR = "deploy"
LAMBDA_HANDLER_PATH = "lambda_function.handler"
LAMBDA_TIMEOUT = 300
LAMBDA_MEMORY_SIZE = 256

# SQS paramater
SQS_VISIBILITY_TIMEOUT = 500

# Rule paramater
RULE_ENABLED = True
CREATE_RULE_NAME = "*"

# DynamoDB paramater
SCHEDULE_MASTER_TABLE_PARTITION_KEY = "pkey"
SCHEDULE_MASTER_TABLE_SORT_KEY = "channel_id"
SCHEDULE_MASTER_TABLE_READ_CAPACITY = 1
SCHEDULE_MASTER_TABLE_WRITE_CAPACITY = 1
NOTIFY_CONTROLLER_TABLE_PARTITION_KEY = "video_id"
NOTIFY_CONTROLLER_TABLE_SORT_KEY = "version"
NOTIFY_CONTROLLER_TABLE_READ_CAPACITY = 1
NOTIFY_CONTROLLER_TABLE_WRITE_CAPACITY = 1

# service_name
YOUTUBE_SCHEDULE_SERVICE_NAME = "youtube_schedule_service"
CREATE_RULE_SERVICE_NAME = "create_rule_service"
NOTIFY_SCHEDULE_SERVICE_NAME = "notify_schedule_service"
POST_TWITTER_SERVICE_NAME = "post_twitter_service"
REGISTER_SCHEDULE_MASTER_SERVICE_NAME = "register_schedule_master_service"
SCHEDULE_MASTER_TABLE_NAME = "schedule_master_table"
MANUAL_SCHEDULE_SERVICE_NAME = "manual_schedule_service"
NOTIFY_CONTROLLER_TABLE_NAME = "notify_controller_table"

# service_description
YOUTUBE_SCHEDULE_SERVICE_DESCRIPTION = "Get the delivery schedule."
CREATE_RULE_SERVICE_DESCRIPTION = "Create an event rule."
NOTIFY_SCHEDULE_SERVICE_DESCRIPTION = "Notify the delivery schedule."
POST_TWITTER_SERVICE_DESCRIPTION = "Post to Twitter."
REGISTER_SCHEDULE_MASTER_SERVICE_DESCRIPTION = "Register a master in schedule_master_table."
MANUAL_SCHEDULE_SERVICE_DESCRIPTION = "Register a delivery schedule manually."

# paramater store
SSM_YOUTUBE_API_KEY = "youtube_api_key"
SSM_TWITTER_API_KEY = "twitter_api_key"
SSM_TWITTER_API_SECRET_KEY = "twitter_api_secret_key"
SSM_TWITTER_ACCESS_TOKEN = "twitter_access_token"
SSM_TWITTER_ACCESS_TOKEN_SECRET = "twitter_access_token_secret"

# Lambda env param
lambda_param_file_path = Path.cwd() / "env_param" / "lambda_param.yaml"
with open(str(lambda_param_file_path), "r", encoding="utf-8") as f:
    lambda_param = yaml.safe_load(f)
YOUTUBE_SCHEDULE_SERVICE_PARAMATER = lambda_param[YOUTUBE_SCHEDULE_SERVICE_NAME]
CREATE_RULE_SERVICE_PARAMATER = lambda_param[CREATE_RULE_SERVICE_NAME]
NOTIFY_SCHEDULE_SERVICE_PARAMATER = lambda_param[NOTIFY_SCHEDULE_SERVICE_NAME]
POST_TWITTER_SERVICE_PARAMATER = lambda_param[POST_TWITTER_SERVICE_NAME]
REGISTER_SCHEDULE_MASTER_SERVICE_PARAMATER = lambda_param[REGISTER_SCHEDULE_MASTER_SERVICE_NAME]
MANUAL_SCHEDULE_SERVICE_PARAMATER = lambda_param[MANUAL_SCHEDULE_SERVICE_NAME]

# Lambda env key
SNS_TOPICK_NAME_KEY = "SNS_TOPICK_ARN"
