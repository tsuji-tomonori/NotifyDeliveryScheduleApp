from __future__ import annotations

import logging
import os
import json
import datetime

from api import get_video, search
from schedule_utils import (
    calc_published_after_str, 
    get_value_from_ssm,
    get_target_channel_id_from_dyn, 
    calc_version,
    register_schedule_to_db,
)

# set logging
logger = logging.getLogger()
logger.setLevel(os.environ["LOG_LEVEL"])


def is_upcoming(item: dict) -> bool | None:
    return item.get("snippet") and item["snippet"].get("liveBroadcastContent") and item["snippet"]["liveBroadcastContent"] == "upcoming"


def get_videoid_from_item(item: dict) -> str | None:
    return item.get("id", {}).get("videoId")


def build_description(item: dict) -> str:
    return f'({item.get("snippet", {}).get("channelTitle")})[{item.get("snippet", {}).get("title")}]'


def service(
    yt_api_key: str,
    timedelta_days: float,
    schedule_master_table_name: str,
    notify_controller_table_name: str,
):

    logger.debug("Service Start!")
    
    for channel_id in get_target_channel_id_from_dyn(schedule_master_table_name):

        logger.debug(f"start: {channel_id}")
        
        params = {
            "publishedAfter": calc_published_after_str(float(timedelta_days))
        }
        res_search = search(
            YT_API_KEY=yt_api_key,
            channel_id=channel_id, 
            kwags=params
        )
        logger.debug(json.dumps(res_search))
        for item in res_search.get("items", []):
            logger.debug(json.dumps(item))
            if is_upcoming(item) and (video_id := get_videoid_from_item(item)):
                res_get_video = get_video(YT_API_KEY=yt_api_key, video_id=video_id)

                # get param
                title = item["snippet"]["title"]
                scheduled_start_time = res_get_video["items"][0]["liveStreamingDetails"]["scheduledStartTime"]

                # register dynamodb
                version = calc_version(title, scheduled_start_time)
                dt_now = datetime.datetime.now()
                time_stamp = dt_now.strftime('%Y-%m-%d %H:%M:%S [UTC]')

                # master
                register_schedule_to_db(
                    table_name=notify_controller_table_name,
                    item={
                        "video_id": video_id,
                        "version": "master",
                        "current_version": version,
                        "time_stamp": time_stamp,
                    },
                )

                # current
                register_schedule_to_db(
                    table_name=notify_controller_table_name,
                    item={
                        "video_id": video_id,
                        "version": version,
                        "title": title,
                        "scheduled_start_time": scheduled_start_time,
                        "time_stamp": time_stamp,
                    },
                )

                logger.info(
                    f"[INFO] put event title={title} scheduled_start_time={scheduled_start_time}")


def handler(event, context):
    service(
        yt_api_key=get_value_from_ssm(os.environ["YOUTUBE_API_KEY"]),
        timedelta_days=os.environ["TIMEDELTA_DAYS"],
        schedule_master_table_name=os.environ["SCHEDULE_MASTER_TABLE"],
        notify_controller_table_name=os.environ["NOTIFY_CONTROLLER_TABLE"],
    )
