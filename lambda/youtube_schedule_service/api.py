import requests


def search(YT_API_KEY: str, channel_id:str, page_token=None, kwags=None) -> dict:
    """API リクエストで指定したクエリ パラメータに一致する検索結果のコレクションを返します.

    channel ID をもとに video ID を取得することがここでの主目的 \n
    channel ID は「https://www.youtube.com/channel/UCuvk5PilcvDECU7dDZhQiEw」 /channel/配下の文字列 \n
    一回で取得できる最大数は50件までであるため, それ以上取得する場合は page_tokeを使用する


    Args:
        YT_API_KEY ([String]): YoutTube API Key
        channel_id ([String]): channel ID
        page_token ([String]): page_token デフォルト: None (使用しない場合)
        kwags      ([dict])  : 今回設定していないパラメタを設定する場合に必要

    Returns:
        [dict]: 取得したデータ
    """

    url = "https://www.googleapis.com/youtube/v3/search"
    params = {
        "key": YT_API_KEY,
        "channelId": channel_id,
        "part": "id,snippet",
        "maxResults": 50}
    if page_token is not None:
        params["pageToken"] = page_token
    if kwags is not None:
        params.update(kwags)
    return requests.get(url, params=params).json()


def get_video(YT_API_KEY, video_id, page_token=None, kwags=None):
    """API リクエストのパラメータに一致する動画のリストを返します.

    予定開始時刻を取得することがここでの主目的 \n
    video ID が必要なため, 事前に取得しておく必要がある \n
    一回で取得できる最大数は50件までであるため, それ以上取得する場合は page_tokeを使用する


    Args:
        YT_API_KEY ([String])         : YoutTube API Key
        video_id   ([String])         : Video ID
        page_token ([String])         : page_token デフォルト: None (使用しない場合)
        kwags      ([type], optional) : 今回設定していないパラメタを設定する場合に必要 Defaults to None.

    Returns:
        [type]: 取得したデータ
    """
    url = "https://www.googleapis.com/youtube/v3/videos"
    params = {
        "key": YT_API_KEY,
        "id": video_id,
        "part": "liveStreamingDetails",
        "maxResults": 50}
    if page_token is not None:
        params["pageToken"] = page_token
    if kwags is not None:
        params.update(kwags)
    return requests.get(url, params=params).json()
