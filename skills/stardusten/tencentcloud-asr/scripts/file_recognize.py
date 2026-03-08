# -*- coding: utf-8 -*-
"""
录音文件识别 (CreateRecTask + DescribeTaskStatus)
异步接口，支持 ≤5h (URL) 或 ≤5MB (上传) 音频。
提交任务后轮询状态直到完成。
"""

import base64
import json
import os
import subprocess
import sys
import time


def ensure_dependencies():
    try:
        import tencentcloud  # noqa: F401
    except ImportError:
        print("[INFO] tencentcloud-sdk-python not found. Installing...", file=sys.stderr)
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", "tencentcloud-sdk-python", "-q"],
            stdout=sys.stderr,
            stderr=sys.stderr,
        )
        print("[INFO] tencentcloud-sdk-python installed successfully.", file=sys.stderr)


ensure_dependencies()

from tencentcloud.common import credential
from tencentcloud.common.exception.tencent_cloud_sdk_exception import (
    TencentCloudSDKException,
)
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile
from tencentcloud.asr.v20190614 import models, asr_client


SUPPORTED_FORMATS = {"wav", "mp3", "m4a", "flv", "mp4", "wma", "3gp", "amr", "aac", "ogg-opus", "flac"}

FORMAT_EXT_MAP = {
    ".wav": "wav", ".mp3": "mp3", ".m4a": "m4a", ".flv": "flv",
    ".mp4": "mp4", ".wma": "wma", ".3gp": "3gp", ".amr": "amr",
    ".aac": "aac", ".ogg": "ogg-opus", ".opus": "ogg-opus", ".flac": "flac",
}


def guess_format(path_or_url):
    lower = path_or_url.lower().split("?")[0]
    for ext, fmt in FORMAT_EXT_MAP.items():
        if lower.endswith(ext):
            return fmt
    return "wav"


def get_credentials():
    secret_id = os.getenv("TENCENTCLOUD_SECRET_ID")
    secret_key = os.getenv("TENCENTCLOUD_SECRET_KEY")

    if not secret_id or not secret_key:
        error_msg = {
            "error": "CREDENTIALS_NOT_CONFIGURED",
            "message": (
                "Tencent Cloud API credentials not found. "
                "Please set TENCENTCLOUD_SECRET_ID and TENCENTCLOUD_SECRET_KEY."
            ),
            "guide": {
                "step1": "开通语音识别服务: https://console.cloud.tencent.com/asr",
                "step2": "获取 API 密钥: https://console.cloud.tencent.com/cam/capi",
                "step3": 'export TENCENTCLOUD_SECRET_ID="your_id" && export TENCENTCLOUD_SECRET_KEY="your_key"',
            },
        }
        print(json.dumps(error_msg, ensure_ascii=False, indent=2))
        sys.exit(1)

    token = os.getenv("TENCENTCLOUD_TOKEN")
    if token:
        return credential.Credential(secret_id, secret_key, token)
    return credential.Credential(secret_id, secret_key)


def build_asr_client(cred):
    http_profile = HttpProfile()
    http_profile.endpoint = "asr.tencentcloudapi.com"
    client_profile = ClientProfile()
    client_profile.httpProfile = http_profile
    return asr_client.AsrClient(cred, "", client_profile)


def parse_args():
    import argparse

    parser = argparse.ArgumentParser(
        description="Tencent Cloud Recording File Recognition (录音文件识别)"
    )
    parser.add_argument("input", nargs="?", help="Audio URL or local file path")
    parser.add_argument("--engine", default="16k_zh", help="Engine model type (default: 16k_zh)")
    parser.add_argument("--channel-num", type=int, default=1, choices=[1, 2],
                        help="Channel number: 1=mono, 2=dual (8k only) (default: 1)")
    parser.add_argument("--res-text-format", type=int, default=0, choices=[0, 1, 2, 3, 4, 5],
                        help="Result text format: 0=basic, 1-3=detailed, 4=nlp segment, 5=oral-to-written (default: 0)")
    parser.add_argument("--speaker-diarization", type=int, default=0, choices=[0, 1],
                        help="Speaker diarization: 0=off, 1=on (default: 0)")
    parser.add_argument("--speaker-number", type=int, default=0,
                        help="Number of speakers: 0=auto, 1-10=fixed (default: 0)")
    parser.add_argument("--poll-interval", type=int, default=5,
                        help="Polling interval in seconds (default: 5)")
    parser.add_argument("--max-poll-time", type=int, default=10800,
                        help="Max polling time in seconds (default: 10800 = 3h)")
    parser.add_argument("--no-poll", action="store_true",
                        help="Submit task only, do not poll for result (returns TaskId)")

    args = parser.parse_args()

    if not args.input:
        print(json.dumps({
            "error": "NO_INPUT",
            "message": "No audio input provided.",
            "usage": {
                "url": 'python3 file_recognize.py "https://example.com/audio.wav"',
                "file": 'python3 file_recognize.py /path/to/audio.wav (≤5MB)',
            },
        }, ensure_ascii=False, indent=2))
        sys.exit(1)

    return args


