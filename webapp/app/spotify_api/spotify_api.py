import requests

class SpotifyApi:
    def __init__(self, access_token):
        self._access_token = access_token
        self._headers = {'Authorization': 'Bearer {}'.format(access_token)}
        self._LONG_LIMIT = 100
        self._SHORT_LIMIT = 50

    def GetPlaylistInfo(self, id: str) -> dict:
        #delete it later -?
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
    
    def RequestPlaylist(self, id: str) -> dict:
        r = requests.get(f"https://api.spotify.com/v1/playlists/{id}", headers=self._headers)
        return r.json()
    
    def requestSongsAudioFeatures(self, songs_ids: list) -> list[dict]:
        offset = 0
        json_response = {}
        while len(songs_ids) > offset:
            r = requests.get(
                f"https://api.spotify.com/v1/audio-features?ids={','.join(songs_ids[offset:self._LONG_LIMIT+offset])}", 
                headers=self._headers)
            offset += self._LONG_LIMIT
            json_response += r.json()
        
        return json_response

    # def requestSongsMetadata(self, songs_ids) -> list[dict]:
    #     if type(songs_ids) == str:
    #         return self.requestSongsMetadataByPlaylist(songs_ids)
    #     elif type(songs_ids) == list:
    #         return self.requestSongsMetadataByList(songs_ids)
    #     else:
    #         return False
        
    # def requestSongsMetadataByPlaylist(self, playlist_id: str) -> list[dict]:
    #     r = requests.get(f"https://api.spotify.com/v1/playlists/{id}", headers=self._headers)
    #     return r.json()

    def requestSongsMetadataByList(self, songs_ids: list) -> list[dict]:
        offset = 0
        audio_features = []
        while len(songs_ids) > offset:
            r = requests.get(
                f"https://api.spotify.com/v1/audio-features?ids={','.join(songs_ids[offset:self._SHORT_LIMIT+offset])}", 
                headers=self._headers)
            offset += self._SHORT_LIMIT
            audio_features += r.json()["audio_features"]
        
        return audio_features
    
    def retrieveIdsFromPlaylist(self, playlist: dict) -> list:
        track_ids = []
        for t in playlist["tracks"]["items"]:
            track_ids.append(t["track"]["id"])
        return track_ids
    
    def retrieveSongsAudioFeatures(self, songs_ids: list) -> list[dict]:
        offset = 0
        audio_features = []
        while len(songs_ids) > offset:
            r = requests.get(
                f"https://api.spotify.com/v1/audio-features?ids={','.join(songs_ids[offset:self._SHORT_LIMIT+offset])}", 
                headers=self._headers)
            offset += self._SHORT_LIMIT
            audio_features += r.json()["audio_features"]
        
        return audio_features

    def retrieveSongsMetadata(self, songs_ids: list) -> list[dict]:
        offset = 0
        audio_features = []
        while len(songs_ids) > offset:
            r = requests.get(
                f"https://api.spotify.com/v1/tracks?ids={','.join(songs_ids[offset:self._SHORT_LIMIT+offset])}", 
                headers=self._headers)
            offset += self._SHORT_LIMIT
            audio_features += r.json()["tracks"]
        
        return audio_features
    
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