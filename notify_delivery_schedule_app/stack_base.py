import os

import aws_cdk as cdk
from aws_cdk import (
    aws_lambda as lambda_,
    aws_logs as logs,
    aws_iam as iam, 
    aws_sqs as sqs,
    aws_events as event,
    aws_events_targets as target,
    aws_dynamodb as dynamodb,
    aws_sns as sns
)

import notify_delivery_schedule_app.stack_config as config


def build_resource_name(resource_name: str, service_name: str) -> str:
    """リソース名を組み立てる関数.

    Args:
        resource_name (str): AWSリソース名(例: lmd)
        service_name (str): サービス固有名(例: xxx_service)

    Returns:
        str: 組み立てたリソース名 (例: lmd_xxx_service_cdk)
    """
    return f"{resource_name}_{service_name}_{config.CREATER}"


def set_tags(func):
    """タグ付けを行う関数. \n

    この関数はアノテーションとして利用する想定. \n
    設定するタグは以下. \n
    ・projectタグ: プロジェクト全体で統一して使用する\n
    ・service_nameタグ: 各サービス名\n
    ・createrタグ: 何を使用して作成したか cdk固定\n
    ※ 使用する際は作成するリソース(関数)のキーワード引数に[service_name]を入れること

    Args:
        func (function): 作成するリソース(関数)

    Returns:
        function: タグ付けを実施したリソースを作成する関数
    """
    def wrapper(*args, **kwargs) -> None:
        result = func(*args, **kwargs)
        cdk.Tags.of(result).add("project", config.PROJECT_NAME)
        cdk.Tags.of(result).add("service_name", kwargs["service_name"])
        cdk.Tags.of(result).add("creater", config.CREATER)
        return result
    return wrapper


@set_tags
def create_lambda(
    self, 
    service_name: str, 
    environment: dict,
    service_description: str,
    lambda_role: iam.Role,
) -> lambda_.Function:
    """Lambdaを作成する関数.

    Args:
        service_name (str): サービス名
        environment (dict): 環境変数
        service_description (str): 詳細
        lambda_role (iam.Role): Lambda実行ロール

    Returns:
        lambda_.Function: Lambda
    """
    return lambda_.Function(
        self, build_resource_name(config.LAMBDA_PREFIX, service_name),
        code=lambda_.Code.from_asset(os.path.join(config.LAMBDA_DEPLOY_DIR, service_name)),
        handler=config.LAMBDA_HANDLER_PATH,
        runtime=lambda_.Runtime.PYTHON_3_9,
        function_name=build_resource_name(config.LAMBDA_PREFIX, service_name),
        environment=environment,
        description=service_description,
        timeout=cdk.Duration.seconds(config.LAMBDA_TIMEOUT),
        memory_size=config.LAMBDA_MEMORY_SIZE,
        log_retention=logs.RetentionDays.THREE_MONTHS,
        role=lambda_role,
    )


@set_tags
def create_iam_role_for_lambda(
    self,
    service_name: str,
    service_description: str
) -> iam.Role:
    """Lambda用のIAMロールを作成する関数.

    Args:
        service_name (str): サービス名
        service_description (str): 詳細

    Returns:
        iam.Role: IAM Role
    """
    return iam.Role(
        self, build_resource_name(config.IAM_PREFIX, service_name),
        assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
        managed_policies=[
            iam.ManagedPolicy.from_aws_managed_policy_name(
                "service-role/AWSLambdaBasicExecutionRole")
        ],
        role_name=build_resource_name(config.IAM_PREFIX, service_name),
        description=service_description
    )


@set_tags
def create_sqs(
    self,
    service_name: str
) -> sqs.Queue:
    """SQSを作成する関数.

    Args:
        service_name (str): サービス名

    Returns:
        sqs.Queue: SQS
    """
    return sqs.Queue(
        self, build_resource_name(config.SQS_PREFIX, service_name),
        queue_name=build_resource_name(config.SQS_PREFIX, service_name),
        visibility_timeout=cdk.Duration.seconds(config.SQS_VISIBILITY_TIMEOUT)
    )


