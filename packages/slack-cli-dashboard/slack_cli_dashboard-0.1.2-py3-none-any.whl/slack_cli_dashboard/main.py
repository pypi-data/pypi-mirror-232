from .slack_data import SlackChannelPrioritizer, SlackMessagesPrioritizer, SlackUserData
import sys
from threading import Thread
import shutil
import time


def main():

    mode = sys.argv[-1]

    sd = SlackChannelPrioritizer()
    sd.start()
    sud = SlackUserData()

    sm = SlackMessagesPrioritizer(sd, sud)
    sm.start()

    n_lines = shutil.get_terminal_size((80, 20)).lines  # pass fallback
    print_buffer = ["" for _ in range(n_lines)]
    while True:

        try:

            merged_messages = sm.message_map
            channel_messages = [ch for ch in list(merged_messages.values()) if ch]

            if mode == "count":
                print("\u001b[2J")
                print(sm.display_message_count)
                time.sleep(6)

            else:
                for messages in channel_messages:
                    print("\u001b[2J")
                    print(f"\n{sm.display_message_count}")
                    print_buffer = ["" for _ in range(n_lines - 1)]
                    print_buffer = messages + print_buffer
                    print_buffer = print_buffer[: n_lines - 1]

                    for ms in print_buffer:
                        print(ms)

                    time.sleep(6)

        except Exception as e:
            print(e)


if __name__ == "__main__":
    main()
