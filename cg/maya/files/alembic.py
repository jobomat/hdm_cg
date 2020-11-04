import pymel.core as pc


def abc_export(root, file, frameRanges=[{"start": 1, "end": 1}], attrs=[], 
                   attrPrefixes=["ai"], dataFormat="ogawa", 
                   flags=["uvWrite","writeColorSets","writeFaceSets","writeUVSets"]):
    """
    flags=[
         "noNormals","ro","stripNamespaces","uvWrite","writeColorSets",
         "writeFaceSets","wholeFrameGeo","worldSpace","writeVisibility",
         "eulerFilter","autoSubd","writeUVSets"
    ]
    frameranges=[
        {"start": 1, "end": 1},
        {"start": -10, "end": 0, "step": 1, "preRoll": True, "frameRelativeSamples":[]}
        {"start": 10, "end": 20, "step": 0.5, "frameRelativeSamples":[-0.2,0,0.2]}
    ]
    """
    fr_list = []
    for fr in frameRanges:
        fr_list.extend([
            " -frameRange", " {}".format(fr["start"]), " {}".format(fr["end"]),
            "{}".format(" -step {}".format(fr["step"]) if fr.get("step", False) else ""),
            " -preRoll" if fr.get("preRoll") else ""   
        ])
        fr_list.extend([
            " -frameRelativeSample {}".format(frs) for frs in fr.get("frameRelativeSamples", [])
        ])
        frameRange_str = "".join(fr_list)

    attr_str = ""
    if attrs:
        attr_str = " -attr {}".format(" -attr ".join(attrs))

    attrPrefix_str = ""
    if attrPrefixes:
        attrPrefix_str = " -attrPrefix {}".format(" -attrPrefix ".join(attrPrefixes))

    mel = "".join([
        "AbcExport -j \"",
        frameRange_str,
        " -" if flags else "",
        " -".join(flags),
        attr_str,
        attrPrefix_str,
        " -dataFormat ", dataFormat,
        " -root ", root,
        " -file ", file, "\""
    ])
    print(mel)
    pc.mel.eval(mel)


def abc_merge(root, file):
    pc.mel.eval('AbcImport -mode import -connect "{}" "{}";'.format(root, file))


def abc_import(file):
    pc.mel.eval('AbcImport -mode import "{}";'.format(file))