def create_rec_task(client, input_value, engine, channel_num, res_text_format, speaker_diarization, speaker_number):
    """Submit a recording file recognition task."""
    req = models.CreateRecTaskRequest()
    params = {
        "EngineModelType": engine,
        "ChannelNum": channel_num,
        "ResTextFormat": res_text_format,
        "SpeakerDiarization": speaker_diarization,
        "SpeakerNumber": speaker_number,
    }

    if input_value.startswith("http://") or input_value.startswith("https://"):
        params["SourceType"] = 0
        params["Url"] = input_value
    elif os.path.isfile(input_value):
        file_size = os.path.getsize(input_value)
        if file_size > 5 * 1024 * 1024:
            print(json.dumps({
                "error": "FILE_TOO_LARGE",
                "message": f"Local file is {file_size} bytes, exceeds 5MB limit for upload. Please use a URL instead.",
            }, ensure_ascii=False, indent=2))
            sys.exit(1)
        with open(input_value, "rb") as f:
            raw_data = f.read()
        params["SourceType"] = 1
        params["Data"] = base64.b64encode(raw_data).decode("utf-8")
        params["DataLen"] = len(raw_data)
    else:
        print(json.dumps({
            "error": "INVALID_INPUT",
            "message": f"Input '{input_value}' is neither a valid URL nor an existing file.",
        }, ensure_ascii=False, indent=2))
        sys.exit(1)

    req.from_json_string(json.dumps(params))
    resp = client.CreateRecTask(req)
    return json.loads(resp.to_json_string())


def describe_task_status(client, task_id):
    """Query the status of a recording file recognition task."""
    req = models.DescribeTaskStatusRequest()
    req.from_json_string(json.dumps({"TaskId": task_id}))
    resp = client.DescribeTaskStatus(req)
    return json.loads(resp.to_json_string())


def poll_task(client, task_id, poll_interval, max_poll_time):
    """Poll task status until completion or timeout."""
    start_time = time.time()
    status_map = {0: "waiting", 1: "doing", 2: "success", 3: "failed"}

    while True:
        elapsed = time.time() - start_time
        if elapsed > max_poll_time:
            print(json.dumps({
                "error": "POLL_TIMEOUT",
                "message": f"Task {task_id} did not complete within {max_poll_time}s.",
                "task_id": task_id,
            }, ensure_ascii=False, indent=2))
            sys.exit(1)

        result = describe_task_status(client, task_id)
        data = result.get("Data", {})
        status = data.get("Status", -1)
        status_str = status_map.get(status, f"unknown({status})")

        if status == 2:  # success
            return data
        elif status == 3:  # failed
            print(json.dumps({
                "error": "TASK_FAILED",
                "message": data.get("ErrorMsg", "Task failed"),
                "task_id": task_id,
                "status": status_str,
            }, ensure_ascii=False, indent=2))
            sys.exit(1)

        print(
            f"[INFO] Task {task_id} status: {status_str}, "
            f"elapsed: {int(elapsed)}s, next poll in {poll_interval}s...",
            file=sys.stderr,
        )
        time.sleep(poll_interval)


def main():
    args = parse_args()
    cred = get_credentials()
    client = build_asr_client(cred)

    try:
        # Step 1: Create task
        print("[INFO] Submitting recognition task...", file=sys.stderr)
        create_resp = create_rec_task(
            client, args.input, args.engine, args.channel_num,
            args.res_text_format, args.speaker_diarization, args.speaker_number,
        )

        task_data = create_resp.get("Data", {})
        task_id = task_data.get("TaskId")

        if not task_id:
            print(json.dumps({
                "error": "NO_TASK_ID",
                "message": "Failed to get TaskId from CreateRecTask response.",
                "response": create_resp,
            }, ensure_ascii=False, indent=2))
            sys.exit(1)

        print(f"[INFO] Task submitted, TaskId: {task_id}", file=sys.stderr)

        if args.no_poll:
            print(json.dumps({
                "task_id": task_id,
                "message": "Task submitted. Use --task-id to poll result later.",
            }, ensure_ascii=False, indent=2))
            return

        # Step 2: Poll for result
        data = poll_task(client, task_id, args.poll_interval, args.max_poll_time)

        result = {
            "task_id": data.get("TaskId", task_id),
            "status": "success",
            "result": data.get("Result", ""),
            "audio_duration": data.get("AudioDuration", 0),
        }

        result_detail = data.get("ResultDetail")
        if result_detail:
            result["result_detail"] = result_detail

        if data.get("ErrorMsg"):
            result["error_msg"] = data["ErrorMsg"]

        print(json.dumps(result, ensure_ascii=False, indent=2))

    except TencentCloudSDKException as err:
        print(json.dumps({
            "error": "ASR_API_ERROR",
            "code": err.code if hasattr(err, "code") else "UNKNOWN",
            "message": str(err),
        }, ensure_ascii=False, indent=2))
        sys.exit(1)
    except Exception as err:
        print(json.dumps({
            "error": "UNEXPECTED_ERROR",
            "message": str(err),
        }, ensure_ascii=False, indent=2))
        sys.exit(1)


if __name__ == "__main__":
    main()
