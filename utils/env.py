"""環境変数読み込みユーティリティ"""

from pathlib import Path
from dotenv import load_dotenv


def load_project_env() -> None:
    """
    プロジェクトルートの .env ファイルから環境変数を読み込む。

    呼び出し元のファイル位置から自動的に .env ファイルを解決する。
    """
    env_path = Path(__file__).parent.parent / ".env"
    load_dotenv(env_path)
