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


    
def get_target_channel_id_from_dyn(table_name: str) -> list[str]:
    table = boto3.resource("dynamodb").Table(table_name)
    res = table.query(KeyConditionExpression=Key("pkey").eq("youtube"))
    return [item["channel_id"] for item in res["Items"]]


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

