# SourceMod Workflow

A Python script to help with plugin releases.  This is especially helpful for plugins that define include files.  It is intended to be used with GitHub's [`gh`](https://cli.github.com/) command, but can be used to only create zip archives instead of also uploading them to GitHub as releases.

## Why?

Since multiple plugins and files reside in `addons/sourcemod/scripting` it is difficult to manage them using git repos - unless you want to resort to using something like the `--git-dir` and `--work-tree` flags (which is not ideal either).  Ideally each plugin would be in its own folder with its own git repo.

Unfortunately, creating zip archives with your plugin's `.sp` files, `include` folder, and `.smx` file is very tedious.  This script is intended to help create GitHub releases when using a setup wherein each plugin is in its own folder.

This script will find each plugin's version, create a zip archive for it, and create a GitHub release for it if one does not already exist with the current version.  It uses GitHub's [gh](https://github.com/cli/cli#installation) command for this.

The zip archives are created by copying `*.sp` files in the plugin's base folder, copying the `include` folder, and also compiling and copying the `.smx` file.  Any extra files specified in the config will also be copied.  All other files will not be found in the zip archive.  The zip files will be created inside the specified release directory with their versions appended.

## Folder Setup

You can find an example of the folder structure used [here](structure.md) and installation instructions [here](install.md).  Note: the specified release directory should not exist initially - it will be created by the script.

Each plugin should be in its own folder, and that folder should have the same name as the `.sp` file you wish to be compiled (without the `.sp` extension of course).  Otherwise it wouldn't know which file to compile.

The script will also look in that `.sp` file for a version number.  If you do not wish to use the version from the `.sp` file, or you do not have any `.sp` files in your folder (like when releasing just `.inc` files), you can define a `version.txt` file with the sole contents of the file being the version (nothing else in the file).



## Usage

When you are ready to create a release just run the following from a command prompt:

```shell
python release.py
```

It will print out the plugins found, their versions, and a count of how many plugins had new releases.  New releases will appear in a different color and with a `->` separating the plugin name from version number.

By default it will use the `gh` command and only create a release if a release does not exist for the plugin's current version.

The following arguments can modify the script's behavior:

```
-g --nogit     do not use gh to check for or upload release
               this will still create a zip file for each plugin
               note: this will overwrite existing archives of the
                     same version
-s --nosummary suppress the updated count at the end
-q --quiet     only show errors/warnings
```





#### Optional Shell Script

Personally I also define a shell script that calls the python script and copies my plugins' files to the `addons/sourcemod/scripting` folder (copying files in the `include` directory to the `addons/sourcemod/scripting/include` folder.

For those you Linux you can find my bash script [here](copy.md).

## Installation

See [installation](install.md).
