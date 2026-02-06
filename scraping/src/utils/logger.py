"""
カスタムロガーユーティリティ

開発やログの確認のための一般的なロガーを提供します。
"""

import logging
import sys
from pathlib import Path
from typing import Optional


def get_logger(
    name: str,
    level: int = logging.INFO,
    log_dir: Optional[str] = None,
    log_to_file: bool = False,
) -> logging.Logger:
    """
    カスタムロガーを取得する

    Args:
        name (str): ロガー名（通常は __name__ を指定）
        level (int): ログレベル（デフォルト: logging.INFO）
        log_dir (Optional[str]): ログファイルの保存先ディレクトリ（log_to_file=Trueの場合に使用）
        log_to_file (bool): ファイル出力を有効にするか（デフォルト: False）

    Returns:
        logging.Logger: 設定済みのロガーインスタンス

    Example:
        >>> logger = get_logger(__name__)
        >>> logger.info("処理を開始しました")
        >>> logger.warning("警告メッセージ")
        >>> logger.error("エラーが発生しました")
    """
    # ロガーを取得
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # 既にハンドラが設定されている場合はそのまま返す（重複防止）
    if logger.handlers:
        return logger

    # フォーマッタを作成
    formatter = logging.Formatter(
        fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # コンソールハンドラを追加
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # ファイルハンドラを追加（オプション）
    if log_to_file:
        if log_dir is None:
            log_dir = "logs"

        # ログディレクトリを作成
        log_path = Path(log_dir)
        log_path.mkdir(parents=True, exist_ok=True)

        # ログファイルのパス（ロガー名をファイル名として使用）
        log_file = log_path / f"{name.replace('.', '_')}.log"

        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger


def setup_root_logger(level: int = logging.INFO) -> None:
    """
    ルートロガーをセットアップする

    アプリケーション全体のデフォルトログレベルを設定する場合に使用します。

    Args:
        level (int): ログレベル（デフォルト: logging.INFO）

    Example:
        >>> setup_root_logger(logging.DEBUG)
    """
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
