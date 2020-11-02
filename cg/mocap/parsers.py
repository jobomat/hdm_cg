import struct
import os
from cg.mocap.models import OpticalMocapTake


def csmParser(filepath):
    take = OpticalMocapTake()

    if not filepath:
        print("No CSM-File specified. Returned take will be empty.")
        return take

    with open(filepath) as f:
        lineArray = f.readlines()

    lineArray = [line.rstrip() for line in lineArray]
    orderIndex = lineArray.index("$Order")
    pointsIndex = lineArray.index("$Points")

    # metadata
    for line in lineArray[:orderIndex]:
        metaline = line.split()
        if not metaline:
            continue
        if metaline[0] == "$Filename":
            take.takename = metaline[1][:metaline[1].index(".")]
            continue
        if metaline[0] == "$Actor":
            take.actor = metaline[1]
            continue
        if metaline[0] == "$Rate":
            take.rate = float(metaline[1])
            continue

    # markerdata
    markers = lineArray[orderIndex + 1:orderIndex + 2][0].split()
    take.segments = {mkr: [[], [], []] for mkr in markers}
    frames = [p.split()[1:] for p in lineArray[pointsIndex + 1:]]

    for progress, frame in enumerate(frames):
        for i, coord in enumerate([float(c) for c in frame]):
            take.segments[markers[i / 3]][i % 3].append(coord)

    take.length = len(take.segments[take.segments.keys()[0]][0])
    return take


def c3dParser(filepath):
    take = OpticalMocapTake()

    if not filepath:
        print("No C3D-File specified. Returned take will be empty.")
        return take

    take.takename = os.path.basename(filepath)[:-4]    

    with open(filepath, "rb") as c3d:
        headerString = 'b b H H H H H f i f i b b b b'
        size = struct.calcsize(headerString)
        header = struct.unpack(headerString, c3d.read(size))

        if header[1] != 80:
            print("Not a valid C3D file.")
            return take

        take.markerCount = header[2]
        take.rate = header[9]
        startOfDataBlock = (header[8] - 1) * 512

        parameterDict = {}
        groupIdNameMap = {}
        c3d.seek(516)
        bytesToNextGroup = 0

        typeDict = {-1: "s", 1: "B", 2: "H", 4: "f"}

        while True:
            value = None
            nameLength, groupId = struct.unpack("Bb", c3d.read(2))
            groupName = struct.unpack("{}s".format(nameLength), c3d.read(nameLength))[0]
            currentFilePos = c3d.tell()
            bytesToNextGroup = struct.unpack("H", c3d.read(2))[0]
            if bytesToNextGroup == 0:
                break
            dataInfo = struct.unpack("bB", c3d.read(2))
            # i assume c3d parameter data is restricted to two levels(?). therefore:
            # groupId < 0 -> Toplevel; groupId == abs(existing groupId) -> child
            if groupId < 0:  # it's a group
                groupIdNameMap[abs(groupId)] = groupName
                parameterDict[groupName] = {}
            else:  # it's a value
                if dataInfo[0] == -1:  # type: string or array of strings
                    stringSize = struct.unpack("B", c3d.read(1))[0]
                    if dataInfo[1] > 1:  # type: array of strings
                        value = []
                        arraySize = struct.unpack("B", c3d.read(1))[0]
                        for _ in range(arraySize):
                            value.append(
                                struct.unpack(
                                    "{}s".format(stringSize), c3d.read(stringSize)
                                )[0].strip()
                            )
                    else:  # type: string
                        value = struct.unpack(
                            "{}s".format(stringSize), c3d.read(stringSize)
                        )[0].strip()
                elif dataInfo[1] == 0:  # type: a single value
                    length = (dataInfo[0] if dataInfo[0] != -1
                              else struct.unpack("B", c3d.read(1))[0])
                    value = struct.unpack(typeDict[dataInfo[0]], c3d.read(length))[0]
                else:
                    value = []
                    for _ in range(dataInfo[1]):
                        length = (dataInfo[0] if dataInfo[0] != -1
                                  else struct.unpack("B", c3d.read(1))[0])
                        value.append(struct.unpack(typeDict[dataInfo[0]], c3d.read(length))[0])
                parameterDict[groupIdNameMap[groupId]][groupName] = value
            c3d.seek(currentFilePos + bytesToNextGroup)

        take.actor = parameterDict.get("SUBJECTS", {}).get("NAMES", [''])[0]
        take.length = parameterDict["POINT"]["FRAMES"]

        makerCoords = "f f f i"
        size = struct.calcsize(makerCoords)
        c3d.seek(startOfDataBlock)
        parameterDict["POINT"]["LABELS"] = [mkr.replace("*", "UNLABELED") for mkr in parameterDict["POINT"]["LABELS"]]
        markers = [mkr.split(":")[-1] for mkr in parameterDict["POINT"]["LABELS"]]
        take.segments = {mkr: [[], [], []] for mkr in markers}
        mkrCounter = 0

        for i in range(header[5] * parameterDict["POINT"]["USED"]):
            coords = struct.unpack(makerCoords, c3d.read(size))
            take.segments[markers[mkrCounter]][0].append(coords[0])
            take.segments[markers[mkrCounter]][1].append(coords[1])
            take.segments[markers[mkrCounter]][2].append(coords[2])
            mkrCounter += 1
            if mkrCounter == parameterDict["POINT"]["USED"]:
                mkrCounter = 0

        return take
