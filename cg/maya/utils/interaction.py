import pymel.core as pc


def get_selected_channelbox_attributes():
    """Returns the user-selected attributes in the maya main channelbox."""
    return pc.Mel.eval("selectedChannelBoxAttributes();")
