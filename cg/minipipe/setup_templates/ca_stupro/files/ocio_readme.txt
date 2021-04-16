At HdM CA-Lab everything is set up and ready to go.

At home download the OCIO config (warning - big download ahead!):
https://github.com/colour-science/OpenColorIO-Configs/tree/feature/aces-1.1-config

Place the downloaded OCIO-folder outside your NextCloud-synced folder if you want to avoid syncing GigaBytes of stuff and annoying your group members.

Create a system environment variable named "OCIO" which points to your OCIO folder and your chosen version (e.g. "C:/ocio/aces_1.1/config.ocio"). 


--------------------------------------------
Maya

If  environment-var is set, Maya will find your config file on startup and activate aces_cg as your rendering-space. Easy!

You can also manually choose the config in the "Maya Preferences > Color Management" section. But you will have to do this after each startup of Maya.


--------------------------------------------
Nuke

Nuke is also easy to configure if the OCIO environment variable is set:

Go to "Edit > Project Settings".
In the Tab "Color" switch "color management" to OCIO (which only will appear if env var is set!).


--------------------------------------------
Resolve

Go to Settings (the gear symbol on the bottom right corner).
In the list on the left switch to "Color Management".

Set:
Color science: ACEScct
ACES version: 1.1
(or your choosen Version)

ACES Input Device Transform: ACEScg
ACES Output Device Transform: sRGB
