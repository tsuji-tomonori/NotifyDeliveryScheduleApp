from __future__ import annotations

import logging
import os
import json
import datetime

from notify_utils import (
    publish_to_sns,
)

# set logging
logger = logging.getLogger()
logger.setLevel(os.environ["LOG_LEVEL"])


def service(
    event: dict,
    topic_arn: str,
) -> int:

    logger.debug("Service Start!")
    logger.info(event)

    dt = datetime.datetime.fromisoformat(event["scheduled_start_time"].replace('Z', '+00:00'))
    dt_j = dt.astimezone(datetime.timezone(datetime.timedelta(hours=9)))
    notify_str = f"配信が始まりました: {event['title']} [{dt_j.isoformat()}]"
    publish_to_sns(
        topic_arn=topic_arn,
        item={
            "default": json.dumps(event, ensure_ascii=False),
            "email": notify_str,
            "lambda": json.dumps(event, ensure_ascii=False),
            "sms": notify_str,
        }
    )
    
    return 200


def handler(event, context):
    return service(
        event=event,
        topic_arn=os.environ["POST_TWITTER_SERVICE"],
    )
