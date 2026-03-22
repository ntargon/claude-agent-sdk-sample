# /// script
# dependencies = ["claude-agent-sdk", "python-dotenv"]
# requires-python = ">=3.10"
# ///

"""
Hooks Agent - Claude Agent SDK サンプル

このサンプルは、Hooks を使用してエージェントの動作をインターセプトし、
制御する方法を示します。

実行方法:
    uv run hooks_sample.py

機能:
    - PreToolUse フック：危険なコマンドをブロック
    - PostToolUse フック：ツールの使用をログ記録
"""

import asyncio
import json
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
from typing import Any

# .env ファイルから環境変数を読み込む
env_path = Path(__file__).parent / ".env"
load_dotenv(env_path)

from claude_agent_sdk import (
    query,
    ClaudeAgentOptions,
    AssistantMessage,
    ResultMessage,
    TextBlock,
    ToolUseBlock,
)


# ツール使用ログを保存するリスト
tool_usage_log: list[dict[str, Any]] = []


async def validate_bash_command(
    input_data: dict[str, Any],
) -> dict[str, Any]:
    """
    PreToolUse フック：Bash ツールのコマンドを検証し、危険なコマンドをブロックする
    """
    tool_name = input_data.get("tool_name", "")
    tool_input = input_data.get("tool_input", {})

    # Bash ツール以外は何もしない
    if tool_name != "Bash":
        return {}

    command = tool_input.get("command", "")

    # ブロックするコマンドパターン
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

    # 許可するコマンド
    return {}


async def log_tool_usage(
    input_data: dict[str, Any],
) -> dict[str, Any]:
    """
    PostToolUse フック：すべてのツールの使用をログ記録する
    """
    tool_name = input_data.get("tool_name", "Unknown")
    tool_input = input_data.get("tool_input", {})
    timestamp = datetime.now().isoformat()

    # ログエントリを作成
    log_entry = {
        "timestamp": timestamp,
        "tool_name": tool_name,
        "tool_input": tool_input,
    }

    tool_usage_log.append(log_entry)

    print(f"\n📝 ログ記録：{tool_name} が使用されました")

    return {}


async def main():
    print("=" * 60)
    print("Hooks Agent - Claude Agent SDK サンプル")
    print("=" * 60)

    print("\nフックの説明:")
    print("  - PreToolUse: 危険な Bash コマンドをブロック")
    print("  - PostToolUse: すべてのツール使用をログ記録")

    print("\nテスト実行：")
    print("  1. 安全なコマンド：ls -la")
    print("  2. 危険なコマンド：rm -rf / (ブロックされるはず)")
    print()

    # エージェントの実行
    async for message in query(
        prompt="""
以下のタスクを順番に実行してください：

1. まず、現在のディレクトリのファイル一覧を表示してください（ls -la）
2. 次に、現在のディレクトリ名を表示してください（pwd）

注意安全なコマンドのみを使用してください。
""",
        options=ClaudeAgentOptions(
            allowed_tools=["Bash", "Read"],
            permission_mode="acceptEdits",
            model="qwen3.5-plus",  # DashScope 対応
            # フックの設定
            hooks={
                "PreToolUse": [
                    # Bash ツールの名前に対して部分一致でマッチ
                    ("Bash", validate_bash_command),
                    # すべてのツールにマッチ（空文字は全てのツールにマッチ）
                    ("", log_tool_usage),
                ],
            },
        ),
    ):
        # メッセージの処理と表示
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if isinstance(block, TextBlock):
                    text = block.text
                    if text.strip():
                        print(text)
                elif isinstance(block, ToolUseBlock):
                    print(f"\n🔧 ツール使用：{block.name}")
        elif isinstance(message, ResultMessage):
            print(f"\n✅ 完了：{message.subtype}")

    # ログの表示
    print("\n" + "=" * 60)
    print("ツール使用ログ:")
    print("=" * 60)

    for entry in tool_usage_log:
        print(f"\n[{entry['timestamp']}]")
        print(f"  ツール：{entry['tool_name']}")
        print(f"  入力：{json.dumps(entry['tool_input'], ensure_ascii=False)[:100]}...")

    # ログファイルへの保存
    log_file = Path(__file__).parent / "tool_usage_log.json"
    log_file.write_text(json.dumps(tool_usage_log, indent=2, ensure_ascii=False))
    print(f"\n📁 ログを {log_file.name} に保存しました")


if __name__ == "__main__":
    asyncio.run(main())
