"""
ジオコーディングユーティリティ

住所文字列から緯度・経度を取得するための機能を提供します。
Google Maps Platform の Geocoding API を使用します。
"""

import json
import os
from typing import Dict, Optional, Tuple

import googlemaps
from googlemaps.exceptions import ApiError, Timeout, TransportError

from .logger import get_logger

logger = get_logger(__name__)

# キャッシュファイルのパス
CACHE_FILE_PATH = os.path.join(
    os.path.dirname(__file__), "../../data/geocoding_api_history.json"
)


def _load_cache() -> Dict[str, Dict[str, str]]:
    """キャッシュファイルから過去のジオコーディング結果を読み込む
    
    Returns:
        Dict[str, Dict[str, str]]: キャッシュデータ。キーはID、値は{"lat": ..., "lon": ...}の辞書
    """
    if not os.path.exists(CACHE_FILE_PATH):
        logger.info(f"キャッシュファイルが存在しません: {CACHE_FILE_PATH}")
        return {}
    
    try:
        with open(CACHE_FILE_PATH, "r", encoding="utf-8") as f:
            cache = json.load(f)
            logger.info(f"キャッシュファイルを読み込みました: {len(cache)}件")
            return cache
    except json.JSONDecodeError as e:
        logger.error(f"キャッシュファイルの読み込みに失敗しました: {e}")
        return {}
    except Exception as e:
        logger.error(f"キャッシュファイルの読み込み中にエラーが発生しました: {e}")
        return {}


def _save_cache(cache: Dict[str, Dict[str, str]]) -> None:
    """ジオコーディング結果をキャッシュファイルに保存する
    
    Args:
        cache: 保存するキャッシュデータ
    """
    try:
        # ディレクトリが存在しない場合は作成
        os.makedirs(os.path.dirname(CACHE_FILE_PATH), exist_ok=True)
        
        with open(CACHE_FILE_PATH, "w", encoding="utf-8") as f:
            json.dump(cache, f, ensure_ascii=False, indent=4)
            logger.info(f"キャッシュファイルを保存しました: {len(cache)}件")
    except Exception as e:
        logger.error(f"キャッシュファイルの保存中にエラーが発生しました: {e}")


def get_coordinates_from_address(
    address: str, api_key: str, property_id: Optional[str] = None
) -> Optional[Tuple[float, float]]:
    """住所文字列から緯度・経度を取得する

    Google Maps Geocoding APIを使用して、指定された住所の緯度・経度を取得します。
    property_idが指定されている場合は、キャッシュを利用してAPI呼び出しを削減します。

    Args:
        address (str): ジオコーディング対象の住所文字列
            例: "東京都渋谷区渋谷1-1-1"
        api_key (str): Google Maps Platform APIキー
        property_id (Optional[str]): 物件ID。指定された場合はキャッシュを利用します。

    Returns:
        Optional[Tuple[float, float]]: 取得に成功した場合は(緯度, 経度)のタプル、
            失敗した場合はNoneを返します。

    Raises:
        ValueError: 住所文字列またはAPIキーが空の場合

    Example:
        >>> api_key = "your_google_maps_api_key"
        >>> coordinates = get_coordinates_from_address("東京都渋谷区渋谷1-1-1", api_key, "20001055")
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
        - property_idが指定されている場合、過去の結果をキャッシュから取得します
    """
    # 入力値の検証
    if not address or not address.strip():
        raise ValueError("住所文字列が空です")

    if not api_key or not api_key.strip():
        raise ValueError("APIキーが空です")

    # キャッシュの読み込み
    cache = _load_cache()
    
    # property_idが指定されている場合、キャッシュを確認
    if property_id and str(property_id) in cache:
        cached_data = cache[str(property_id)]
        try:
            latitude = float(cached_data["lat"])
            longitude = float(cached_data["lon"])
            logger.info(f"キャッシュから座標を取得: id={property_id}, 緯度={latitude}, 経度={longitude}")
            return (latitude, longitude)
        except (KeyError, ValueError, TypeError) as e:
            logger.warning(f"キャッシュデータが不正です: id={property_id}, error={e}")
            # キャッシュが不正な場合は削除して保存
            del cache[str(property_id)]
            _save_cache(cache)
            # APIを呼び出す

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
        
        # property_idが指定されている場合、結果をキャッシュに保存
        if property_id:
            cache[str(property_id)] = {
                "lat": latitude,
                "lon": longitude
            }
            _save_cache(cache)
            logger.info(f"キャッシュに保存しました: id={property_id}")
        
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
        logger.exception(f"予期しないエラーが発生しました: {e}")
        return None
