"""
ジオコーディングユーティリティ

住所文字列から緯度・経度を取得するための機能を提供します。
Google Maps Platform の Geocoding API を使用します。
"""

from typing import Optional, Tuple

import googlemaps
from googlemaps.exceptions import ApiError, Timeout, TransportError

from .logger import get_logger

logger = get_logger(__name__)


def get_coordinates_from_address(
    address: str, api_key: str
) -> Optional[Tuple[float, float]]:
    """住所文字列から緯度・経度を取得する

    Google Maps Geocoding APIを使用して、指定された住所の緯度・経度を取得します。

    Args:
        address (str): ジオコーディング対象の住所文字列
            例: "東京都渋谷区渋谷1-1-1"
        api_key (str): Google Maps Platform APIキー

    Returns:
        Optional[Tuple[float, float]]: 取得に成功した場合は(緯度, 経度)のタプル、
            失敗した場合はNoneを返します。

    Raises:
        ValueError: 住所文字列またはAPIキーが空の場合

    Example:
        >>> api_key = "your_google_maps_api_key"
        >>> coordinates = get_coordinates_from_address("東京都渋谷区渋谷1-1-1", api_key)
        >>> if coordinates:
        ...     latitude, longitude = coordinates
        ...     print(f"緯度: {latitude}, 経度: {longitude}")
        ... else:
        ...     print("座標の取得に失敗しました")

    Note:
        - Google Maps Platform の Geocoding API を使用するため、APIキーが必要です
        - API使用には料金が発生する可能性があります
        - レート制限やクォータ制限がある場合があります
        - ネットワークエラーやAPIエラーが発生した場合はNoneを返します
    """
    # 入力値の検証
    if not address or not address.strip():
        raise ValueError("住所文字列が空です")

    if not api_key or not api_key.strip():
        raise ValueError("APIキーが空です")

    try:
        # Google Maps クライアントを初期化
        gmaps = googlemaps.Client(key=api_key)

        # ジオコーディングを実行
        logger.info(f"住所のジオコーディングを実行: {address}")
        geocode_result = gmaps.geocode(address)

        # 結果が空の場合
        if not geocode_result:
            logger.warning(f"住所が見つかりませんでした: {address}")
            return None

        # 最初の結果から緯度・経度を取得
        try:
            location = geocode_result[0]["geometry"]["location"]
            latitude = location["lat"]
            longitude = location["lng"]
        except (KeyError, IndexError, TypeError) as e:
            logger.error(f"APIレスポンスの構造が不正です: {e}")
            return None

        logger.info(f"座標取得成功: 緯度={latitude}, 経度={longitude}")
        return (latitude, longitude)

    except ApiError as e:
        logger.error(f"Google Maps API エラー: {e}")
        return None
    except Timeout as e:
        logger.error(f"タイムアウトエラー: {e}")
        return None
    except TransportError as e:
        logger.error(f"通信エラー: {e}")
        return None
    except Exception as e:
        logger.error(f"予期しないエラーが発生しました: {e}")
        return None
