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
from pathlib import Path

from utils import load_project_env, display_agent_message
from utils.hooks import create_bash_validator, create_tool_logger, save_tool_log
from claude_agent_sdk import (
    query,
    ClaudeAgentOptions,
    AssistantMessage,
    ResultMessage,
)

load_project_env()


# ツール使用ログを保存するリスト
tool_usage_log: list[dict] = []


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

    # フックの作成
    validate_bash_command = create_bash_validator()
    log_tool_usage = create_tool_logger(tool_usage_log)

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
            model="qwen3.5-plus",
            # フックの設定
            hooks={
                "PreToolUse": [
                    ("Bash", validate_bash_command),
                    ("", log_tool_usage),
                ],
            },
        ),
    ):
        display_agent_message(message)

    # ログの表示
    print("\n" + "=" * 60)
    print("ツール使用ログ:")
    print("=" * 60)

    for entry in tool_usage_log:
        print(f"\n[{entry['timestamp']}]")
        print(f"  ツール：{entry['tool_name']}")
        print(f"  入力：{str(entry['tool_input'])[:100]}...")

    # ログファイルへの保存
    log_filename = save_tool_log(tool_usage_log)
    print(f"\n📁 ログを {log_filename} に保存しました")


if __name__ == "__main__":
    asyncio.run(main())
