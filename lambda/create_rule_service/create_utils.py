from __future__ import annotations

import json
from datetime import datetime

import boto3


def put_rule_to_sns(time: datetime, contents: dict, lambda_arn: str, rule_name: str, description: str) -> None:
    """時間指定でSNSトピックにメッセージを送る関数.

    Args:
        time (datetime): 送信時刻
        contents (dict): 送信したい内容
        sns_arn (str): 対象のSNSトピックのARN
        rule_name (str): 作成するルール名
        description (str): ルールの詳細
    """
    client = boto3.client("events")
    client.put_rule(
        Name=rule_name,
        ScheduleExpression=time.strftime("cron(%M %H %d %m ? %Y)"),
        EventPattern='',
        State='ENABLED',
        Description=description,
        Tags=[
            {
                "Key": "project",
                "Value": "NotifyDeliveryScheduleApp"
            },
            {
                "Key": "service_name",
                "Value": "create_rule_service"
            },
            {
                "Key": "creater",
                "Value": "sdk"
            },
        ],
    )
    client.put_targets(
        Rule=rule_name,
        Targets=[
            {
                "Id": "to_lambda",
                "Arn": lambda_arn,
                "Input": json.dumps(contents, ensure_ascii=False)
            }
        ]
    )
