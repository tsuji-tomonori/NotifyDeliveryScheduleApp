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
        message["status"] = "配信がはじまりました"
        message["rule_name"] = f"rul_{message['channel_id']}_{message['video_id']}_sdk"
        scheduled_start_time = datetime.datetime.strptime(message["scheduled_start_time"], '%Y-%m-%dT%H:%M:%SZ')
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