@set_tags
def create_schdule_rule_every_15_minutes(
    self,
    service_name: str,
    service_description: str,
) -> event.Rule:
    """15分毎のイベントを作成する関数.

    Args:
        service_name (str): サービス名
        service_description (str): 詳細

    Returns:
        event.Rule: [description]
    """
    return event.Rule(
        self, build_resource_name(config.RULE_PREFIX, service_name),
        schedule=event.Schedule.cron(
            minute="0/15",
            hour="*",
            day="*",
            month="*",
            year="*"
        ),
        rule_name=build_resource_name(config.RULE_PREFIX, service_name),
        description=service_description,
        enabled=config.RULE_ENABLED
    )


@set_tags
def create_dynamodb_exist_sort_key(
    self,
    service_name: str,
    partition_key: str,
    sort_key: str,
    read_capacity: int,
    write_capacity: int,
) -> dynamodb.Table:
    """dynamodbを作成する関数.\n

    ソートキーがあるバージョン. \n
    ※ スタック削除時一緒に削除するように設定

    Args:
        service_name (str): サービス名
        partition_key (str): パーティションキー名
        sort_key (str): ソートキー名
        read_capacity (int): 読込キャパシティユニット
        write_capacity (int): 書込キャパシティユニット

    Returns:
        dynamodb.Table: dynamodb
    """
    return dynamodb.Table(
        self,
        build_resource_name(config.DYNAMODB_PREFIX, service_name),
        table_name=build_resource_name(config.DYNAMODB_PREFIX, service_name),
        billing_mode=dynamodb.BillingMode.PROVISIONED,
        read_capacity=read_capacity,
        write_capacity=write_capacity,
        removal_policy=cdk.RemovalPolicy.DESTROY,
        partition_key=dynamodb.Attribute(
            name=partition_key,
            type=dynamodb.AttributeType.STRING,
        ),
        sort_key=dynamodb.Attribute(
            name=sort_key,
            type=dynamodb.AttributeType.STRING,
        ),
    )


@set_tags
def create_dynamodb_not_sort_key(
    self,
    service_name: str,
    partition_key: str,
    read_capacity: int,
    write_capacity: int,
) -> dynamodb.Table:
    """dynamodbを作成する関数.\n

    ソートキーがないバージョン. \n
    ※ スタック削除時一緒に削除するように設定

    Args:
        service_name (str): サービス名
        partition_key (str): パーティションキー名
        read_capacity (int): 読込キャパシティユニット
        write_capacity (int): 書込キャパシティユニット

    Returns:
        dynamodb.Table: dynamodb
    """
    return dynamodb.Table(
        self,
        build_resource_name(config.DYNAMODB_PREFIX, service_name),
        table_name=build_resource_name(config.DYNAMODB_PREFIX, service_name),
        billing_mode=dynamodb.BillingMode.PROVISIONED,
        read_capacity=read_capacity,
        write_capacity=write_capacity,
        removal_policy=cdk.RemovalPolicy.DESTROY,
        partition_key=dynamodb.Attribute(
            name=partition_key,
            type=dynamodb.AttributeType.STRING,
        ),
    )


@set_tags
def create_sns(
    self,
    service_name: str,
) -> sns.Topic:
    """snsトピックを作成する関数.

    Args:
        service_name (str): サービス名

    Returns:
        sns.Topic: SNS Topic
    """
    return sns.Topic(
        self, build_resource_name(config.SNS_PREFIX, service_name),
        topic_name=build_resource_name(config.SNS_PREFIX, service_name),
    )


def subscribe_sns(
    self,
    service_name: str,
    topic: sns.Topic,
    target_lambda: lambda_.Function
) -> None:
    """snsトピックをサブスクリプションする関数.

    Args:
        service_name (str): サービス名
        topic (sns.Topic): 対象のトピック
        target_lambda (lambda_.Function): トピックが通知するLambda
    """
    sns.Subscription(
        self, build_resource_name(config.SNS_SUBSCRIPTION_PREFIX, service_name),
        topic=topic,
        endpoint=target_lambda.function_arn,
        protocol=sns.SubscriptionProtocol.LAMBDA,
    )
