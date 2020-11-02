import pymel.core as pc


def toggle_port(port):
    port_str = ":{}".format(port)
    if port_str in pc.commandPort(q=True, listPorts=True):
        pc.commandPort(name=port_str, close=True)
        print("Port {} Closed.".format(port))
    else:
        pc.commandPort(name=port_str, sourceType="python")
        print("Port {} Opened.".format(port))


def toggle_sublime_port():
    toggle_port(7002)
