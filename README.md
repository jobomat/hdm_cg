# Rig-Tools, Minipipe and Stuff

## Installation

### Via Commandline / git bash
git clone https://github.com/jobomat/hdm_cg.git to the *desired location* on your computer.

### As Zip-File
Click the green "Code" Button above and download the repo as zip file. Unpack to your *desired location*

## Setup
1. Close Maya.
2. Copy the Files *userSetup.py* and *config.json* from the folder *setup* to your *maya/scripts* location.
+ **Windows:** drive:\Users\\*username*\Documents\maya\scripts
+ **Mac:** /Users/username/Library/Preferences/Autodesk/maya/scripts
+ **Linux:** ~/maya/scripts
3. Edit the *config.json*. The key *"GLOBAL_SETUP_PATH"* has to hold the path to *desired location*/hdm_cg. This may be another name based on your installation process. Make sure it points to the folder containing the *cg*, *maya* and *setup* folders.

## Create New Minipipe Project
This has only to be done once. If a coworker already has performed these steps and you want to join this project see the next section *"Switch to existing Minipipe Project"*.

1. Open Minipipe by clicking the new *HdM* Button on the toolbar in Maya (the bar on the left side beneath the *Show Outliner* Button).
2. Click on *Settings*.
3. In the *Minipipe Starter* section choose a *Base Path* (an empty folder preferably named like your project or a shortened version of the project name).
4. Choose a *Minipipe Template* (ca_stupro).
5. Click *Create Project*.

## Switch to existing Minipipe Project
In the *Settings* click *Choose Config* and load the *minipipe_config.json* which normally resides in *pipeline/minipipe* in the project folder.

At the moment it is save to restart Minipipe after that by clicking on the *HdM* button again.

## Set a Username
In the Minipipe Settings under *Current User* choose a short username e.g. your shorthand HdM account name (xy123) and click *Save to Global Config File*.

The user info is saved on a per-computer-account-basis. If you are working at the same project on different computers and/or under different user accounts but want to use the same user name in each environment, make sure to choose the same user name and save it to the global config for each computer/accout.

You could choose different names to later differentiate from which account or computer a file was saved if that is of any use for you.

## Working with Minipipe
Minipipe is a folder- and filename-convention based load/save/reference/cache helper for your project (with a little meta-info here and there contained in the *"minipipe_meta"* node of the files saved or created with Minipipe).

In short it suggests certain INPUT and OUTPUT actions based on the *type* (char, prop, set, shot, extra) and the existent *departments* (mod, rig, shd, ani, rnd) of a file in your project.

It makes it easy to create versions, releases, references and caches. All executed actions are standard Maya actions that could also be performed the standard Maya way.

Minipipe just saves you from choosing save paths and file names each time and offers streamlined tasks based on the current stage of a file.

For example
+ it offers to create relative references of availible *props* which already have a *shading release* if you are working in a file of type *set*.  
+ it offers to create relative references of availible *chars* which already have a *rig release* if you are working in a file of type *shot*.
+ it offers to export alembic-caches of all referenced *chars* if you are working in a file of type *shot* in department *animation*.

More actions are added at the moment.