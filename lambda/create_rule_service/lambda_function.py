from __future__ import annotations

import logging
import os
import json
import datetime

from create_utils import (
    put_event_to_sns,
)

# set logging
logger = logging.getLogger()
logger.setLevel(os.environ["LOG_LEVEL"])


def service(
    event: dict,
    topic_arn: str
):

    logger.debug("Service Start!")

    for record in event["Records"]:

        message = json.loads(record["Sns"]["Message"])
        scheduled_start_time = datetime.strptime(message["scheduled_start_time"], '%Y-%m-%dT%H:%M:%SZ')
        put_event_to_sns(
            time=scheduled_start_time,
            contents=message,
            sns_arn=topic_arn,
            event_name=f"rul_{message['channel_id']}_{message['video_id']}_sdk",
            description=message["title"]

        )


def handler(event, context):
    service(
        event=event,
        topic_arn=os.environ["POST_TWITTER_SERVICE"],
    )
