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
    same_as_current_version,
    publish_to_sns,
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


def is_error(res: dict) -> bool:
    """エラーメッセージが入っているか判定する関数. \n

    入っていた場合, エラーログを吐いてTrueを返す.\n
    TODO: 異常系の処理どうしよう

    Args:
        res (dict): YouTube API Response

    Returns:
        bool: エラー: True 正常: False
    """
    if res.get("error"):
        logger.error(json.dumps(res))
        return True
    return False


def service(
    yt_api_key: str,
    timedelta_days: float,
    schedule_master_table_name: str,
    notify_controller_table_name: str,
    topic_arn: str,
) -> int:

    logger.debug("Service Start!")
    
    for channel_id in get_target_channel_id_from_dyn(schedule_master_table_name):
        logger.info(f"start: {channel_id}")
        # 直近で投稿された動画の一覧を取得する
        params = {
            "publishedAfter": calc_published_after_str(float(timedelta_days)),
        }
        res_search = search(
            YT_API_KEY=yt_api_key,
            channel_id=channel_id, 
            kwags=params
        )
        if is_error(res_search):
            return 400
        
        # 取得に成功した場合, 各動画ごとに処理
        for item in res_search.get("items", []):
            logger.info(f'({item["snippet"]["channelTitle"]}) {item["snippet"]["title"]}')
            # 今後配信予定のブロードキャスト
            if is_upcoming(item) and (video_id := get_videoid_from_item(item)):

                # video_idを取得
                res_get_video = get_video(YT_API_KEY=yt_api_key, video_id=video_id)
                if is_error(res_get_video):
                    return 400

                # 各種値を取得
                title = item["snippet"]["title"]
                scheduled_start_time = res_get_video["items"][0]["liveStreamingDetails"]["scheduledStartTime"]
                version = calc_version(title, scheduled_start_time)
                dt_now = datetime.datetime.now()
                time_stamp = dt_now.strftime('%Y-%m-%d %H:%M:%S [UTC]')

                # すでに取得済みのものであればSkip
                if same_as_current_version(notify_controller_table_name, video_id, version):
                    continue

                # 先にSNSトピックにメッセージを投げる
                # この処理で失敗した場合, dbに登録されず次の定期実行にて再処理される
                lambda_input = {
                    "channel_id": channel_id,
                    "video_id": video_id,
                    "version": version,
                    "title": title,
                    "scheduled_start_time": scheduled_start_time,
                }
                dt = datetime.datetime.fromisoformat(scheduled_start_time.replace('Z', '+00:00'))
                dt_j = dt.astimezone(datetime.timezone(datetime.timedelta(hours=9)))
                notify_str = f"枠が立ちました: {title} [{dt_j.isoformat()}]"
                publish_to_sns(
                    topic_arn=topic_arn,
                    item={
                        "default": json.dumps(lambda_input, ensure_ascii=False),
                        "email": notify_str,
                        "lambda": json.dumps(lambda_input, ensure_ascii=False),
                        "sms": notify_str,
                    }
                )

                # 現状マスターの情報をもとに一連の処理を実施する決めるため, バージョン情報から書込み
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

                # マスター
                register_schedule_to_db(
                    table_name=notify_controller_table_name,
                    item={
                        "video_id": video_id,
                        "version": "master",
                        "current_version": version,
                        "time_stamp": time_stamp,
                    },
                )

                logger.info(
                    f"put event title={title} scheduled_start_time={scheduled_start_time}")
    return 200


def handler(event, context):
    return service(
        yt_api_key=get_value_from_ssm(os.environ["YOUTUBE_API_KEY"]),
        timedelta_days=os.environ["TIMEDELTA_DAYS"],
        schedule_master_table_name=os.environ["SCHEDULE_MASTER_TABLE"],
        notify_controller_table_name=os.environ["NOTIFY_CONTROLLER_TABLE"],
        topic_arn=os.environ["SNS_TOPICK_ARN"],
    )
