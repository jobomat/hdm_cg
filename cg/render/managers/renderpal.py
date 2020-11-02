import os
from os.path import dirname, normpath, join
import json
from collections import OrderedDict
from subprocess import Popen, PIPE, STDOUT


RP_CMD = join(os.environ["RP_CMDRC_DIR"], "RpRcCmd")
RP_RENDERERS_JSON = join(normpath(dirname(__file__)), "renderpal_renderers.json")
RP_POOLS_JSON = join(normpath(dirname(__file__)), "renderpal_pools.json")


def listrenderers():
    """
    Gets "cached" rendererlist from RP_RENDERERS_JSON. [fast]
    If RP_RENDERERS_JSON is non existent calls RenderPal via listrenderers(). [slow]
    """
    if os.path.exists(RP_RENDERERS_JSON) and os.path.isfile(RP_RENDERERS_JSON):
        with open(RP_RENDERERS_JSON) as renderer_json:
            r_dict = json.load(renderer_json, object_pairs_hook=OrderedDict)
        return r_dict
    return listrenderers_cmd()


def listpools():
    """
    Gets "cached" pool list from RP_POOLS_JSON. [fast]
    If RP_POOLS_JSON is non existent calls RenderPal via listrenderers(). [slow]
    """
    if os.path.exists(RP_POOLS_JSON) and os.path.isfile(RP_POOLS_JSON):
        with open(RP_POOLS_JSON) as pools_json:
            pools = json.load(pools_json)
        return pools
    return listpools_cmd()


def listrenderers_cmd():
    rp_return = cmd("-listrenderers")
    plain_list = [
        v.replace(" *", "")
        for v in rp_return.split("\r\n")[7:-4]
    ]

    r_dict = OrderedDict()

    for line in plain_list:
        software, rendererstring = line.split(": ")
        renderer, version = rendererstring.split("/")

        if not r_dict.get(software, None):
            r_dict[software] = {}
        if not r_dict[software].get(renderer, None):
            r_dict[software][renderer] = []

        r_dict[software][renderer].append(version)

    with open(RP_RENDERERS_JSON, "w") as renderers_json:
        json.dump(r_dict, renderers_json)

    return r_dict


def listpools_cmd():
    rp_return = cmd("-listpools")
    pools = rp_return.split("\r\n")[7:-2]

    with open(RP_POOLS_JSON, "w") as pools_json:
        json.dump(pools, pools_json)

    return pools


def cmd(flags):
    """
    Interacts with renderpal-server via RpRcCmd.exe and returns plain text result.
    Parameter "flags" can be given as:
        - string (e.g. '-listparams "Arnold Renderer/2020_ca"')
        - dict   (e.g. {"nj_renderer": "Arnold Renderer/2020_ca", "frames": "1-100"})

    :param node: flags
    :type flags: dict or str

    :returns: The raw output of the cmd.
    :rtype: str
    :raises: None
    """
    if isinstance(flags, dict):
        flags = " ".join(["-{} {}".format(k, v) for k, v in flags.items()])

    cmd = '"{}" {}'.format(RP_CMD, flags)

    p = Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT)
    output = p.stdout.read()
    return output
