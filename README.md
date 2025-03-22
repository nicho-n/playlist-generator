<h1>Overview</h1>
This is a cloud-deployed "ai agent" that listens to the radio 24/7 and builds spotify playlists.

Running the `spotify_headless` will ping some "Now Playing" radio API endpoints, collecting the songs to a file.

This app is deployed on GCP. `cloud_startup_script.sh` is fed to a GCP instance at startup which initializes everything.

For local use, CLIENT_ID, SECRET_ID, and SPOTIFY_REFRESH token need to be populated with your own Spotify developer credentials. 

<a href="https://open.spotify.com/playlist/3Oof1Q9vwZpJrj0L9ohkOc">Listen to the Playlist!</a>
<p align="center">
  <img src="example.png" alt="A continuously generated Spotify playlist from FluxFM Sound of Berlin" width="225px" />
</p>
