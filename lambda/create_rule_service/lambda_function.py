from __future__ import annotations

import logging
import os
import json
import datetime

from create_utils import (
    put_rule_to_sns,
)

# set logging
logger = logging.getLogger()
logger.setLevel(os.environ["LOG_LEVEL"])


def service(
    event: dict,
    lambda_arn: str
):

    logger.debug("Service Start!")

    for record in event["Records"]:

        message = json.loads(record["Sns"]["Message"])
        message["status"] = "30分後に配信が始まります"
        message["rule_name"] = f"rul_{message['channel_id']}_{message['video_id']}_30_sdk"
        scheduled_start_time = datetime.datetime.strptime(message["scheduled_start_time"], '%Y-%m-%dT%H:%M:%SZ')
        scheduled_start_time_30 = scheduled_start_time - datetime.timedelta(minutes=30)
        now_time = datetime.datetime.now()

        if scheduled_start_time_30 > now_time:
            put_rule_to_sns(
                time=scheduled_start_time_30,
                contents=message,
                lambda_arn=lambda_arn,
                rule_name=message["rule_name"],
                description=message["title"]

            )
        message["status"] = "配信が始まりました"
        message["rule_name"] = f"rul_{message['channel_id']}_{message['video_id']}_sdk"

        if scheduled_start_time > now_time:
            put_rule_to_sns(
                time=scheduled_start_time,
                contents=message,
                lambda_arn=lambda_arn,
                rule_name=message["rule_name"],
                description=message["title"]

            )


def handler(event, context):
    service(
        event=event,
        lambda_arn=os.environ["NOTIFY_SCHEDULE_SERVICE"],
    )
