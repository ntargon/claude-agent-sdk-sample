# /// script
# dependencies = ["anthropic"]
# requires-python = ">=3.9"
# ///

"""
Claude API サンプルスクリプト

実行方法:
    uv run claude_sample.py

事前準備:
    環境変数 ANTHROPIC_API_KEY に API キーを設定してください。
    export ANTHROPIC_API_KEY="your-api-key-here"

    Alibaba Cloud DashScope を使用する場合は、
    ANTHROPIC_BASE_URL も設定してください。
"""

import os
from anthropic import Anthropic


def main():
    # API クライアントの初期化
    # 環境変数 ANTHROPIC_API_KEY から自動的に API キーを取得
    # ANTHROPIC_BASE_URL が設定されていれば、自動的にそのエンドポイントを使用
    client = Anthropic()

    # メッセージの送信
    message = client.messages.create(
        max_tokens=1024,
        messages=[
            {
                "role": "user",
                "content": "Hello, Claude! Python から挨拶しています。",
            }
        ],
        model="claude-opus-4-6-20251101",
    )

    # レスポンスの表示
    print("レスポンス:")
    print(message.content[0].text)


if __name__ == "__main__":
    main()
