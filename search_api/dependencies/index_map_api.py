from flask import current_app, g
from search_api import config
from search_api.exceptions import ApplicationError


def search_for_index_map(uprn):
    current_app.logger.info("Performing uprn title search")

    title_resp = g.requests.get('{}/v1/uprns/{}'.format(config.INDEX_MAP_API_URL, uprn),
                                timeout=config.INDEX_MAP_TIMEOUT,
                                headers={"Content-Type": "application/json", "Accept": "application/json"})
    if title_resp.status_code == 200:
        features = []
        for title in title_resp.json():
            current_app.logger.info("Performing index map search")
            index_map_resp = g.requests.get(
                '{}/v1/index_map/{}'.format(config.INDEX_MAP_API_URL, title),
                timeout=config.INDEX_MAP_TIMEOUT,
                headers={"Content-Type": "application/json", "Accept": "application/json"},
                params={"exclude_classes": "CN"})
            if index_map_resp.status_code == 200:
                index_map_json = index_map_resp.json()
                features = features + index_map_json['features']
            elif index_map_resp.status_code != 404:
                raise ApplicationError(index_map_resp.json(), 500, 500)
        if features:
            return {"type": "FeatureCollection",
                    "features": features}
    elif title_resp.status_code != 404:
        raise ApplicationError(title_resp.json(), 500, 500)


def search_for_index_map_by_title_no(title):
    current_app.logger.info("Performing index map search")
    index_map_resp = g.requests.get(
        '{}/v1/index_map/{}'.format(config.INDEX_MAP_API_URL, title),
        timeout=config.INDEX_MAP_TIMEOUT,
        headers={"Content-Type": "application/json", "Accept": "application/json"},
        params={"exclude_classes": "CN"})

    return index_map_resp
