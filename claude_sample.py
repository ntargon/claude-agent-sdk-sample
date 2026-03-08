# /// script
# dependencies = ["anthropic", "python-dotenv"]
# requires-python = ">=3.9"
# ///

"""
Claude API サンプルスクリプト

実行方法:
    uv run claude_sample.py

事前準備:
    .env.example を .env にコピーして API キーを設定してください。
    cp .env.example .env
"""

from pathlib import Path
from dotenv import load_dotenv

# .env ファイルから環境変数を読み込む
env_path = Path(__file__).parent / ".env"
load_dotenv(env_path)

from anthropic import Anthropic


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
                "content": "Hello, Claude! Python から挨拶しています。",
            }
        ],
        model="qwen3.5-plus",
    )

    # レスポンスの表示
    print("レスポンス:")
    print(message.content[0].text)


if __name__ == "__main__":
    main()
