import json
import requests
import time
import sys
import os
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import logging
from typing import Any, Literal
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Client:
    def __init__(self, token) -> None:
        self._token = token
        self._headers = {"Authorization": "Bearer {}".format(token)}
        self._session = requests.Session()
        self._session.mount(
            "https://slack.com/",
            HTTPAdapter(max_retries=Retry(total=5, backoff_factor=3)),
        )

    def _call(self, url, params=None) -> dict[str, Any]:
        if not params:
            params = {}

        response = self._session.get(url, headers=self._headers, params=params, timeout=3)
        response.raise_for_status()
        return response.json()

    def fetch_users(self) -> list[dict[str, Any]]:
        """ユーザーをすべて取得する
        References:
            - https://api.slack.com/methods/users.list
        """
        response = self._call("https://slack.com/api/users.list")
        return response["members"]

    def fetch_channels(self) -> list[dict[str, Any]]:
        """チャンネルをすべて取得する
        References:
            - https://api.slack.com/methods/conversations.list
        """
        response = self._call(
            "https://slack.com/api/conversations.list",
            params={
                # "types": "public_channel,private_channel,mpim,im",
                "types": "public_channel,private_channel",
                "exclude_archived": True,
            },
        )
        return response["channels"]

    def fetch_messages(self, channel_id: str) -> list[dict[str, Any]]:
        """指定したチャンネルのメッセージ（スレッドを除く）をすべて取得する
        References:
            - https://api.slack.com/methods/conversations.history
        """
        messages = []
        next_cursor = None
        while True:
            params = {"channel": channel_id, "limit": 200}
            if next_cursor:
                params["cursor"] = next_cursor

            response = self._call("https://slack.com/api/conversations.history", params=params)
            messages += response["messages"]

            if response["has_more"]:
                next_cursor = response["response_metadata"]["next_cursor"]
            else:
                break

        return messages

    def fetch_replies(self, channel_id: str, thread_ts: float) -> list[dict[str, Any]]:
        """指定したチャンネル・時刻のスレッド内のメッセージをすべて取得する
        References:
            - https://api.slack.com/methods/conversations.replies
        """
        replies = []
        next_cursor = None
        while True:
            payload = {"channel": channel_id, "limit": 200, "ts": thread_ts}
            if next_cursor:
                payload["cursor"] = next_cursor

            response = self._call("https://slack.com/api/conversations.replies", params=payload)

            done = False
            for message in response["messages"]:
                if message["ts"] == thread_ts and len(replies) > 0:
                    done = True
                    break

                replies.append(message)

            if done:
                break
            elif response["has_more"]:
                next_cursor = response["response_metadata"]["next_cursor"]

        return replies

    def get_file(self,url) -> list[dict[str, Any]]:
        response = self._session.get(url, headers=self._headers, timeout=3)
        return response






def main(TOKEN: str,attachment_files_dir: Path,output_format: Literal["json", "jsonl"] = "json"):

    client = Client(TOKEN)

    logger.info("Fetching channels")
    channels = client.fetch_channels()

    for channel in channels:
        channel_id = channel["id"]
        channel_name = channel.get("name")

        logger.info(f"Fetching messages: {channel_name=}")
        messages = client.fetch_messages(channel_id)

        messages_and_replies = []
        for message in reversed(messages):
            thread_ts = message.get("thread_ts")
            if not thread_ts:
                messages_and_replies.append(message)
                continue

            replies = client.fetch_replies(channel_id, thread_ts)
            messages_and_replies += replies

        for messages_and_replie in messages_and_replies:
            if('files' in messages_and_replie):
                files = messages_and_replie['files']
                msg_id = messages_and_replie['client_msg_id']
                for file in files:
                    if(file['filetype'] not in ['quip']):
                        download_url = file['url_private_download']
                        response = client.get_file(download_url)
                        response.raise_for_status()
                        file_name = file['name']
                        filename = f"./{attachment_files_dir}/{msg_id}_{file_name}"
                        with open(filename, 'wb') as f:
                            f.write(response.content)
                            logger.info(f"file: {filename=}")
                        time.sleep(1)
        logger.info(f"{len(messages_and_replies)} messages/replies fetched")
    print('end')


if __name__ == '__main__':
    if(len(sys.argv)<2):
        token = input('TOKEN : ')
    else:
        token = sys.argv[1]

    attachment_files_dir = "files"
    if not os.path.exists(attachment_files_dir):
        # ディレクトリが存在しない場合、ディレクトリを作成する
        os.makedirs(attachment_files_dir)

    main(token,Path(attachment_files_dir))
