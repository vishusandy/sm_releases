# Installation

Note: this requires python to be installed on your system.  See the [Python Wiki](https://wiki.python.org/moin/BeginnersGuide/Download) for instructions on installing python.

1. [Install](https://github.com/cli/cli#installation) the `gh` command. Windows users may want to see the [Releases](https://github.com/cli/cli/releases/) page.

2. [Authenticate](https://cli.github.com/manual/gh_auth_login) with your GitHub account

3. Choose a folder to store your plugins (separate from your 'scripting' folder). Example: `$HOME/my_plugins`. This is where all of your plugins will be kept.

4. Copy the python scripts to that folder (or to a `scripts` folder within it)

5. Edit `config.py`
   
   - See the comments for each entry for documentation
   
   - The most important item to edit is the `plugins_dir` entry - this should point to the `addons/sourcemod/plugins` folder that you are using. The rest are optional.
   
   - The `plugins_dir` and `spcomp` entries have environmental variables it looks for as a fallback, `SOURCEPAWN_PLUGINS` and `SOURCEPAWN_SPCOMP` respectively.

Note for Linux users: you must make your `spcomp` file executable, otherwise you will get a permission error when running the script. Example: `chmod +x spcomp` (when your terminal's working directory is the `addons/sourcemod/scripting` directory).
