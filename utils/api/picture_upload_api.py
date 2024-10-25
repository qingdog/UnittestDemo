import logging

import requests
import json

from requests import Response


def upload(file_path, authorization, upload_url="https://sm.ms/api/v2/upload", files_key="file"):
    headers = {'Authorization': f'{authorization}'}
    with open(file_path, 'rb') as f:
        files = {files_key: f}
    # url = 'https://smms.app/api/v2/upload'
    session = requests.Session()
    res = session.request(method='POST', url=upload_url, headers=headers, files=files)
    session.close()
    return res


def get_sm_ms_url(res: Response):
    """获取上传sm.ms图床返回的url"""
    url = None
    try:
        if res.status_code == 200:
            url = json.dumps(res.json(), indent=4)
        else:
            logging.error(res, exc_info=True)
    except Exception:
        logging.error(res, exc_info=True)
    return url


if __name__ == "__main__":
    img_url = get_sm_ms_url(upload('anime.png', "cMZkqPKLXfroLwwGBqpYtunwkKm6BvUp", files_key="smfile"))
    print(img_url)
