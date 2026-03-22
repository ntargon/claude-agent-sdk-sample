"""
Interactive Agent - ClaudeSDKClient サンプル

このサンプルは、ClaudeSDKClient を使用した双方向の対話型インターフェースを実装します。
query() 関数との違いは、セッション状態が維持され、複数のメッセージをやり取りできる点です。

実行方法:
    uv run interactive_agent.py

機能:
    - 対話型ターミナルインターフェース
    - セッション状態の維持（複数ターンの会話）
    - カスタム MCP ツール（天気、計算機、通貨変換）
    - 特殊コマンド：/exit, /interrupt, /new
"""

import asyncio
from typing import Any

from utils import load_project_env, display
from claude_agent_sdk import (
    ClaudeSDKClient,
    ClaudeAgentOptions,
    AssistantMessage,
    ResultMessage,
    TextBlock,
    ToolUseBlock,
    tool,
    create_sdk_mcp_server,
)

load_project_env()


# =============================================================================
# カスタムツールの定義
# =============================================================================

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

    # モックの天気データ
    weather_conditions = ["晴れ", "曇り", "雨", "雷雨", "雪"]
    temperatures = {
        "Tokyo": 25,
        "New York": 22,
        "London": 18,
        "Paris": 20,
        "Sydney": 28,
        "Singapore": 30,
        "Seoul": 19,
        "Beijing": 23,
    }

    import random
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
                    "text": f"Error: サポートしていない通貨 - {from_currency} or {to_currency}"
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


# =============================================================================
# メイン処理
# =============================================================================

async def main():
    print("=" * 70)
    print("Interactive Agent - ClaudeSDKClient サンプル")
    print("=" * 70)

    # カスタムツールを含む MCP サーバーを作成
    custom_server = create_sdk_mcp_server(
        name="interactive-tools",
        version="1.0.0",
        tools=[get_weather, calculate, convert_currency],
    )

    # クライアントオプションを設定
    options = ClaudeAgentOptions(
        allowed_tools=["Read", "Write", "Bash", "mcp__interactive-tools__*"],
        mcp_servers={"interactive-tools": custom_server},
        permission_mode="acceptEdits",
    )

    print("\n利用可能なカスタムツール:")
    print("  - get_weather: 天気情報を取得")
    print("  - calculate: 数値計算")
    print("  - convert_currency: 通貨変換")
    print("\n特殊コマンド:")
    print("  /exit      - 終了")
    print("  /interrupt - 実行中のタスクを中断")
    print("  /new       - 新しいセッションを開始（会話リセット）")
    print("\n" + "-" * 70)

    # ClaudeSDKClient でセッションを開始
    async with ClaudeSDKClient(options=options) as client:
        turn_count = 0

        while True:
            try:
                # ユーザー入力
                user_input = input(f"\n[Turn {turn_count + 1}] あなた：")

                # 特殊コマンドの処理
                cmd = user_input.strip().lower()

                if cmd == "/exit" or cmd == "/quit" or cmd == "q":
                    print("\nセッションを終了します...")
                    break

                elif cmd == "/interrupt":
                    print("\nタスクを中断しました")
                    await client.interrupt()
                    continue

                elif cmd == "/new":
                    print("\n--- 新しいセッションを開始します ---")
                    await client.disconnect()
                    await client.connect()
                    turn_count = 0
                    continue

                # 空入力はスキップ
                if not user_input.strip():
                    continue

                # メッセージを送信
                await client.query(user_input)

                # レスポンスをストリーミング表示
                print(f"[Turn {turn_count + 1}] Claude: ", end="", flush=True)

                async for message in client.receive_response():
                    if isinstance(message, AssistantMessage):
                        for block in message.content:
                            if isinstance(block, TextBlock):
                                print(block.text, end="", flush=True)
                            elif isinstance(block, ToolUseBlock):
                                print(f"\n  [ツール使用：{block.name}]", end="", flush=True)
                    elif isinstance(message, ResultMessage):
                        # 結果メッセージの表示
                        pass

                print()  # 改行
                turn_count += 1

            except KeyboardInterrupt:
                print("\n\nCtrl+C が押されました。/interrupt で中断するか、/exit で終了できます。")
                continue
            except Exception as e:
                print(f"\nエラーが発生しました：{e}")
                continue

    print("-" * 70)
    print(f"合計 {turn_count} ターンの対話を行いました")
    print("Interactive Agent セッション終了")


if __name__ == "__main__":
    asyncio.run(main())
