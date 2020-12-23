This Repo contains Rig-Tools, the Minipipe and other Stuff

# 1 Installation

## 1.1 Via Commandline / git bash
git clone https://github.com/jobomat/hdm_cg.git to the *desired location* on your computer.

## 1.2 Via Zip-File
Click the green "Code" Button above and download the repo as zip file. Unpack to your *desired location*

# 2 Setup
1. Close Maya.
2. Copy the Files *userSetup.py* and *config.json* from the folder *setup* to your *maya/scripts* location.
+ **Windows:** drive:\Users\\*username*\Documents\maya\scripts
+ **Mac:** /Users/username/Library/Preferences/Autodesk/maya/scripts
+ **Linux:** ~/maya/scripts
3. Edit the *config.json*. The key *"GLOBAL_SETUP_PATH"* has to hold the path to *desired location*/hdm_cg. This may be another name based on your installation process. Make sure it points to the folder containing the *cg*, *maya* and *setup* folders.

# 3 Minipipe
## 3.1 Create a new Minipipe Project
This has only to be done once. If a coworker already has performed these steps and you want to join this project see section *"3.3 Switch to existing Minipipe Project"*.

1. Open Minipipe by clicking the new *HdM* Button on the toolbar in Maya (the bar on the left side beneath the *Show Outliner* Button).
2. Click on *Settings*.
3. In the *Minipipe Starter* section choose a *Base Path* (an empty folder preferably named like your project or a shortened version of the project name).
4. Choose a *Minipipe Template* (ca_stupro).
5. Click *Create Project*.

## 3.2 Complete your Settings

### 3.2.1 Set a Username
In the Minipipe Settings under *Current User* choose a short username e.g. your shorthand HdM account name (xy123) and click *Save to Global Config File*.

The user info is saved on a per-computer-account-basis. If you are working at the same project on different computers and/or under different user accounts but want to use the same user name in each environment, make sure to choose the same user name and save it to the global config for each computer/accout.

You could choose different names to later differentiate from which account or computer a file was saved if that is of any use for you.

### 3.2.2 Set a (Remote) Render Base Path
The setting *Path at Render Location* should contain the path to your Maya at the location where you are planning to render your scenes at a render farm. At HdM this is typically one of the cg-drives (L:/, M:/, N:/) followed by the sub directories to your Maya project (eg. M:/MyProject/3d).

## 3.3 Switch to existing Minipipe Project
In the *Settings* click *Choose Config* and load the *minipipe_config.json* which normally resides in *pipeline/minipipe* in the project folder.

At the moment it is save to restart Minipipe after that by clicking on the *HdM* button again.


## 3.4 Working with Minipipe
Minipipe is a folder- and filename-convention based load/save/reference/cache helper for your project (with a little meta-info here and there contained in the *"minipipe_meta"* node of the files saved or created with Minipipe).

In short it suggests certain INPUT and OUTPUT actions based on the *type* (char, prop, set, shot) and the existent *departments* (mod, rig, shd, ani, rnd) of a file in your project.

It makes it easy to create versions, releases, references and caches. All executed actions are standard Maya actions that could also be performed the standard Maya way.

Minipipe just saves you from choosing save paths and file names each time and offers streamlined tasks based on the current stage of a file. It thereby suggests a certain workflow.

For example
+ it offers to create relative references of availible *props* which already have a *shading release* if you are working in a file of type *set*.  
+ it offers to create relative references of availible *chars* which already have a *rig release* if you are working in a file of type *shot*.
+ it offers to export alembic-caches of all referenced *chars* if you are working in a file of type *shot* in department *animation*.

You always can bypass this workflows with your own manualy executed standard Maya actions like referencing scenes, import/export caches and only use the parts of Minipipe that fit your needs.

### 3.4.1 Create new assets
Create new assets by clicking on one of the asset types in the *"CREATE NEW"* section. The IN and OUT sections will offer different actions based on the type of the asset and the current stage / department.

