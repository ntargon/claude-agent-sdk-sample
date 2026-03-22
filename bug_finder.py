# /// script
# dependencies = ["claude-agent-sdk", "python-dotenv"]
# requires-python = ">=3.10"
# ///

"""
Bug Finder Agent - Claude Agent SDK サンプル

このサンプルは、コードのバグを検出して修正するエージェントを実装します。

実行方法:
    uv run bug_finder.py

事前準備:
    1. .env ファイルに ANTHROPIC_API_KEY を設定
    2. 必要に応じて test_code.py などのテストファイルを用意
"""

import asyncio
from pathlib import Path
from dotenv import load_dotenv

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


# テスト用のバグを含んだコード（必要に応じて作成）
TEST_CODE = '''
def calculate_average(numbers):
    total = 0
    for num in numbers:
        total += num
    return total / len(numbers)


def get_user_name(user):
    return user["name"].upper()


def divide(a, b):
    return a / b
'''


async def main():
    # テスト用ファイルの作成
    test_file = Path(__file__).parent / "test_code.py"

    print("=" * 60)
    print("Bug Finder Agent - Claude Agent SDK サンプル")
    print("=" * 60)

    # テストファイルが存在しない場合、作成する
    if not test_file.exists():
        print(f"\nテストファイル {test_file.name} を作成します...")
        test_file.write_text(TEST_CODE)
        print("以下のバグを含んだコードを作成しました:")
        print("-" * 40)
        print(TEST_CODE)
        print("-" * 40)

    print("\nエージェントがコードのバグを検出して修正します...\n")

    # エージェントの実行
    async for message in query(
        prompt=f"""
{test_file.name} をレビューして、クラッシュを引き起こす可能性のあるバグをすべて見つけてください。

以下の点に注目してください:
1. 例外処理の欠如
2. 境界条件のチェック不足
3. None 値への対応不足

見つけたバグをすべて修正し、安全なコードにしてください。
""",
        options=ClaudeAgentOptions(
            allowed_tools=["Read", "Edit", "Glob"],  # 使用するツール
            permission_mode="acceptEdits",  # ファイル編集を自動承認
        ),
    ):
        # メッセージの処理と表示
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if isinstance(block, TextBlock):
                    # Claude の思考プロセスを表示
                    text = block.text
                    if text.strip():  # 空行はスキップ
                        print(text)
                elif isinstance(block, ToolUseBlock):
                    # ツールの使用を表示
                    print(f"\n🔧 ツール使用：{block.name}")
                    if hasattr(block, "input") and block.input:
                        # ファイル編集の場合は簡潔に表示
                        if block.name == "Edit":
                            print(f"   ファイルを編集中...")
        elif isinstance(message, ResultMessage):
            print(f"\n✅ 完了：{message.subtype}")

    # 結果の確認
    print("\n" + "=" * 60)
    print("修正後のコード:")
    print("=" * 60)
    if test_file.exists():
        print(test_file.read_text())


if __name__ == "__main__":
    asyncio.run(main())
