from typing import Any, Union
import urllib.request
import urllib.error
import pathlib
import warnings
import os
import time
import json


def download(url, save_path, sleep=1):
    """
    urlからダウンロードする。save_pathが存在するなら何もしない。
    Args:
        url (str): url
        save_path (str): save path
        sleep (int): 待機時間(秒)
    Returns:
        int: 成功なら1,urlがnotfoundまたはファイルが既に存在するなら0
    """
    save_path = pathlib.Path(save_path)
    if save_path.exists():
        return 0
    time.sleep(sleep)
    os.makedirs(save_path.parent, exist_ok=True)
    req = urllib.request.Request(url)
    try:
        with urllib.request.urlopen(req) as res:
            save_path.write_bytes(res.read())
        return 1
    except urllib.error.HTTPError as e:
        warnings.warn(f"{e.code}: {e.reason}")
        warnings.warn(f"url: {url}")
        return 0


def json_write(obj: Union[dict, list], file_path: str, overwrite: bool = False) -> int:
    """dictをjsonファイルに書き込む

    Args:
        obj (Union[dict, list]): json化するオブジェクト
        file_path (str): ファイルパス
        overwrite (bool, optional): Trueで上書きを許す. Defaults to False.

    Returns:
        int: 成功なら1が返る

    Example:
        _.json_write({"a": 1}, "path/to/sample.json")
        _.json_write({"a": 1}, "path/to/sample.json", overwrite=True)
    """
    file_path = pathlib.Path(file_path)
    if not overwrite and file_path.exists():
        return 0
    os.makedirs(file_path.parent, exist_ok=True)
    file_path.write_text(json.dumps(obj))
    return 1


def json_read(file_path: str) -> Any:
    """jsonファイルを読み込んでdict化する

    Args:
        file_path (str): ファイルパス

    Returns:
        Any: dictもしくはlist

    Example:
        _.json_read("path/to/sample.json")
    """
    file_path = pathlib.Path(file_path)
    return json.loads(file_path.read_text())


def cat(file_path: str) -> str:
    """pathlib.Path().read_textのshortcut

    Args:
        file_path (str): filepath

    Returns:
        str: file内の文字列

    Example:
        >>> cat('unknown.txt')

    """
    file_path = pathlib.Path(file_path)
    if file_path.is_file():
        return file_path.read_text()
    return None
