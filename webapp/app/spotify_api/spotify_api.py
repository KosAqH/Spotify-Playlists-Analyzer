import requests
import pandas as pd

class SpotifyApi:
    def __init__(self, access_token: str) -> None:
        """
        Constructor.

            Args:
                access_token (str) - access token to Spotify API
        """
        self._access_token = access_token
        self._headers = {'Authorization': 'Bearer {}'.format(access_token)}
        self._LONG_LIMIT = 100
        self._SHORT_LIMIT = 50
    
    def retrieveArtistMetadata(self, artist_ids: list[str]) -> dict:
        """
        Function is making the call to Spotify API. It requests metadata of all artists, that ids were passed
            as argument.

            Args:
                artist_ids (list[str]) - list containing artists ids

            Returns:
                d (dict) - list containing one dict for each artist. Each dict contains artist's name, id, genres,
                    and url of thumnbail.
        """
        r = requests.get(f"https://api.spotify.com/v1/artists?ids={','.join(artist_ids)}", headers=self._headers)
        
        l = []
        for artist in r.json()["artists"]:
            l.append({
                "name": artist["name"],
                "id": artist["id"],
                "url_photo": artist["images"][0]["url"],
                "genres": artist["genres"]
            })
            
        return l

    def retrieveAlbumMetadata(self, album_ids: list[str]) -> list[dict]:
        """
        Function is making the call to Spotify API. It requests metadata of all albums, that ids were passed
            as argument.

            Args:
                album_ids (list[str]) - list containing album ids

            Returns:
                d (dict) - list containing one dict for each album. Each dict contains album's name, id, artist name,
                    url of thumnbail and genres.
        """
        r = requests.get(f"https://api.spotify.com/v1/albums?ids={','.join(album_ids)}", headers=self._headers)
        l = []
        for album in r.json()["albums"]:
            l.append({
                "name": album["name"],
                "id": album["id"],
                "artist": album["artists"][0]["name"],
                "url_photo": album["images"][0]["url"],
                "genres": album["genres"]
            })
            
        return l

    def retrieveIdsFromPlaylist(self, playlist_id: str, total_count: int) -> list[str]:
        """
        Function requests Spotify API and gets ids of all tracks that were added to playlist. 

            Args:
                playlist_id (str) - id of playlist
                total_count (int) - count of tracks added to playlist 

            Returns:
                result (list[str]) - list containing ids of all songs added to playlist
        """
        offset = 0
        result = []

        while total_count > offset:          
            r = requests.get(f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks?limit={self._SHORT_LIMIT}&offset={offset}", headers=self._headers)
            for t in r.json()["items"]:
                try:
                    result.append(t["track"]["id"])
                except:
                    pass
            offset += 50 

        return result
    
    def retrieveSongsAudioFeatures(self, songs_ids: list) -> list[dict]:
        """
        Function requests Spotify API and gets audio features of all songs, that ids was passed as argument. 

            Args:
                songs_ids (list[str]) - list of songs ids

            Returns:
                audio_features (list[dict]) - list containing one dict for each track. Each dict contains
                    all retrieved values.
        """
        offset = 0
        audio_features = []
        while len(songs_ids) > offset:
            r = requests.get(
                f"https://api.spotify.com/v1/audio-features?ids={','.join(songs_ids[offset:self._LONG_LIMIT+offset])}", 
                headers=self._headers)
            offset += self._LONG_LIMIT
            audio_features += r.json()["audio_features"]
        
        return audio_features

    def retrieveSongsMetadata(self, songs_ids: list) -> list[dict]:
        """
        Function requests Spotify API and gets metadata of all songs, that ids was passed as argument. 

            Args:
                songs_ids (list[str]) - list of songs ids

            Returns:
                audio_metadata (list[dict]) - list containing one dict for each track. Each dict contains
                    all retrieved values and derived from them album_name, album_id, artist_name, artist_id 
                    and placeholder value for genre.
        """
        offset = 0
        audio_metadata = []
        while len(songs_ids) > offset:
            r = requests.get(
                f"https://api.spotify.com/v1/tracks?ids={','.join(songs_ids[offset:self._SHORT_LIMIT+offset])}", 
                headers=self._headers)
            offset += self._SHORT_LIMIT
            audio_metadata += r.json()["tracks"]
        
        for d in audio_metadata:
            d["album_name"] = d["album"]["name"]
            d["album_id"] = d["album"]["id"]
            d["genres"] = "unknown" # TO DO
            d["artist_name"] = d["artists"][0]["name"]
            d["artist_id"] = d["artists"][0]["id"]

        return audio_metadata
    
    def retrievePlaylistMetadata(self, id: str) -> dict:
        """
        Function is making the call to Spotify API. It requests playlist's metadata and returns
            dict with chosen values.

            Args:
                id (str) - id of playlist

            Returns:
                d (dict) - dictionary containing name, creator, url, url of thumnbail and count 
                    of songs in playlist
        """

        r = requests.get(f"https://api.spotify.com/v1/playlists/{id}", headers=self._headers)
        playlist = r.json()
        d = {
                "name": playlist['name'],
                "creator": playlist["owner"]["display_name"],
                "total_count": playlist["tracks"]["total"],
                "img_url": playlist["images"][0]["url"],
                "url": playlist["external_urls"]["spotify"]
            }
        
        return d