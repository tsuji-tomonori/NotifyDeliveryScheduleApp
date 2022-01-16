from aws_cdk import (
    Stack,
    aws_ssm as ssm,
    aws_events_targets as target,
    aws_iam as iam,
    aws_lambda_event_sources as event_source,
)
from constructs import Construct

from notify_delivery_schedule_app.stack_base import (
    create_lambda,
    create_iam_role_for_lambda,
    create_sns,
    create_dynamodb_exist_sort_key,
    create_schdule_rule_every_hour,
    subscribe_sns_to_lambda,
)
import notify_delivery_schedule_app.stack_config as config

class NotifyDeliveryScheduleAppStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Declaring a resource

        rul_youtube_schedule_service_cdk = create_schdule_rule_every_hour(
            self,
            service_name=config.YOUTUBE_SCHEDULE_SERVICE_NAME,
            service_description=config.YOUTUBE_SCHEDULE_SERVICE_DESCRIPTION,
        )
        iam_youtube_schedule_service = create_iam_role_for_lambda(
            self,
            service_name=config.YOUTUBE_SCHEDULE_SERVICE_NAME,
            service_description=config.YOUTUBE_SCHEDULE_SERVICE_DESCRIPTION,
        )
        lmd_youtube_schedule_service = create_lambda(
            self,
            service_name=config.YOUTUBE_SCHEDULE_SERVICE_NAME,
            service_description=config.YOUTUBE_SCHEDULE_SERVICE_DESCRIPTION,
            environment=config.YOUTUBE_SCHEDULE_SERVICE_PARAMATER,
            lambda_role=iam_youtube_schedule_service,
        )
        rul_youtube_schedule_service_cdk.add_target(target.LambdaFunction(lmd_youtube_schedule_service))
        ssm_youtube_api_key = ssm.StringParameter.from_secure_string_parameter_attributes(
            self, config.SSM_YOUTUBE_API_KEY,
            version=1,
            parameter_name=config.SSM_YOUTUBE_API_KEY
        )
        dyn_youtube_schedule_service = create_dynamodb_exist_sort_key(
            self,
            service_name=config.SCHEDULE_MASTER_TABLE_NAME,
            partition_key=config.SCHEDULE_MASTER_TABLE_PARTITION_KEY,
            sort_key=config.SCHEDULE_MASTER_TABLE_SORT_KEY,
            read_capacity=config.SCHEDULE_MASTER_TABLE_READ_CAPACITY,
            write_capacity=config.SCHEDULE_MASTER_TABLE_WRITE_CAPACITY,
        )
        dyn_notify_controller_table = create_dynamodb_exist_sort_key(
            self,
            service_name=config.NOTIFY_CONTROLLER_TABLE_NAME,
            partition_key=config.NOTIFY_CONTROLLER_TABLE_PARTITION_KEY,
            sort_key=config.NOTIFY_CONTROLLER_TABLE_SORT_KEY,
            read_capacity=config.NOTIFY_CONTROLLER_TABLE_READ_CAPACITY,
            write_capacity=config.NOTIFY_CONTROLLER_TABLE_WRITE_CAPACITY,
        )
        sns_youtube_schedule_service = create_sns(
            self,
            service_name=config.YOUTUBE_SCHEDULE_SERVICE_NAME
        )
        subscribe_sns_to_lambda(
            self,
            service_name=config.YOUTUBE_SCHEDULE_SERVICE_NAME,
            topic=sns_youtube_schedule_service,
            target_lambda=lmd_youtube_schedule_service,
        )


        iam_register_schedule_master_service_cdk = create_iam_role_for_lambda(
            self,
            service_name=config.REGISTER_SCHEDULE_MASTER_SERVICE_NAME,
            service_description=config.CREATE_RULE_SERVICE_DESCRIPTION,
        )
        lmd_register_schedule_master_service_cdk = create_lambda(
            self,
            service_name=config.REGISTER_SCHEDULE_MASTER_SERVICE_NAME,
            environment=config.REGISTER_SCHEDULE_MASTER_SERVICE_PARAMATER,
            service_description=config.REGISTER_SCHEDULE_MASTER_SERVICE_DESCRIPTION,
            lambda_role=iam_register_schedule_master_service_cdk,
        )


        iam_manual_schedule_service = create_iam_role_for_lambda(
            self,
            service_name=config.MANUAL_SCHEDULE_SERVICE_NAME,
            service_description=config.MANUAL_SCHEDULE_SERVICE_DESCRIPTION,
        )
        lmd_manual_schedule_service = create_lambda(
            self,
            service_name=config.MANUAL_SCHEDULE_SERVICE_NAME,
            environment=config.MANUAL_SCHEDULE_SERVICE_PARAMATER,
            service_description=config.CREATE_RULE_SERVICE_DESCRIPTION,
            lambda_role=iam_manual_schedule_service,
        )


        iam_create_rule_service = create_iam_role_for_lambda(
            self,
            service_name=config.CREATE_RULE_SERVICE_NAME,
            service_description=config.CREATE_RULE_SERVICE_DESCRIPTION,
        )
        lmd_create_rule_service = create_lambda(
            self,
            service_name=config.CREATE_RULE_SERVICE_NAME,
            environment=config.CREATE_RULE_SERVICE_PARAMATER,
            service_description=config.CREATE_RULE_SERVICE_DESCRIPTION,
            lambda_role=iam_create_rule_service,
        )
        lmd_create_rule_service.add_event_source(event_source.SnsEventSource(sns_youtube_schedule_service))


        iam_notify_schedule_service = create_iam_role_for_lambda(
            self,
            service_name=config.NOTIFY_SCHEDULE_SERVICE_NAME,
            service_description=config.NOTIFY_SCHEDULE_SERVICE_DESCRIPTION,
        )
        lmd_notify_schedule_service = create_lambda(
            self,
            service_name=config.NOTIFY_SCHEDULE_SERVICE_NAME,
            environment=config.NOTIFY_SCHEDULE_SERVICE_PARAMATER,
            service_description=config.NOTIFY_SCHEDULE_SERVICE_DESCRIPTION,
            lambda_role=iam_notify_schedule_service,
        )
        lmd_notify_schedule_service.add_permission(
            "permission_lmd_notify_schedule_service",
            action="lambda:InvokeFunction",
            principal=iam.ServicePrincipal("events.amazonaws.com"),
        )


        sns_post_twitter_service = create_sns(
            self,
            service_name=config.POST_TWITTER_SERVICE_NAME,
        )
        iam_post_twitter_service = create_iam_role_for_lambda(
            self,
            service_name=config.POST_TWITTER_SERVICE_NAME,
            service_description=config.POST_TWITTER_SERVICE_DESCRIPTION,
        )
        lmd_post_twitter_service = create_lambda(
            self,
            service_name=config.POST_TWITTER_SERVICE_NAME,
            environment=config.POST_TWITTER_SERVICE_PARAMATER,
            service_description=config.POST_TWITTER_SERVICE_DESCRIPTION,
            lambda_role=iam_post_twitter_service,
        )
        subscribe_sns_to_lambda(
            self,
            service_name=config.POST_TWITTER_SERVICE_NAME,
            topic=sns_post_twitter_service,
            target_lambda=lmd_post_twitter_service,
        )
        lmd_post_twitter_service.add_event_source(event_source.SnsEventSource(sns_post_twitter_service))
        ssm_twitter_api_key = ssm.StringParameter.from_secure_string_parameter_attributes(
            self, config.SSM_TWITTER_API_KEY,
            version=1,
            parameter_name=config.SSM_TWITTER_API_KEY,
        )
        ssm_twitter_api_secret_key = ssm.StringParameter.from_secure_string_parameter_attributes(
            self, config.SSM_TWITTER_API_SECRET_KEY,
            version=1,
            parameter_name=config.SSM_TWITTER_API_SECRET_KEY,
        )
        ssm_twitter_access_token = ssm.StringParameter.from_secure_string_parameter_attributes(
            self, config.SSM_TWITTER_ACCESS_TOKEN,
            version=1,
            parameter_name=config.SSM_TWITTER_ACCESS_TOKEN,
        )
        ssm_twitter_access_token_secret = ssm.StringParameter.from_secure_string_parameter_attributes(
            self, config.SSM_TWITTER_ACCESS_TOKEN_SECRET,
            version=1,
            parameter_name=config.SSM_TWITTER_ACCESS_TOKEN_SECRET,
        )


        # Create the IAM role

        ssm_youtube_api_key.grant_read(iam_youtube_schedule_service)
        sns_youtube_schedule_service.grant_publish(iam_youtube_schedule_service)
        dyn_youtube_schedule_service.grant_read_data(iam_youtube_schedule_service)
        dyn_notify_controller_table.grant_read_write_data(iam_youtube_schedule_service)

        dyn_youtube_schedule_service.grant_write_data(iam_register_schedule_master_service_cdk)
        
        sns_youtube_schedule_service.grant_publish(iam_manual_schedule_service)

        iam_create_rule_service.add_to_policy(
            iam.PolicyStatement(
                actions=["events:PutRule", "events:PutTargets", "events:TagResource"],
                effect=iam.Effect.ALLOW,
                resources=[config.CREATE_RULE_NAME],
            )
        )

        sns_post_twitter_service.grant_publish(iam_notify_schedule_service)

        sns_post_twitter_service.grant_publish(iam_post_twitter_service)
        ssm_twitter_api_key.grant_read(iam_post_twitter_service)
        ssm_twitter_api_secret_key.grant_read(iam_post_twitter_service)
        ssm_twitter_access_token.grant_read(iam_post_twitter_service)
        ssm_twitter_access_token_secret.grant_read(iam_post_twitter_service)
        iam_post_twitter_service.add_to_policy(
            iam.PolicyStatement(
                actions=["events:*"],
                effect=iam.Effect.ALLOW,
                resources=[config.CREATE_RULE_NAME],
            )
        )
        dyn_notify_controller_table.grant_read_data(iam_post_twitter_service)


        # Name resolution of environment variables
        lmd_youtube_schedule_service.add_environment(
            key=config.SCHEDULE_MASTER_TABLE_NAME.upper(),
            value=dyn_youtube_schedule_service.table_name,
        )
        lmd_youtube_schedule_service.add_environment(
            key=config.NOTIFY_CONTROLLER_TABLE_NAME.upper(),
            value=dyn_notify_controller_table.table_name,
        )
        lmd_youtube_schedule_service.add_environment(
            key=config.SNS_TOPICK_NAME_KEY.upper(),
            value=sns_youtube_schedule_service.topic_arn,
        )
        lmd_youtube_schedule_service.add_environment(
            key=config.SSM_YOUTUBE_API_KEY.upper(),
            value=ssm_youtube_api_key.parameter_name,
        )

        lmd_register_schedule_master_service_cdk.add_environment(
            key=config.SCHEDULE_MASTER_TABLE_NAME.upper(),
            value=dyn_youtube_schedule_service.table_name
        )

        lmd_manual_schedule_service.add_environment(
            key=config.SNS_TOPICK_NAME_KEY.upper(),
            value=sns_youtube_schedule_service.topic_name,
        )
        lmd_manual_schedule_service.add_environment(
            key=config.NOTIFY_CONTROLLER_TABLE_NAME.upper(),
            value=dyn_notify_controller_table.table_name,
        )

        lmd_create_rule_service.add_environment(
            key=config.NOTIFY_SCHEDULE_SERVICE_NAME.upper(),
            value=lmd_notify_schedule_service.function_arn,
        )

        lmd_notify_schedule_service.add_environment(
            key=config.POST_TWITTER_SERVICE_NAME.upper(),
            value=sns_post_twitter_service.topic_arn,
        )

        lmd_post_twitter_service.add_environment(
            key=config.NOTIFY_CONTROLLER_TABLE_NAME.upper(),
            value=dyn_notify_controller_table.table_name,
        )
        lmd_post_twitter_service.add_environment(
            key=config.SSM_TWITTER_API_KEY.upper(),
            value=ssm_twitter_api_key.parameter_name,
        )
        lmd_post_twitter_service.add_environment(
            key=config.SSM_TWITTER_API_SECRET_KEY.upper(),
            value=ssm_twitter_api_secret_key.parameter_name,
        )
        lmd_post_twitter_service.add_environment(
            key=config.SSM_TWITTER_ACCESS_TOKEN.upper(),
            value=ssm_twitter_access_token.parameter_name,
        )
        lmd_post_twitter_service.add_environment(
            key=config.SSM_TWITTER_ACCESS_TOKEN_SECRET.upper(),
            value=ssm_twitter_access_token_secret.parameter_name,
        )
