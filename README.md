### Spotify playlist downloader 📋 🎼

---

### Reason


Recently I found a [service](https://www.soundloaders.com/spotify-downloader/), which allows downloading songs from
Spotify, but does not allow downloading whole playlists. 
This program is aimed to fix this small detail.

### Usage

```
usage: main.py [-h] [-d DIR] [-t THREADS] playlist

Download playlists from spotify

positional arguments:
  playlist              URL to playlist. Example: https://open.spotify.com/pla
                        ylist/37i9dQZF1E8OSy3MPBx3OT

options:
  -h, --help            show this help message and exit
  -d DIR, --dir DIR     Path to store tracks
  -t THREADS, --threads THREADS
                        Amount of tracks to store at the same time. Please, be
                        careful with that option, high numbers may cause
                        problems on the service we use under the hood, do not
                        let it down
```


### Known problems

- [ ] Script does not recognize more, than 30 tracks in playlist.
Probably can be fixed by sending another http-request to Spotify
