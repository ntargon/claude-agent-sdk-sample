"""フック関数ユーティリティ"""

import json
from datetime import datetime
from typing import Any


def create_bash_validator(block_patterns: list[str] | None = None):
    """
    Bash コマンドを検証するフックファクトリ。

    Args:
        block_patterns: ブロックするコマンドパターンのリスト（デフォルト：危険なコマンド）

    Returns:
        validate_bash_command コールバック
    """
    if block_patterns is None:
        block_patterns = [
            "rm -rf /",
            "rm -rf ~",
            "sudo rm",
            "mkfs",
            "dd if=/dev/zero",
            ":(){:|:&};:",  # fork bomb
            "> /dev/sda",
            "chmod -R 777 /",
        ]

    async def validate_bash_command(input_data: dict[str, Any]) -> dict[str, Any]:
        """
        PreToolUse フック：Bash ツールのコマンドを検証し、危険なコマンドをブロックする。
        """
        tool_name = input_data.get("tool_name", "")
        tool_input = input_data.get("tool_input", {})

        # Bash ツール以外は何もしない
        if tool_name != "Bash":
            return {}

        command = tool_input.get("command", "")

        for pattern in block_patterns:
            if pattern in command:
                print(f"\n🚫 フック：危険なコマンドをブロックしました")
                print(f"   コマンド：{command}")
                print(f"   理由：パターン '{pattern}' が含まれています")

                return {
                    "hookSpecificOutput": {
                        "hookEventName": "PreToolUse",
                        "permissionDecision": "deny",
                        "permissionDecisionReason": f"セキュリティポリシーによりブロック：'{pattern}' を含むコマンドは許可されていません",
                    }
                }

        return {}

    return validate_bash_command


def create_tool_logger(log_list: list[dict[str, Any]] | None = None, verbose: bool = True):
    """
    ツール使用をログ記録するフックファクトリ。

    Args:
        log_list: ログを保存するリスト（省略時は内部で生成）
        verbose: True の場合はコンソールにも出力

    Returns:
        log_tool_usage コールバック
    """
    if log_list is None:
        log_list = []

    async def log_tool_usage(input_data: dict[str, Any]) -> dict[str, Any]:
        """
        PostToolUse フック：すべてのツールの使用をログ記録する。
        """
        tool_name = input_data.get("tool_name", "Unknown")
        tool_input = input_data.get("tool_input", {})
        timestamp = datetime.now().isoformat()

        log_entry = {
            "timestamp": timestamp,
            "tool_name": tool_name,
            "tool_input": tool_input,
        }

        log_list.append(log_entry)

        if verbose:
            print(f"\n📝 ログ記録：{tool_name} が使用されました")

        return {}

    return log_tool_usage


def save_tool_log(log_list: list[dict[str, Any]], file_path: str | None = None) -> str:
    """
    ツール使用ログをファイルに保存する。

    Args:
        log_list: 保存するログエントリのリスト
        file_path: 保存先ファイルパス（省略時は tool_usage_log.json）

    Returns:
        保存されたファイル名
    """
    from pathlib import Path

    if file_path is None:
        file_path = "tool_usage_log.json"

    target_path = Path(file_path)
    target_path.write_text(json.dumps(log_list, indent=2, ensure_ascii=False))
    return target_path.name
