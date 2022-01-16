from __future__ import annotations

import json
from datetime import date, timedelta
import hashlib

import boto3
from boto3.dynamodb.conditions import Key


def get_value_from_ssm(key: str = "YT_API_KEY") -> str:
    client = boto3.client("ssm")
    value = client.get_parameter(
        Name=key,
        WithDecryption=True
    )
    return value["Parameter"]["Value"]


def calc_published_after_str(timedelta_days: float = 7.0) -> str:
    return (date.today() - timedelta(days=timedelta_days)).strftime("%Y-%m-%dT%H:%M:%SZ")


    
def get_version_from_db(table_name: str, video_id: str) -> str:
    table = boto3.resource("dynamodb").Table(table_name)
    result = table.get_item(
        Key={
            "video_id": video_id,
            "version": "master",
        }
    )
    return result["Item"]["current_version"]


def calc_version(title: str, scheduled_start_time: str) -> str:
    return hashlib.md5(f"{title}-{scheduled_start_time}".encode()).hexdigest()


def register_schedule_to_db(table_name: str, item: dict) -> None:
    table = boto3.resource("dynamodb").Table(table_name)
    table.put_item(Item=item)


def same_as_current_version(table_name: str, video_id: str, version: str) -> bool:
    table = boto3.resource("dynamodb").Table(table_name)
    res = table.get_item(Key={"video_id":video_id, "version":"master"}).get("Item")
    return bool(res and res["current_version"] == version)


def publish_to_sns(topic_arn: str, item: dict, subject: str="youtube_schedule") -> None:
    topic = boto3.resource('sns').Topic(topic_arn)
    topic.publish(
        Subject=subject,
        Message=json.dumps(item, ensure_ascii=False),
        MessageStructure="json",
    )


def delete_rule_to_lambda(rule_name: str) -> None:
    client = boto3.client('events')
    client.remove_targets(Rule=rule_name, Ids=["to_lambda",])
    client.delete_rule(Name=rule_name)

