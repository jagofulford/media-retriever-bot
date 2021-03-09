import media
import urllib
import json
import requests
import yaml
import os

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(ROOT_DIR, "config.yaml")
config = yaml.safe_load(open(CONFIG_PATH, encoding="utf8"))

mandatory_fields = ["tvdbId", "tvRageId", "title", "titleSlug", "images", "seasons"]

class RadarrRetriever(media.MediaRetriever):
    def searchForMedia(self, search_term: str):
        results = {}
        query_parameters = urllib.parse.urlencode({'apikey':config['radarr']['apikey'],'term':search_term })
        media_search_request = requests.get('http://192.168.1.112:7878/api/v3/movie/lookup?{query_parameters}'.format(query_parameters=query_parameters) )
        mediaResults = json.loads(media_search_request.text)
        for mR in mediaResults:
            result = media.result(
                mR.get("title"),
                mR.get("year"),
                mR.get("remotePoster"),
                mR.get("overview",''),
                mR.get("imdbId"),
                "Radarr")
            results['r'+str(result.id)] = result
        return results
    def addMedia(self, tvdbid: int):
        media_addition_post_data = json.dumps(RadarrRetriever.buildRequest(self, tvdbid))
        query_parameters = urllib.parse.urlencode({'apikey':config['radarr']['apikey'] })
        addition_request = requests.post('http://192.168.1.112:7878/api/movie?{query_parameters}'.format(query_parameters=query_parameters),data=media_addition_post_data )
        if addition_request.status_code == 201:
            return True
        else:
            return False
    def buildRequest(self, imdbid: int):
        query_parameters = urllib.parse.urlencode({'apikey':config['radarr']['apikey'],'imdbId':imdbid })
        movie_request = requests.get('http://192.168.1.112:7878/api/series/lookup?{query_parameters}'.format(query_parameters=query_parameters ) )
        movie_json = json.loads(movie_request.text)
        request_body = {
            "qualityProfileId": "1",
            "addOptions": {
                "ignoreEpisodesWithFiles": "true",
                "ignoreEpisodesWithoutFiles": "false",
                "searchForMissingEpisodes": "false",
            },
            "rootFolderPath": RadarrRetriever.getRootFolder(self),
            "seasonFolder": "true",
        }
        for movie in movie_json:
            for key, value in movie.items():
                if key in mandatory_fields:
                    request_body[key] = value
        return request_body
    def getRootFolder(self) -> str:
        return 'D:\\TV\\'