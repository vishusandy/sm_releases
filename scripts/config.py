

config = {
    # location of addons/sourcemod/plugins
    # leave blank to use the SOURCEPAWN_PLUGINS env var if available
    # will attempt to use $HOME/sourcemodAPI/addons/sourcemod/plugins as a fallback
    "plugins_dir": "",

    # location of spcomp (path and filename)
    # leave blank to use the SOURCEPAWN_SPCOMP env var if available
    # otherwise will use plugin_dir's path to look for '../scripting/spcomp[.exe]'
    "spcomp": "",

    # store zip archives in this folder
    "release_dir": "releases",

    # do not treat these directories as plugin directories
    "exclude_plugin_dirs": ['scripts', 'docs'],

    # extra files that should be copied for each plugin (if they exist)
    "extra_files": ['LICENSE.txt'],

    "compile_verbosity": "--verbose=2",

    # add these directories as paths to include files when compiling
    "extra_include_dirs": [],


    # ANSI color codes:
    #   https://en.wikipedia.org/wiki/ANSI_escape_code#8-bit
    "colors": {
        # Color for plugins with a new release
        "update": '\033[38:5:10m',
        # Color when only creating archives
        "archive": '\033[38:5:12m',
        # Color for plugins without a new release
        "nochange": '\033[38:5:250m',
        # Color for updated count in summary
        "summary": '\033[38:5:10m',

        "warning": '\033[38:5:202m',
        "error": '\033[38:5:9m',
    }
}
