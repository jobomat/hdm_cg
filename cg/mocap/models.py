# coding: utf-8


class OpticalMocapTake:
    """
    Class for holding point-based mocap data.
    segments is a dict of optical segment names as keys
    containing a list of three lists for x, y and z coordinates.
    segments["LFHD"][0] --> all x-coords of LFHD
    """

    def __init__(self):
        self.filepath = ""
        self.takename = ""
        self.rate = None
        self.actor = ""
        self.firstFrame = 0
        self.lastFrame = 0
        self.comments = ""
        self.segments = {}
        self.markerCount = 0