+ **Character:** Assets that will later be rigged/animated. Typical examples are your "actors" (humans, animals, robots, drohnes...) and objects your "actors" will interact with (move).
+ **Prop:** Unanimated objects like furniture or parts of a landscape.
+ **Set:** A collection of props and some additional models for example a room or a landscape
+ **Shot:** A shot of your production containing sets, props, cameras, keyframed characters in stage *Animation* or cached characters and the shot lighting in stage *Rendering*.
+ **Extras:** Things that fit non of the above mentioned categories (Experimenatl atm).

When you create a new asset, a folder structure will be created in your maya projects scene directory in a subdirectory called like the *type*. (For a character named *sam* it would create a folder *sam/* in *scenes/chars/* and inside the *sam* folder there will be a *versions/mod* and *release_history/mod* folder). It also creates a starter file  by copying and renaming the *scenes/initial.ma* to the *versions/mod*. You could adjust the *initial.ma* file if for example you want all your started assets to contain a specific node.

### 3.4.2 Save
You can use the normal Maya save function by pressing ctrl + s if you just want to overwrite the version you are working on.

#### 3.4.2.1 Save new version
If you want to keep the previous saved file and save your current changes under a new name, use the *"Save New Version"* button in the OUT tab. This will save your current scene under a new name in the *versions/-department-* folder.

#### 3.4.2.2 Take a screenshot for your asset
In the OUT tab you can click on the template image (a box for props, a house for sets...) to create a new thumbnail picture for your asset. At the moment two windows will be opened - a viewport and a "Capture Control" window. Use the viewport to frame your object and use the red "Capture" button to save the viewport image. If you change the viewport mode (textured view, antialiasing...) in your normal Maya viewport, these changes will be reflected in the capture window too.

### 3.4.3 Workflow

#### 3.4.3.1 Modeling Department
The modeling department exists for props, chars and sets. Models and UVs for props and characters are created here. Additional models in sets that are not explicit props (like walls) can be modeled and shaded here.

##### Quick overview of IN Actions
+  Open a specific version.
+  Sets: Pull in released props as references

##### Quick overview of OUT Actions
+  Save a new version.
+  Characters: Create releases and create the first rigging version. The first shading version and shading releases for characters have to be done from the rigging stage.
+  Props: Create the first shading version from here when model (and ideally) UVs are finished.
+  Sets: Release model or shading version (preferably shading! See last Paragraph in *Details*).

##### Details
Hand off a character model to rigging by creating a release and then create the first rig version. **IMPORTANT: If the model is released for deformation rigging the topology should not be changed anymore!** The UVs on the other side do not have to be finished to release for rigging.

For *character* types (will be rigged) talk to the rigger about how to group your objects. Grouping can also happen in the rigging department, but ungrouping can't when working with references. When in doubt do not group anything in models of type character. This is the reason why shading releases for characters have to be triggered from the rigging department. As the grouping of objects is essential when working with caches and the final grouping may be decided up on in rigging department, one only can create a "correct" first shading version from inside the rigging file.

You can release models early in the process if you need access to unfinished models for set building or shot blocking purposes. Be aware that actions like freezing transforms, changing pivot points, changes to names or hirarchies may lead to unexpected results if the asset is already in use in another scene (e.g. a prop thats placed in a set will change position in the set if its pivot changes in the released model file).

For props you create the first shading version out of the model department. If it is planned to just assign a shader to the model (no per face assignments, no textures) a shading release can be done while the model is still worked on! However if names, hirarchies or object-count changes, it may be necessary to reassign the shaders manually. If you use per face assignments of shaders, changes to the topology of the model will result in loss of shader assignments in your shading file (you can always reassign your shaders manually).

If you start to texture the asset be shure to also have final UVs before starting the texture process.

Model versions of sets are not particulary useful. Switch to shading releases as soon as you want the animation department to find the set without any further hassle (normaly ASAP). Modeling and UVs for non-prop-addons can also be done in the shading versions of sets.

#### 3.4.3.2 Rigging Department

##### Quick overview of IN Actions
+  Open a specific version.

##### Quick overview of OUT Actions
+  Save a new version.
+  Release a rig.
+  Create the first shading version.

##### Details
Release a rig as soon as it has the first useful features for your animators. Once your released rig is used (referenced) in an animation version of a shot think careful about what you can change without destroying the already made animation:

You can:
+  add new controllers and attributes to existing controllers.
+  remove controllers and attributes that are not already keyed in a shot.
+  rework the internals of your deform and control rig that are not exposed to the animators.

You should not:
+  remove controllers and attributes that are already keyed in a shot.
+  rename or regroup controllers that are already in use.

Release the first shading version as soon as you grouped the objects (referenced from the model release file) by your liking and the model department provided a final model. Final means final object count, final hirarchy (grouping) and final naming. If the prop is to be textured in also means final UVs. One could release a "not final" model-release for shading tests. For expample when final UVs are missing, testing shading parameters without applying textures is totally fine. Textures made on not final UVs are useless. Also note that per-face-assignments of shaders will be useless for models without final topology.

#### 3.4.3.3 Shading Department

##### Quick overview of IN Actions
+  Open a specific version.
+  Update Model (Merge in a new Alembic-Base-Mesh)

##### Quick overview of OUT Actions
+  Release a shading file.

##### Details
The update process is necessary if the model department changed any shading-relevant parameters:

+  A change in topology if there are per-face-assignments of shaders. In this case the assignments will be lost in parts or completely and you'll have to reassign the shaders. 
+  Changed UVs if you are using texture maps

If you use object-assigned shaders without uv-based texture maps an update is not necessary unless the modeling/rigging department made changes to hirarchy or names. In this case it even could be necessary to delete the model group and import the updated cache via "Cache > Alembic Cache > Import" ("Add" NOT "Merge" in the Options). All shader assignments will be lost and have to be redone in this case.

#### 3.4.3.4 Animation Department

The animation department acts on sequences rather than shots. A sequence is a somehow connected series of shots. For example a sequence could contain a continous action of one or more characters that will be showed from different camera angles. In this example the different camera angles represent the shots. The idea of a sequence is that it contains the animation in one piece (and maybe also shares a basic light-setup that will be augmentet with more lights on a per-shot-basis).

An animation-type asset ideally only contains the sets, props, characters and cameras of a sequence but no lights of other render specific items.

##### Quick overview of IN Actions
+  Open a specific version.
+  Pull in rig-releases of characters.
+  Pull in shading-releases of sets.
+  Pull in any other asset if necessary.

##### Quick overview of OUT Actions
+  Save a new Version.
+  Flag cameras as relevant "shot cameras" with frame ranges and export option.
+  Create caches for the characters of the sequence.
+  Create the Shots of the Sequence.

##### Details
To pull in other types than characters and sets or other department stages than rig and shading just remove the respective checkboxes on the bottom of the "Create Reference" list.

To remove references use the normal Maya way to do this (In the Outliner right-click on a reference node and choose "Remove" from the "Reference" sub menu).

If you flag a camera as "shot camera" it will be easy exportable. Furthermore the camera movement will automatically be baked before exporting it. The aim is to clearly seperate tasks between animation and lighting/rendering department. Camera movement should not be done or edited in the lighting/rendering department. On the other hand it is not recommended to add lights in the animation department.

Caches will be exported to the "caches" subfolder of the current shot. Already existing caches of the same name will be replaced but the old version will be copied to "caches/archives" beforehand.

On creating the "Render Versions" (AKA Shots) you can decide what will be present in the shot-files:

+  For characters you can replace the rig versions of the characters with the shading version.
+  For cameras you can bake and export the flagged cameras and reference the resulting files in the created shot file.

Both actions can safely be done quite early in the process. New camera movements and character animations can always be exported again and will find their way into the shot files.

#### 3.4.3.5 Render (Lighting) Department

##### Quick overview of IN Actions
+  Open a specific version of a specific Variant (Shot).
+  Pull in shading-releases of characters.
+  Pull in shading-releases of sets.
+  Pull in any other asset if necessary.
+  Pull in a cache for every asset of type character.
+  Pull in a baked Camera from Animation Department.

##### Quick overview of OUT Actions
+  Save a new Version.
+  Release a Render File (with replacement of Alembic paths!)
+  Create a RenderPal Render-Set

##### Details
To create a RenderSet you have to create a Release-File first. This is because only in the Releases the correct paths for Alembic caches relative to the render location will be set.