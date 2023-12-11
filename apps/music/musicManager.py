import yaml, os, threading, queue, time, random, json
import mutagen.easyid3 as id3
import mutagen, math
import pyray as pr
import requests

# was using it to keep track of when song was done but it for some reason made fps drop from 2000 to 20 :[ sub optimal so killed 😭😭
""" class Timer:
    def __init__(self):
        self.timerThread = None
        self.q = queue.Queue()

    def runTimer(self, duration, endFunction):
        startTime = time.time()
        paused = False
        while True:
            try:
                command = self.q.get_nowait()
                if command == 'stop':
                    break
                elif command == 'pause':
                    pauseTime = time.time()
                    paused = True
                elif command == 'resume':
                    startTime += time.time()-pauseTime
                    paused = False
            except queue.Empty:
                pass
            if not paused:
                runTime = time.time()-startTime
                if runTime >= duration:
                    endFunction()
                    break

    def start(self, duration, endFunction):
        # if self.timerThread is not None:
        #     self.q.put('stop')
        self.timerThread = threading.Thread(target=self.runTimer, args=(duration,endFunction))
        self.timerThread.start()

    def stop(self):
        self.q.put('stop')

    def pause(self):
        self.q.put('pause')

    def resume(self):
        self.q.put('resume') """

class SongObject:
    def __init__(self, file, title, album, artist, length):
        self.file = file
        self.title = title
        self.album = album
        self.artist = artist
        self.length = length
        

class MusicManager:
    def __init__(self, lastFmApiKey):
        self.queue = []
        self.history = []

        self.loop = False
        self.musicStream = None
        self.currentSongObject = None

        self.apiKey = lastFmApiKey

        pr.init_audio_device()

    def indexLibrarySongs(self):
        fileList = [f for f in os.listdir(self.libraryPath)
                    if os.path.isfile(self.libraryPath+f) and f != 'index.txt']

        self.libraryIndex = {'artists':{}, 'albums':{}, 'songs':{}}
        self.librarySongList = []

        for file in fileList:
            track = id3.EasyID3(self.libraryPath+file)
            album = track['album'][0]
            artist = track['artist'][0]
            title = track['title'][0]
            if artist not in self.libraryIndex['artists'].keys():
                self.libraryIndex['artists'][artist] = []
            if album not in self.libraryIndex['albums']:
                self.libraryIndex['albums'][album] = []

            self.libraryIndex['artists'][artist].append(title)
            self.libraryIndex['albums'][album].append(title)
            songObj = SongObject(file, title, album, artist, mutagen.File(self.libraryPath+file).info.length)
            self.libraryIndex['songs'][title] = songObj
            self.librarySongList.append(songObj)

        self.librarySize = len(self.librarySongList)

    def createPlaylistFile(self):
        with open(self.libraryPath+'index.txt', 'w') as file:
            pass

    def loadLibrary(self, path):
        self.libraryPath = path

        self.indexLibrarySongs()

        try:
            with open(path+'/index.txt', 'r') as file:
                self.playlists = yaml.safe_load(file)
        except FileNotFoundError:
            self.createPlaylistFile()

    def queuePlaylist(self, playlist, shufflePlaylist=False):
        self.queue = []
        playListOrder = self.playlists[playlist]
        if shufflePlaylist:
            random.shuffle(playListOrder)
        for song in playListOrder:
            self.addSongToQueue(self.libraryIndex['songs'][song])

    def clearQueues(self):
        self.queue = []
        self.history = []

    def playNextSongInQueue(self):
        try:
            song = self.queue.pop(0)
            self.playSong(song)
            self.history.append(song)
        except IndexError:
            if self.loop:
                self.queue = self.history
                self.history = []
                self.playNextSongInQueue()
            else:
                self.musicStream = None


    def addSongToQueue(self, song):
        self.queue.append(song)

    def addSongNext(self, song):
        self.queue.insert(0, song)

    def queueAndPlay(self, song):
        self.addSongNext(song)
        self.playNextSongInQueue()

    def playSong(self, song):
        #self.player = audioplayer.AudioPlayer(self.libraryPath+
        #                                      self.libraryIndex['songs'][song].file)
        
        #self.player.play()
        if self.musicStream is not None:
            pr.unload_music_stream(self.musicStream)
        self.musicStream = pr.load_music_stream(self.libraryPath+
                                              song.file)
        pr.play_music_stream(self.musicStream)
        #self.timer.start(song.length, self.songFinished)
        self.currentSongObject = song

    def songFinished(self):
        self.nextSong()

    def pause(self):
        #self.player.pause()
        pr.pause_music_stream(self.musicStream)

    def resume(self):
        #self.player.resume()
        pr.resume_music_stream(self.musicStream)

    def nextSong(self):
        #self.player.close()
        if self.musicStream is not None:
            pr.stop_music_stream(self.musicStream)
        self.playNextSongInQueue()

    def previousSong(self):
        if self.musicStream is not None:
            pr.stop_music_stream(self.musicStream)
            if len(self.history) > 1:
                self.addSongNext(self.history.pop(-1))
                self.playSong(self.history[-1])

    def stop(self):
        if self.musicStream is not None:
            pr.stop_music_stream(self.musicStream)
            pr.unload_music_stream(self.musicStream)
        pr.close_audio_device()
        self.musicStream = None

    def togglePlayPause(self):
        if self.musicStream is not None:
            if pr.is_music_stream_playing(self.musicStream):
                self.pause()
            else:
                self.resume()

    def updateStream(self):
        if self.musicStream is not None:
            pr.update_music_stream(self.musicStream)
            if (1-self.getProportionPlayed()) < 0.01: #because it is never exactly 1 :(
                #print('song done!! :)')
                self.songFinished()

    def getCurrentSongData(self):
        response = requests.get(
            'https://ws.audioscrobbler.com/2.0/?method=track.getInfo'
            f'&api_key={self.apiKey}&artist={self.currentSongObject.artist}&track={self.currentSongObject.title}&format=json')
        return json.loads(response.text)
    
    def getTimePlayed(self):
        if self.musicStream is not None:
            return pr.get_music_time_played(self.musicStream)
        else:
            return None
    
    def getFormatedTimePlayed(self):
        if self.musicStream is not None:
            timePlayed = pr.get_music_time_played(self.musicStream)
            minutes = math.floor(timePlayed/60)
            seconds =  math.floor(timePlayed - (minutes*60))
            secondsString = str(seconds)
            if len(secondsString) == 1:
                secondsString = '0'+secondsString
            return f'{minutes}:{secondsString}'
        else:
            return None
    
    def getProportionPlayed(self):
        if self.musicStream is not None:
            return pr.get_music_time_played(self.musicStream)/pr.get_music_time_length(self.musicStream)
        else:
            return None
    
    def setPlaybackVolume(self, volume):
        if self.musicStream is not None:
            pr.set_music_volume(self.musicStream, volume)
    
    def setPlaybackPan(self, pan):
        if self.musicStream is not None:
            pr.set_music_pan(self.musicStream, pan)

    def getSearchResults(self, search):
        results = []
        for song in self.librarySongList:
            if search.lower() in song.title.lower():
                results.append(song)
        
        return results

