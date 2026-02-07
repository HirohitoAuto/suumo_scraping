"""
geocodingユーティリティ

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

# Cacheファイルのパス
CACHE_FILE_PATH = os.path.join(
    os.path.dirname(__file__), "../../data/geocoding_api_history.json"
)


def _load_cache() -> Dict[str, Dict[str, float]]:
    """Cacheファイルから過去のgeocoding結果を読み込む

    Returns:
        Dict[str, Dict[str, float]]: Cacheデータ。キーはID、値は{"lat": ..., "lon": ...}の辞書
    """
    if not os.path.exists(CACHE_FILE_PATH):
        return {}

    try:
        with open(CACHE_FILE_PATH, "r", encoding="utf-8") as f:
            cache = json.load(f)

        # 読み込んだデータの型を検証する
        if not isinstance(cache, dict):
            logger.warning(
                "Cacheファイルの形式が不正です。dict を期待しましたが %s が見つかりました。空のキャッシュにリセットします。",
                type(cache),
            )
            cache = {}
            # 可能であれば不正なキャッシュを上書きして修正する
            _save_cache(cache)
            return cache

        # （任意）各エントリが期待される形であるかの簡易チェック
        valid_cache: Dict[str, Dict[str, float]] = {}
        for key, value in cache.items():
            if not isinstance(key, str):
                continue
            if not isinstance(value, dict):
                continue
            lat = value.get("lat")
            lon = value.get("lon")
            if not isinstance(lat, (int, float)) or not isinstance(lon, (int, float)):
                continue
            # 型が正しいものだけを残す
            valid_cache[key] = {"lat": float(lat), "lon": float(lon)}

        return valid_cache
    except json.JSONDecodeError as e:
        # JSON として読み取れない場合はキャッシュを無視する
        logger.warning(
            "Cacheファイル(%s)が壊れています。空のキャッシュを使用します。: %s",
            CACHE_FILE_PATH,
            e,
        )
        return {}
    except Exception as e:
        # 予期せぬエラーの場合もキャッシュなしで継続する
        logger.exception(
            "Cacheファイル(%s)の読み込みに失敗しました。空のキャッシュを使用します。: %s",
            CACHE_FILE_PATH,
            e,
        )
        return {}


def _save_cache(cache: Dict[str, Dict[str, float]]) -> None:
    """geocoding結果をCacheファイルに保存する

    Args:
        cache: 保存するCacheデータ
    """
    try:
        # ディレクトリが存在しない場合は作成
        os.makedirs(os.path.dirname(CACHE_FILE_PATH), exist_ok=True)

        with open(CACHE_FILE_PATH, "w", encoding="utf-8") as f:
            json.dump(cache, f, ensure_ascii=False, indent=4)
    except Exception:
        logger.error("Cacheファイルの保存に失敗しました")


def get_coordinates_from_address(
    address: str, api_key: str, property_id: Optional[str] = None
) -> Optional[Tuple[float, float]]:
    """住所文字列から緯度・経度を取得する

    Google Maps Geocoding APIを使用して、指定された住所の緯度・経度を取得します。
    property_idが指定されている場合は、Cacheを利用してAPI呼び出しを削減します。

    Args:
        address (str): geocoding対象の住所文字列
            例: "東京都渋谷区渋谷1-1-1"
        api_key (str): Google Maps Platform APIキー
        property_id (Optional[str]): 物件ID。指定された場合はCacheを利用します。

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
        - property_idが指定されている場合、過去の結果をCacheから取得します
        - 並行実行には対応していません。複数プロセスでの同時実行時はCacheの競合が発生する可能性があります
    """
    # 入力値の検証
    if not address or not address.strip():
        raise ValueError("住所文字列が空です")

    if not api_key or not api_key.strip():
        raise ValueError("APIキーが空です")

    # Cacheの読み込み
    cache = _load_cache()

    # property_idが指定されている場合、Cacheを確認
    if property_id and str(property_id) in cache:
        cached_data = cache[str(property_id)]
        try:
            latitude = float(cached_data["lat"])
            longitude = float(cached_data["lon"])
            return (latitude, longitude)  # Cacheから取得できたら終了

        except (KeyError, ValueError, TypeError) as e:
            logger.warning(f"Cacheデータが不正です: id={property_id}, error={e}")
            # Cacheが不正な場合は削除して保存
            del cache[str(property_id)]
            _save_cache(cache)

    # APIを呼び出す
    try:
        # Google Maps クライアントを初期化
        gmaps = googlemaps.Client(key=api_key)
        # geocodingを実行
        geocode_result = gmaps.geocode(address)
        # 結果が空の場合
        if not geocode_result:
            return None

        # 最初の結果から緯度・経度を取得
        try:
            location = geocode_result[0]["geometry"]["location"]
            latitude = location["lat"]
            longitude = location["lng"]
        except (KeyError, IndexError, TypeError) as e:
            logger.error(f"APIレスポンスの構造が不正です: {e}")
            return None

        # property_idが指定されている場合、結果をCacheに保存
        if property_id:
            cache[str(property_id)] = {"lat": latitude, "lon": longitude}
            _save_cache(cache)
            logger.info(f"Cacheに保存しました: id={property_id}")

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
