Bash script for Linux users:

```bash
#!/usr/bin/env bash

# this directory should contain your plugin folders
SRC=~/my_plugins
# location to copy the files to
DEST=~/sourcemodAPI/addons/sourcemod/scripting

for plugin in "$SRC"/*; do
    # if it's not a directory skip it
    [ -d "$plugin" ] || continue

    # ignore the 'scripts' and 'releases' folders
    if [ "$plugin" = "scripts" ] || [ "$plugin" = "releases" ] || [ "$plugin" = "docs" ]; then continue; fi

    cd "$plugin" || continue

    # check to see if any .sp files exist in the base of the plugin directory
    if compgen -G "*.sp" >/dev/null; then
        rsync --update ./*.sp "$DEST"
    fi

    # copy the include folder if it exists
    [ -d "${plugin}/include" ] || continue
    rsync --update -q -r "$plugin/include/" "$DEST/include/"
done

# run the release python script
# NOTE: make sure to update the path if it is not located in the scripts folder
python scripts/release.py
```

Don't forget to make the script executable.
