import os
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
import time
from pathlib import Path
import json
import re
import datetime
import random

from queue import PriorityQueue
import colorful as cf
from .asynchronous.threads import TestableThread


class SlackMessagesPrioritizer(TestableThread):
    def __init__(self, slack_data, slack_user_data):
        self.client = WebClient(token=os.environ["SLACK_TOKEN"])
        self.slack_data = slack_data
        self.slack_user_data = slack_user_data
        self.n_chars = os.get_terminal_size().columns
        self.message_map = {}
        self.high_priority_map = {}
        self.iter_message_count = 0
        self.display_message_count = 0
        self.full_message_count = 0

        self.message_update_queue = PriorityQueue()

        super().__init__(name="SlackMessagePrioritizer", target=self.__run)
        # shutil.get_terminal_size((80, 20)).columns  # pass fallback

    def __run(self):

        while True:

            self.iter_message_count = 0
            self.slack_user_data.refresh()
            for ch in list(self.slack_data.convo_cache.values()):
                # print(ch.get("jm_priority"))
                self.message_update_queue.put(
                    (ch.get("jm_priority", 100_000_000), ch["id"])
                )

            while not self.message_update_queue.empty():
                (_, ch_id) = self.message_update_queue.get()
                if self.slack_data.convo_cache.get(ch_id):
                    # print(ch_id)
                    # print(self.slack_data.convo_cache[ch_id])
                    messages = self.__query_for_channel(
                        self.slack_data.convo_cache[ch_id]
                    )

                    self.message_map[ch_id] = messages

                # print(self.message_map)

                self.display_message_count = sum(
                    [len(ms) for ms in self.message_map.values()]
                )

    def __query_for_channel(self, ch):
        # print(ch)
        try:

            time.sleep(1)
            messages = self.client.conversations_history(
                channel=ch["id"],
                oldest=ch.get("last_read", time.time()),
                inclusive=False,
            )["messages"][:-1]

            try:
                channel_name = ch.get(
                    "name",
                    self.slack_user_data.user_cache.get(ch.get("user"), "Unknown"),
                )
            except:
                print("EXCEPTION")
                time.sleep(20)
            messages = [
                self.format_message(m, channel_name)
                for m in messages
                if self.should_show(m)
            ]

            # if len(messages) >= 1:
            # ch["jm_priority"] += 100_000
            # self.message_update_queue.put((ch["jm_priority"], ch["id"]))

            return list(reversed(messages))
        except Exception as e:
            # raise e
            print("EXCEPTION")
            print(e)

        return []

    def get_high_priority(self):

        high_freq = [
            self.slack_data.get_channel_by_id(k)
            for k, v in self.message_map.items()
            if v
        ]

        for ch in high_freq:
            messages = self.__query_for_channel(ch)
            self.high_priority_map[ch["id"]] = messages

    def get_messages(self):
        # add private/dm
        # add way to prioritize refreshing channels that already have data

        for ch in sorted(
            list(self.slack_data.convo_cache.values()),
            key=lambda x: float(x.get("jm_priority", time.time())),
            reverse=False,
        ):
            messages = self.__query_for_channel(ch)
            self.message_map[ch["id"]] = messages

    def should_show(self, message):
        message_text = message["text"]
        if len(message_text) == 0:
            return False

        if message.get("subtype") == "bot_message":
            return False

        if "has left the channel" in message_text:
            return False
        if "has joined the channel" in message_text:
            return False

        return True

    def format_message(self, message, channel_name):
        channel_name = channel_name
        message_time = datetime.datetime.fromtimestamp(float(message["ts"]))
        time_str = message_time.strftime("%b %d %H:%M")
        sender = self.slack_user_data.user_cache.get(message.get("user"), "Unknown")

        unstyled_leader = f"({time_str})" + f" #{channel_name} " + f"| {sender}:"

        max_text_chars = self.n_chars - len(unstyled_leader)
        raw_text = message["text"]
        if len(raw_text) > max_text_chars:
            raw_text = raw_text[: max_text_chars - 4] + "..."
        formatted_message = re.sub(
            "<\@[UW][^>]*>",
            lambda x: ""
            + cf.cyan(
                "@" + self.slack_user_data.user_cache.get(x.group(0)[2:-1], x.group(0))
            ),
            raw_text,
        ).replace("\n", "")

        leader = (
            cf.bold_black_on_white(f"({time_str})")
            + f" #{channel_name} "
            + cf.bold_black_on_white(f"| {sender}:")
        )

        message = f"{leader} {formatted_message}"

        return message


