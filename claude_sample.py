"""
Claude API サンプルスクリプト

実行方法:
    uv run claude_sample.py

事前準備:
    .env.example を .env にコピーして API キーを設定してください。
    cp .env.example .env
"""

from utils import load_project_env
from anthropic import Anthropic

load_project_env()


def main():
    # API クライアントの初期化
    # 環境変数 ANTHROPIC_API_KEY, ANTHROPIC_BASE_URL を自動的に取得
    client = Anthropic()

    # メッセージの送信
    message = client.messages.create(
        max_tokens=1024,
        messages=[
            {
                "role": "user",
                "content": "Hello! Python から挨拶しています。",
            }
        ],
        model="qwen3.5-plus",
    )

    # レスポンスの表示
    print("レスポンス:")
    for block in message.content:
        # ThinkingBlock は text 属性を持たないので型をチェック
        if hasattr(block, "text"):
            print(block.text)
        elif hasattr(block, "thinking"):
            print("<think>")
            print(block.thinking)
            print("</think>")


if __name__ == "__main__":
    main()
