"""
Web Researcher Agent - Claude Agent SDK サンプル

このサンプルは、Brave Search MCP を使用して Web 検索による情報収集を行い、
レポートを生成するエージェントを実装します。

実行方法:
    uv run web_researcher.py

機能:
    - Brave Search MCP による Web 検索
    - 収集した情報の整理
    - レポートの生成と保存

前提条件:
    .env ファイルに BRAVE_API_KEY を設定してください。
"""

import asyncio
import os
from pathlib import Path

from utils import load_project_env, display_agent_message
from claude_agent_sdk import (
    query,
    ClaudeAgentOptions,
    AssistantMessage,
    ResultMessage,
    SystemMessage,
    TextBlock,
    ToolUseBlock,
)

load_project_env()


async def main():
    print("=" * 60)
    print("Web Research Agent - Claude Agent SDK サンプル")
    print("=" * 60)

    # 検索テーマ
    research_topic = "2026 年の最新の AI 技術動向"

    print(f"\n🔍 検索テーマ：{research_topic}")
    print("\nエージェントが Brave Search を使用して情報を収集します...\n")

    # エージェントの実行
    async for message in query(
        prompt=f"""
以下のテーマについて Web 検索を使用して調査し、詳細なレポートを作成してください：

テーマ：{research_topic}

実施すること：
1. Web 検索を使用して関連情報を収集
2. 重要な発見を整理
3. Markdown 形式で構造化されたレポートを作成
4. レポートを research_report.md として保存

レポートの構成：
- タイトル
- 概要（要約）
- 主要なトピック（3-5 個）
- 各トピックの詳細
- 結論
- 参考文献（あれば）
""",
        options=ClaudeAgentOptions(
            mcp_servers={
                "brave-search": {
                    "command": "npx",
                    "args": ["-y", "@modelcontextprotocol/server-brave-search"],
                    "env": {"BRAVE_API_KEY": os.environ.get("BRAVE_API_KEY", "")},
                }
            },
            allowed_tools=["mcp__brave-search__*", "Read", "Write", "Bash"],
            permission_mode="acceptEdits",
        ),
    ):
        display_agent_message(message)

    # レポートファイルの確認
    report_file = Path(__file__).parent / "research_report.md"
    if report_file.exists():
        print("\n" + "=" * 60)
        print("生成されたレポート:")
        print("=" * 60)
        print(report_file.read_text()[:2000])  # 最初の 2000 文字のみ表示
        print("\n...（続きは research_report.md を参照）")
    else:
        print("\n⚠️ レポートファイルが生成されませんでした")


if __name__ == "__main__":
    asyncio.run(main())
