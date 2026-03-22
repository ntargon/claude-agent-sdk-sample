# /// script
# dependencies = ["claude-agent-sdk", "python-dotenv"]
# requires-python = ">=3.10"
# ///

"""
Custom Tools Agent - Claude Agent SDK サンプル

このサンプルは、カスタム MCP ツールを定義してエージェントに統合する方法を示します。

実行方法:
    uv run custom_tools.py

機能:
    - 天気情報を取得するツール
    - 計算を行うツール
    - 変換を行うツール
"""

import asyncio
import random
from pathlib import Path
from dotenv import load_dotenv
from typing import Any

# .env ファイルから環境変数を読み込む
env_path = Path(__file__).parent / ".env"
load_dotenv(env_path)

from claude_agent_sdk import (
    query,
    tool,
    create_sdk_mcp_server,
    ClaudeAgentOptions,
    AssistantMessage,
    ResultMessage,
    TextBlock,
    ToolUseBlock,
)


# カスタムツールの定義

@tool(
    "get_weather",
    "指定した都市の天気情報を取得します",
    {
        "city": {
            "type": "string",
            "description": "都市名（例：Tokyo, New York, London）"
        }
    }
)
async def get_weather(args: dict[str, Any]) -> dict[str, Any]:
    """天気情報を返すモックツール"""
    city = args.get("city", "Unknown")

    # モックの天気データ（実際には API を呼び出す）
    weather_conditions = ["晴れ", "曇り", "雨", "雷雨", "雪"]
    temperatures = {
        "Tokyo": 25,
        "New York": 22,
        "London": 18,
        "Paris": 20,
        "Sydney": 28,
    }

    temp = temperatures.get(city, random.randint(15, 30))
    condition = random.choice(weather_conditions)

    return {
        "content": [
            {
                "type": "text",
                "text": f"{city} の天気：{condition}, 気温：{temp}°C"
            }
        ]
    }


@tool(
    "calculate",
    "数値計算を行います（加算、減算、乗算、除算）",
    {
        "operation": {
            "type": "string",
            "description": "演算子：add, subtract, multiply, divide"
        },
        "a": {
            "type": "number",
            "description": "最初の数値"
        },
        "b": {
            "type": "number",
            "description": "2 番目の数値"
        }
    }
)
async def calculate(args: dict[str, Any]) -> dict[str, Any]:
    """計算を行うツール"""
    operation = args.get("operation", "add")
    a = float(args.get("a", 0))
    b = float(args.get("b", 0))

    operations = {
        "add": lambda x, y: x + y,
        "subtract": lambda x, y: x - y,
        "multiply": lambda x, y: x * y,
        "divide": lambda x, y: x / y if y != 0 else "Error: Division by zero",
    }

    result = operations.get(operation, lambda x, y: x + y)(a, b)

    return {
        "content": [
            {
                "type": "text",
                "text": f"{a} {operation} {b} = {result}"
            }
        ]
    }


@tool(
    "convert_currency",
    "通貨を変換します（簡易的なモックレート）",
    {
        "amount": {
            "type": "number",
            "description": "変換する金額"
        },
        "from_currency": {
            "type": "string",
            "description": "元の通貨（USD, EUR, JPY, GBP）"
        },
        "to_currency": {
            "type": "string",
            "description": "変換先の通貨（USD, EUR, JPY, GBP）"
        }
    }
)
async def convert_currency(args: dict[str, Any]) -> dict[str, Any]:
    """通貨変換を行うツール（モックレート）"""
    # モックの為替レート（USD 基準）
    rates = {
        "USD": 1.0,
        "EUR": 0.85,
        "JPY": 110.0,
        "GBP": 0.73,
    }

    amount = float(args.get("amount", 0))
    from_currency = args.get("from_currency", "USD").upper()
    to_currency = args.get("to_currency", "USD").upper()

    if from_currency not in rates or to_currency not in rates:
        return {
            "content": [
                {
                    "type": "text",
                    "text": f"Error: サポートされていない通貨 - {from_currency} or {to_currency}"
                }
            ]
        }

    # USD に変換してから目標通貨に変換
    usd_amount = amount / rates[from_currency]
    result = usd_amount * rates[to_currency]

    return {
        "content": [
            {
                "type": "text",
                "text": f"{amount} {from_currency} = {result:.2f} {to_currency}"
            }
        ]
    }


async def main():
    print("=" * 60)
    print("Custom Tools Agent - Claude Agent SDK サンプル")
    print("=" * 60)

    # カスタムツールを含む MCP サーバーを作成
    custom_server = create_sdk_mcp_server(
        name="custom-tools",
        version="1.0.0",
        tools=[get_weather, calculate, convert_currency],
    )

    print("\n以下のカスタムツールを利用可能です:")
    print("  - get_weather: 天気情報を取得")
    print("  - calculate: 数値計算")
    print("  - convert_currency: 通貨変換")
    print("\nエージェントに質問してください...\n")

    # エージェントの実行
    async for message in query(
        prompt="""
以下の質問に答えてください：

1. Tokyo の天気を教えてください
2. 123 × 456 を計算してください
3. 100 USD を JPY に変換してください

カスタムツールを使用して、各質問に答えてください。
""",
        options=ClaudeAgentOptions(
            allowed_tools=["Read", "Write", "Bash", "mcp__custom-tools__*"],
            mcp_servers={"custom-tools": custom_server},  # カスタム MCP サーバーを追加
            permission_mode="acceptEdits",
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


if __name__ == "__main__":
    asyncio.run(main())
