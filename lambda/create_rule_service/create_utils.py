from __future__ import annotations

import json
from datetime import datetime

import boto3


def put_event_to_sns(time: datetime, contents: dict, lambda_arn: str, event_name: str, description: str) -> None:
    """時間指定でSNSトピックにメッセージを送る関数.

    Args:
        time (datetime): 送信時刻
        contents (dict): 送信したい内容
        sns_arn (str): 対象のSNSトピックのARN
        event_name (str): 作成するイベント名
        description (str): イベントの詳細
    """
    client = boto3.client("events")
    client.put_rule(
        Name=event_name,
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
        Rule=event_name,
        Targets=[
            {
                "Id": "to_lambda",
                "Arn": lambda_arn,
                "Input": json.dumps(contents, ensure_ascii=False)
            }
        ]
    )