class SlackMessages:
    def __init__(self, slack_data):
        self.client = WebClient(token=os.environ["SLACK_TOKEN"])
        self.slack_data = slack_data
        self.n_chars = os.get_terminal_size().columns
        self.message_map = {}
        self.high_priority_map = {}
        # shutil.get_terminal_size((80, 20)).columns  # pass fallback

    def __query_for_channel(self, ch):
        # print(ch)
        try:
            if (
                datetime.datetime.utcnow()
                - datetime.datetime.fromtimestamp(
                    float(ch.get("last_read", time.time()))
                )
            ).days > 1:
                return []

            time.sleep(1)
            messages = self.client.conversations_history(
                channel=ch["id"],
                oldest=ch.get("last_read", time.time()),
                inclusive=False,
            )["messages"][:-1]

            try:
                channel_name = ch.get(
                    "name", self.slack_data.user_cache.get(ch.get("user"), "Unknown")
                )
            except:
                print(ch)
                time.sleep(20)
            messages = [
                self.format_message(m, channel_name)
                for m in messages
                if self.should_show(m)
            ]

            return list(reversed(messages))
        except Exception as e:
            # raise e
            print(e)

    def get_high_priority(self):

        high_freq = [
            self.slack_data.get_channel_by_id(k)
            for k, v in self.message_map.items()
            if v
        ]

        for ch in high_freq:
            messages = self.__query_for_channel(ch)
            self.high_priority_map[ch["id"]] = messages

    def get_messages(self):
        # add private/dm

        # add way to prioritize refreshing channels that already have data

        for ch in sorted(
            list(self.slack_data.convo_cache.values()),
            key=lambda x: float(x.get("jm_priority", time.time())),
            reverse=False,
        ):
            messages = self.__query_for_channel(ch)
            self.message_map[ch["id"]] = messages

    def should_show(self, message):
        message_text = message["text"]
        if len(message_text) == 0:
            return False

        if message.get("subtype") == "bot_message":
            return False

        if "has left the channel" in message_text:
            return False
        if "has joined the channel" in message_text:
            return False

        return True

    def format_message(self, message, channel_name):
        channel_name = channel_name
        message_time = datetime.datetime.fromtimestamp(float(message["ts"]))
        time_str = message_time.strftime("%b %d %H:%M")
        sender = self.slack_data.user_cache.get(message.get("user"), "Unknown")

        unstyled_leader = f"({time_str})" + f" #{channel_name} " + f"| {sender}:"

        max_text_chars = self.n_chars - len(unstyled_leader)
        raw_text = message["text"]
        if len(raw_text) > max_text_chars:
            raw_text = raw_text[: max_text_chars - 4] + "..."
        formatted_message = re.sub(
            "<\@[UW][^>]*>",
            lambda x: ""
            + cf.cyan(
                "@" + self.slack_data.user_cache.get(x.group(0)[2:-1], x.group(0))
            ),
            raw_text,
        ).replace("\n", "")

        leader = (
            cf.bold_black_on_white(f"({time_str})")
            + f" #{channel_name} "
            + cf.bold_black_on_white(f"| {sender}:")
        )

        message = f"{leader} {formatted_message}"

        return message


