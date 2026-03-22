"""エージェントメッセージ表示ユーティリティ"""

from claude_agent_sdk import (
    AssistantMessage,
    ResultMessage,
    SystemMessage,
    TextBlock,
    ToolUseBlock,
)


def display_agent_message(message: AssistantMessage | ResultMessage | SystemMessage) -> None:
    """
    エージェントからのメッセージをフォーマットして表示する。

    Args:
        message: 表示するメッセージオブジェクト
    """
    # システムメッセージ（MCP サーバー接続状態）
    if isinstance(message, SystemMessage) and message.subtype == "init":
        mcp_servers = message.data.get("mcp_servers", [])
        print("MCP サーバー接続状態:")
        for server in mcp_servers:
            status = server.get("status", "unknown")
            name = server.get("name", "unknown")
            print(f"  - {name}: {status}")
        print()
        return

    # アシスタントメッセージ
    if isinstance(message, AssistantMessage):
        for block in message.content:
            if isinstance(block, TextBlock):
                text = block.text
                if text.strip():
                    lines = text.split('\n')
                    for line in lines:
                        if len(line) > 80:
                            # 長い行は適度に折り返し
                            for i in range(0, len(line), 80):
                                print(line[i:i+80])
                        else:
                            print(line)
            elif isinstance(block, ToolUseBlock):
                tool_name = block.name
                print(f"\n🔧 ツール使用：{tool_name}")

                # ツール固有の情報表示
                if hasattr(block, "input") and block.input:
                    if tool_name.startswith("mcp__brave-search__"):
                        query_text = block.input.get("query", "")
                        if query_text:
                            print(f"   検索クエリ：{query_text[:50]}...")
                    elif tool_name == "Write":
                        file_path = block.input.get("file_path", "")
                        if file_path:
                            print(f"   書き込みファイル：{file_path}")
        return

    # 完了メッセージ
    if isinstance(message, ResultMessage):
        print(f"\n✅ 完了：{message.subtype}")
