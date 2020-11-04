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

Minipipe just saves you from choosing save paths and file names each time and offers streamlined tasks based on the current stage of a file. It thereby suggests a certain workflow.

For example
+ it offers to create relative references of availible *props* which already have a *shading release* if you are working in a file of type *set*.  
+ it offers to create relative references of availible *chars* which already have a *rig release* if you are working in a file of type *shot*.
+ it offers to export alembic-caches of all referenced *chars* if you are working in a file of type *shot* in department *animation*.

## How to start?

### Create new assets
Create new assets by clicking on one of the asset types in the *"CREATE NEW"* section. The IN and OUT sections will offer different actions based on the type of the asset and the current stage / department.

+ **Character:** Assets that will later be rigged/animated. Typical examples are your "actors" (humans, animals, robots, drohnes...) and objects your "actors" will interact with (move).
+ **Prop:** Unanimated objects like furniture or parts of a landscape.
+ **Set:** A collection of props and some additional models for example a room or a landscape
+ **Shot:** A shot of your production containing sets, props, cameras, keyframed characters in stage *Animation* or cached characters and the shot lighting in stage *Rendering*.
+ **Extras:** Things that fit non of the above mentioned categories.

When you create a new asset, a folder structure will be created in your maya projects scene directory in a subdirectory called like the *type*. (For a character named *sam* it would create a folder *sam/* in *scenes/chars/* and inside the *sam* folder there will be a *versions/mod* and *release_history/mod* folder). It also creates a starter file  by copying and renaming the *scenes/initial.ma* to the *versions/mod*. You could adjust the *initial.ma* file if for example you want all your started assets to contain a specific node.

### Save
You can use the normal Maya save function by pressing ctrl + s.

### Save new version
If you want to keep the previous saved file and save your current changes under a new name, use the *"Save New Version"* button in the OUT tab. This will copy the current version into the *versions/-department-* folder and save your current scene with a new name.

### Take a screenshot for your asset
In the OUT tab you can click on the template image (a box for props, a house for sets...) to create a new thumbnail picture for your asset. At the moment two windows will be opened - a viewport and a "Capture Control" window. Use the viewport to frame your object and use the red "Capture" button to save the viewport image. If you change the viewport mode (textured view, antialiasing...) in your normal Maya viewport, these changes will be reflected in the capture window too.

## What to do when?
### Create a modeling release
You can do this early in the process if you need access to unfinished models for set building or shot blocking purposes. Be aware that actions like freezing transforms, changing pivot points, changes to names or hirarchies may lead to unexpected results if the asset is already in use in another scene (e.g. a prop thats placed in a set will change position in the set if its pivot changes in the released model file).

If the model is released for deformation rigging the topology should not be changed anymore.

### Create first Shading Version
To create a first shading
For **props** you create the first shading version out of the **model** department
If it is planned to just assign a shader to the model (no per face assignments, no textures) a Shading Release can be done while the model is still worked on. However if names, hirarchies or object count changes it may be necessary to reassign the shaders manually.

If you use per face assignments of shaders, changes to the topology of the model will result in loss of shader assignments in your shading file (you can always reassign your shaders manually).

If you start to texture the asset be shure to also have final UVs before starting the texture process.


