class Rhythm:
    def __init__(self, bpm, length, track : list[tuple], music_path, delay):
        self.bpm = bpm #beats per minute
        self.length = length #how many number of beats long it is
        self.track = track.copy()
        self.original_track = track
        self.music_path = music_path
        self.delay = delay
        self.reset()

    def reset(self):
        self.track = self.original_track.copy()

