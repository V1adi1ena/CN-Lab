#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""使用回环地址依次启动当前版本的接收端和发送端。"""

import os
import subprocess
import sys
import time


HERE = os.path.dirname(os.path.abspath(__file__))
LOGS = os.path.join(HERE, "logs")
RECEIVER_TIMEOUT = 10


def print_output(name, output):
    print("=" * 60)
    print(f"--- {name} 输出 ---")
    print("=" * 60)
    print(output.rstrip())


def main():
    os.makedirs(LOGS, exist_ok=True)

    receiver_path = os.path.join(HERE, "receiver.py")
    sender_path = os.path.join(HERE, "sender.py")
    receiver_log = os.path.join(LOGS, "local_receiver.log")
    sender_log = os.path.join(LOGS, "local_sender.log")

    # 子进程输出使用 UTF-8，并让接收端立即输出启动信息。
    child_env = os.environ.copy()
    child_env["PYTHONIOENCODING"] = "utf-8"

    # 接收端逐包输出较多，直接写日志可避免管道缓冲区被写满后阻塞。
    with open(receiver_log, "w", encoding="utf-8") as receiver_log_file:
        receiver = subprocess.Popen(
            [sys.executable, "-u", receiver_path],
            stdout=receiver_log_file,
            stderr=subprocess.STDOUT,
            env=child_env,
        )

        time.sleep(0.5)
        if receiver.poll() is not None:
            receiver_log_file.flush()
            with open(receiver_log, encoding="utf-8") as log_file:
                receiver_output = log_file.read()
            print_output("receiver", receiver_output)
            print("接收端没有成功启动，未运行发送端。")
            return 1

        sender_result = subprocess.run(
            [sys.executable, sender_path, "127.0.0.1"],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="replace",
            env=child_env,
            timeout=RECEIVER_TIMEOUT,
        )
        sender_output = sender_result.stdout

        try:
            receiver.wait(timeout=RECEIVER_TIMEOUT)
            timed_out = False
        except subprocess.TimeoutExpired:
            receiver.kill()
            receiver.wait()
            timed_out = True

    with open(receiver_log, encoding="utf-8") as log_file:
        receiver_output = log_file.read()
    with open(sender_log, "w", encoding="utf-8") as log_file:
        log_file.write(sender_output)

    print_output("receiver", receiver_output)
    print_output("sender", sender_output)

    if sender_result.returncode != 0:
        print(f"发送端运行失败，退出码：{sender_result.returncode}")
        return 1
    if timed_out:
        print("接收端等待超时，可能没有收到 END。")
        return 1
    if receiver.returncode != 0:
        print(f"接收端运行失败，退出码：{receiver.returncode}")
        return 1

    print(f"日志已保存到：{LOGS}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