class SlackChannelPrioritizer(TestableThread):
    def __init__(self):
        self.client = WebClient(token=os.environ["SLACK_TOKEN"])

        self.info_update_queue = PriorityQueue()

        self.cache_file_path = Path("slack_data_cache.json")
        self.convo_cache = self.__load()

        super().__init__(name="ChannelPrioritizer", target=self.__run)

    def __save(self):
        with open(self.cache_file_path, "w") as fh:
            json.dump(self.convo_cache, fh)

        self.last_updated = datetime.datetime.utcnow()

    def __load(self):

        convo_cache = {}

        if self.cache_file_path.exists():
            try:
                with open(self.cache_file_path, "r") as fh:
                    convo_cache = json.load(fh)
            except:
                print("could not load convo cache, skipping...")

        return convo_cache

    def __run(self):
        while True:
            # print("LOOP START!!!!!!!!!!!")
            with self.info_update_queue.mutex:
                self.info_update_queue.queue.clear()

            self.__get_conversation_info()
            # print(len(self.convo_cache.keys()))
            for ch in list(self.convo_cache.values()):
                ch = self.__set_priority(ch)
                # print((ch["jm_priority"], ch))
                self.info_update_queue.put((ch["jm_priority"], ch["id"]))
            while not self.info_update_queue.empty():
                (_, ch_id) = self.info_update_queue.get()
                ch = self.convo_cache[ch_id]
                self.__update_channel_info(ch)
            self.__save()

    def __set_priority(self, ch):
        msg_type_map = {"is_im": 100, "is_mpim": 50, "is_private": 50}

        jm_priority = 0
        for key, value in msg_type_map.items():
            if ch.get(key):
                jm_priority += value
            else:
                jm_priority = 300

        last_read = ch.get("last_read", 0)

        minutes_since_read = (
            datetime.datetime.utcnow()
            - datetime.datetime.fromtimestamp(float(last_read))
        )
        jm_priority = jm_priority + (minutes_since_read.total_seconds() / 60) ** 2

        ch["jm_priority"] = int(jm_priority)

        return ch

    def __should_cache(self, ch):
        if self.__channel_read_timedelta(ch) > datetime.timedelta(days=10):
            if not (
                ch.get("is_private", False)
                or ch.get("is_im", False)
                or ch.get("is_mpim", False)
            ):
                # print(f"unsubscribed from {ch}")
                self.client.conversations_leave(channel=ch["id"])
            return False
        else:
            return True

    def __channel_read_timedelta(self, ch):
        if not ch.get("last_read"):
            return datetime.timedelta(days=11)
        else:
            return datetime.datetime.utcnow() - datetime.datetime.fromtimestamp(
                float(ch["last_read"])
            )

    def __get_all_channels(self):
        convo_type = "public_channel"
        public = self.__get_all_conversations_of_type(convo_type)

        convo_type = "private_channel"
        private = self.__get_all_conversations_of_type(convo_type)

        convo_type = "mpim"
        mpim = self.__get_all_conversations_of_type(convo_type)

        convo_type = "im"
        im = self.__get_all_conversations_of_type(convo_type)

        return public + private + mpim + im

    def __get_all_conversations_of_type(self, convo_type):
        next_cursor = None
        channels = []
        while True:
            response = self.client.users_conversations(
                cursor=next_cursor,
                limit=1000,
                exclude_archived=True,
                types=convo_type,
            )
            next_cursor = response["response_metadata"].get("next_cursor")
            channels += [
                channel
                for channel in response["channels"]
                if channel.get("is_member") in [True, None]
                and channel.get("is_user_deleted") in [False, None]
                and channel.get("is_archived") in [False, None]
            ]
            if next_cursor == "":
                break

        return channels

    def __get_conversation_info(self):

        try:

            # print(self.info_update_queue.qsize())
            new_channels = self.__get_all_channels()
            for ch in new_channels:
                self.convo_cache[ch["id"]] = {
                    **self.convo_cache.get(ch["id"], {}),
                    **ch,
                }

            for ch_id, ch in dict(self.convo_cache).items():
                if not self.__should_cache(ch):
                    self.convo_cache.pop(ch_id)

            self.__save()

        except SlackApiError as e:
            # You will get a SlackApiError if "ok" is False
            assert e.response.get("ok", False) is False
            assert e.response["error"]  # str like 'invalid_auth', 'channel_not_found'
            print(f"Got an error: {e.response}")
            time.sleep(30)

    def __update_channel_info(self, ch):
        # print("updating...")
        # print(ch["jm_priority"])
        # print(ch)
        try:
            response = self.client.conversations_info(channel=ch["id"])
            time.sleep(0.75)

            ch["last_read"] = float(response["channel"]["last_read"])

            if self.__should_cache(ch):
                self.convo_cache[ch["id"]] = ch
            else:
                # print("channel old!!!!")
                self.convo_cache.pop(ch["id"])

            self.__save()
        except SlackApiError as e:
            # You will get a SlackApiError if "ok" is False
            assert e.response.get("ok", False) is False
            assert e.response["error"]  # str like 'invalid_auth', 'channel_not_found'

            print(f"Got an error: {e.response}")

            if e.response["error"] == "channel_not_found":
                self.convo_cache.pop(ch["id"])
            else:
                time.sleep(30)
                self.__update_channel_info(ch)


class SlackUserData:
    default_user_cache = {}

    def __init__(self):
        self.client = WebClient(token=os.environ["SLACK_TOKEN"])
        self.user_file_path = Path("slack_user_lookup.json")

        self.user_cache = self.__load()
        self.last_updated = 0
        self.user_update_interval_seconds = 3600
        self.last_user_update = 0  # time.time()

    def __save(self):

        with open(self.user_file_path, "w") as fh:
            json.dump(self.user_cache, fh)

        self.last_updated = datetime.datetime.utcnow()

    def __load(self):

        user_cache = self.default_user_cache

        if self.user_file_path.exists():
            try:
                with open(self.user_file_path, "r") as fh:
                    user_cache = {**user_cache, **json.load(fh)}
            except:
                print("could not load user cache, skipping...")

        return user_cache

    def refresh(self):
        if time.time() - self.last_user_update > self.user_update_interval_seconds:
            self.__get_user_cache()

    def __get_user_cache(self):
        next_cursor = None

        while True:
            response = self.client.users_list(
                cursor=next_cursor,
                limit=1000,
                exclude_archived=True,
            )

            for user in response["members"]:
                self.user_cache[user["id"]] = user["name"]

            next_cursor = response["response_metadata"].get("next_cursor")
            if next_cursor == "":
                break
            self.__save()


if __name__ == "__main__":
    # cp = SlackChannelPrioritizer()
    # cp.start()

    sd = SlackChannelPrioritizer()
    sd.start()
    sud = SlackUserData()

    sm = SlackMessagesPrioritizer(sd, sud)
    sm.start()
