from __future__ import annotations

import logging
import os
import json
import datetime

import tweepy

from post_utils import (
    get_value_from_ssm,
    get_version_from_db,
    delete_rule_to_lambda,
)

# set logging
logger = logging.getLogger()
logger.setLevel(os.environ["LOG_LEVEL"])


def service(
    event: dict,
) -> int:

    logger.debug("Service Start!")
    logger.info(json.dumps(event))

    # 取得した各種キーを格納-----------------------------------------------------
    consumer_key = get_value_from_ssm(os.environ["TWITTER_API_KEY"])
    consumer_secret = get_value_from_ssm(os.environ["TWITTER_API_SECRET_KEY"])
    access_token = get_value_from_ssm(os.environ["TWITTER_ACCESS_TOKEN"])
    access_token_secret = get_value_from_ssm(os.environ["TWITTER_ACCESS_TOKEN_SECRET"])

    # Twitterオブジェクトの生成
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    api = tweepy.API(auth)
    #-------------------------------------------------------------------------

    for record in event["Records"]:
        sns_message = json.loads(record["Sns"]["Message"])
        current_version = get_version_from_db(os.environ["NOTIFY_CONTROLLER_TABLE"], sns_message["video_id"])
        if current_version != sns_message['version']:
            continue
        post_message = f"{sns_message['status']}\n{sns_message['title']}"
        api.update_status(post_message)
        delete_rule_to_lambda(sns_message["rule_name"])
        logger.info(f"delete: {sns_message['rule_name']}")

    # ツイートを投稿
    # api.update_status("test")
    
    return 200


def handler(event, context):
    return service(
        event=event,
    )
