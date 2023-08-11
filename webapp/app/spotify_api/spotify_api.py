import requests

class SpotifyApi:
    def __init__(self, access_token):
        self._access_token = access_token
        self._headers = {'Authorization': 'Bearer {}'.format(access_token)}

    def GetPlaylistInfo(self, id: str) -> dict:
        r = requests.get(f"https://api.spotify.com/v1/playlists/{id}", headers=self._headers)
        return r.json()
    
    def GetTracksMetadata(self, ids: list) -> list:
        ids = ','.join(ids)
        r = requests.get(f"https://api.spotify.com/v1/tracks?ids={ids}", headers=self._headers)

        tracks = r.json()['tracks']
        l = []
        for t in tracks:
            d = {
                "title": t["name"],
                "artist": t['artists'][0]['name'],
                "album": t['album']['name'],
                "img": t['album']['images'][0]["url"]
            }
            l.append(d)

        return l
    
    def RetrievePlaylistMetadata(self, playlist: dict) -> dict:

        d = {
                "name": playlist['name'],
                "creator": playlist["owner"]["display_name"],
                "total_count": playlist["tracks"]["total"],
                "total_duration": 0,
                "img_url": playlist["images"][0]["url"]
            }
        
        return d
    
    def GetPlaylistsSongsIds(self, dict) -> None:
        pass

    def GetPlaylistsSongsStats():
        pass