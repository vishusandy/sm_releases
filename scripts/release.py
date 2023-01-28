import argparse
import os
import platform
import re
import shutil
import subprocess
import sys
from pathlib import Path
from config import config

# leave blank to use the SOURCEPAWN_PLUGINS env var
# config["release_dir"] = config['release_dir']

# color_update = config['colors']['update']
# color_nochange = config['colors']['nochange']

"""
Finds version number of sourcemod plugins, checks plugin version against existing releases,
and creates release archives that are automatically uploaded to github.

The folder name for a plugin should also be the name of the main .sp file for the plugin.
This helps it find the version information.

If you are not using a main sp file (or you aren't defining a version number in its plugin info) 
you can add a 'version.txt' with the version number.  This will override any version number from
the main sp file.

INSTALLATION
    - Install the github cli (gh command) and login with it
        - Installation: https://github.com/cli/cli#installation
        - Login: https://cli.github.com/manual/gh_auth_login
    - Edit `config.py` - ensure `plugins_dir` is set - the rest are optional.

USAGE
    `python release.py`

STRUCTURE
    - your_plugins/
        - plugin_a/
            - plugin_a.sp
            - include/
                - some_include_for_a.inc
        - plugin_b/
            - plugin_b.sp
            - include/
                - some_include_for_b.inc
        - releases/
            - plugin_a_v<version>
                - scripting/
                    - plugin_a.sp
                - plugins/
                    - plugin_a.smx
            - plugin_b_v<version>
                - scripting/
                    - plugin_b.sp
                    - include/
                        - some_include.inc
                - plugins/
                    -plugin_b.smx

NOTES
    - Plugin folders must be the same name as the main .sp file you wish to compile for each plugin
        (if you wish to automatically find the version from a .sp file, otherwise use `version.txt`)
    - Only *.sp and the include folder is copied into the release archive for each plugin.  This
      allows extra files, like markdown files and screenshots, to be in your repository but not
      included in releases.  By default the following files are copied:
        - plugin_name/*.sp
        - plugin_name/include/
    - The script will attempt to compile your plugin, otherwise it will look for the smx file in your
      `plugins_dir` folder.
    - The script will treat all folders in your working directory as plugins unless excluded in
      config.py
    - You can also use symbolic links to link to other files, for example in a plugin's include dir
      you can have a symbolic link that points to an include file, or a whole directory, and those
      will be copied as files (not links).

"""

# Bold
bld = '\033[01m'

# Reset
rst = '\033[00m'

plugins_folder = None
spcomp_path = None
quiet = False
version_regex = re.compile(r'(?:version ?= ?")([^"]*)(?:")')


if config['plugins_dir'] is not None and config['plugins_dir'] != "" and Path(config['plugins_dir']).exists():
    plugins_folder = config['plugins_dir']
else:
    plugins_env_var = os.getenv('SOURCEPAWN_PLUGINS')

    if plugins_env_var is None or not os.path.exists(plugins_env_var):
        home = os.path.expanduser('~')
        plugins_folder = os.path.join(
            home, 'sourcemodAPI', 'addons', 'sourcemod', 'plugins')
    else:
        plugins_folder = plugins_env_var

if not os.path.exists(plugins_folder):
    print(config['colors']['error'] +
          'Could not find suitable plugins folder' + rst, file=sys.stderr)
    exit()


if config['spcomp'] and Path(config['spcomp']).exists():
    spcomp_path = config['spcomp']
else:
    spcomp_env = os.getenv('SOURCEPAWN_SPCOMP')
    if spcomp_env is None or not Path(spcomp_env).exists():
        sp = Path(plugins_folder).parent
        if platform.system() == 'Windows':
            spcomp_path = sp.joinpath('scripting', 'spcomp.exe')
        else:
            spcomp_path = sp.joinpath('scripting', 'spcomp')
    else:
        spcomp_path = spcomp_env

if not Path(spcomp_path).exists():
    print(config['colors']['warning'] +
          'Could not find spcomp - will look for existing smx files in plugins directory' + rst, file=sys.stderr)


def get_version(name):
    file = f'{name}/version.txt'
    if os.path.exists(file):
        with open(file) as f:
            text = f.readline().rstrip('\n').strip()
            if len(text) > 0:
                return text

    file = f'{name}/{name}.sp'
    if os.path.exists(file):
        with open(file) as f:
            text = f.read()
            results = [match.group(1)
                       for match in version_regex.finditer(text)]

            if len(results) == 1:
                return results[0]
            if len(results) > 1:
                print(
                    f'  {config["colors"]["warning"]}{file} returned multiple possible version matches' + rst, file=sys.stderr)
            else:
                print(
                    f'  {config["colors"]["warning"]}{file} returned no version matches' + rst, file=sys.stderr)

    return None


def copy_scripting_files(dir, dest):
    if len(os.listdir(dir)) == 0:
        return

    os.mkdir(dest)
    with os.scandir(dir) as it:
        for entry in it:
            if entry.is_file() and entry.name.endswith('.sp'):
                shutil.copy2(entry.path, dest)
            elif entry.name in config['extra_files']:
                shutil.copy2(entry.path, dest)
            elif entry.is_dir() and entry.name == 'include':
                path = os.path.join(dest, "include")
                os.mkdir(path)
                shutil.copytree(entry.path, path, dirs_exist_ok=True)


def compile_smx(entry, dest):
    input_file = os.path.join(entry.path, f'{entry.name}.sp')
    out_file = Path(dest).joinpath(f'{entry.name}.smx')
    os.mkdir(dest)

    if not Path(input_file).exists():
        return 1

    global_inc = Path(plugins_folder).parent.joinpath('scripting', 'include')
    rel_inc = Path(entry.path).joinpath('include')

    args = [spcomp_path, input_file, f'-o{out_file}', f'-i{entry.path}',
            f'-i{rel_inc}', f'-i{global_inc}', '-O2', config['compile_verbosity']]

    for i in config['extra_include_dirs']:
        args.append('-i' + i)

    result = subprocess.run(args, stdout=subprocess.DEVNULL)

    if result.returncode == 0 and out_file.exists():
        file = os.path.join(plugins_folder, f'{entry.name}.smx')
        shutil.copy2(out_file, file)
    elif result.returncode != 0:
        print(
            f'{config["colors"]["error"]}  error occurred compiling smx file {entry.name}{rst}')

    return result.returncode


def copy_smx_file_from_plugins_folder(name, dest):
    file = os.path.join(plugins_folder, f'{name}.smx')
    if os.path.exists(file):
        os.mkdir(dest)
        shutil.copy2(file, dest)
        print(config['colors']['warning'] +
              '  warning: copied existing smx file instead of compiling new smx file' + rst, file=sys.stderr)
    else:
        print(config['colors']['warning'] +
              f'  warning: smx file not found: {file}{rst}', file=sys.stderr)


def copy_smx_file(entry, dest):
    if spcomp_path is not None:
        if compile_smx(entry, dest) == 0:
            return

    copy_smx_file_from_plugins_folder(entry.name, dest)


def create_script_dirs(name):
    os.mkdir(f'{config["release_dir"]}/{name}')


def create_archive(name, version):
    archive = os.path.join(f'{config["release_dir"]}', f'{name}_v{version}')
    shutil.make_archive(archive, 'zip', f'{config["release_dir"]}/{name}')
    shutil.rmtree(f'{config["release_dir"]}/{name}')


def create_release_archive(entry, version):
    if os.path.exists(f'{config["release_dir"]}/{entry.name}'):
        shutil.rmtree(f'{config["release_dir"]}/{entry.name}')

    create_script_dirs(entry.name)
    copy_scripting_files(
        entry.path, f'{config["release_dir"]}/{entry.name}/scripting/')
    copy_smx_file(
        entry, f'{config["release_dir"]}/{entry.name}/plugins/')
    create_archive(entry.name, version)


def create_gh_release(name, version):
    os.chdir(name)

    archive = os.path.join(
        '../', f'{config["release_dir"]}', f'{name}_v{version}.zip')
    changelog = os.path.join('../', name, 'CHANGELOG.md')
    if not os.path.exists(archive):
        print(config['colors']['error'] +
              '  error: could not find newly created archive "{archive}"' + rst, file=sys.stderr)
    else:
        if os.path.exists(changelog):
            process = subprocess.Popen(
                ['gh', 'release', 'create', f'v{version}', archive, '-F', changelog], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        else:
            process = subprocess.Popen(
                ['gh', 'release', 'create', f'v{version}', archive], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        _, stderr = process.communicate()

        if stderr == True:
            print(config['colors']['error'] +
                  f'  error creating release: {stderr}{rst}', file=sys.stderr)
            os.chdir('../')
            return False

        os.chdir('../')
        return True


def check_gh_release(entry, version):
    os.chdir(entry.name)

    try:
        process = subprocess.Popen(
            ['gh', 'release', 'view', f'v{version}'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    except Exception as e:
        return None

    _, stderr = process.communicate()
    os.chdir('../')
    if stderr == 'release not found\n':
        if not quiet:
            print(
                f'{bld}{config["colors"]["update"]}{entry.name} -> {version}{rst}')
        create_release_archive(entry, version)
        return create_gh_release(entry.name, version)
    else:
        if not quiet:
            print(f'{config["colors"]["nochange"]}{entry.name} {version}{rst}')
        return None


def plugins_scan(dir, gh: bool):
    i = 0
    with os.scandir(dir) as it:
        for entry in it:
            if entry.is_dir() and not entry.name.startswith('.') and entry.name not in config['exclude_plugin_dirs']:
                version = get_version(entry.name)
                if version is not None:
                    if not gh:
                        if not quiet:
                            print(
                                f'{config["colors"]["nochange"]}{entry.name} {version}{rst}')
                        create_release_archive(entry, version)
                    elif gh and check_gh_release(entry, version) is True:
                        i += 1
    return i


def summary(i: int):
    if i != 1:
        plural = 's'
    else:
        plural = ''

    if i > 0:
        print(
            f'\n{config["colors"]["summary"]}{i} plugin{plural} updated{rst}')
    else:
        print(f'\n0 plugins updated')


def main():
    if not os.path.exists(f'{config["release_dir"]}'):
        os.mkdir(f'{config["release_dir"]}')

    parser = argparse.ArgumentParser(
        description='Utility for creating plugin releases')
    parser.add_argument('-g', '--nogit', action='store_false')
    parser.add_argument('-s', '--nosummary', action='store_true')
    parser.add_argument('-q', '--quiet', action='store_true')
    args = parser.parse_args()

    global quiet
    quiet = args.quiet

    if not quiet:
        print('Checking plugins...\n')

    i = plugins_scan('.', args.nogit)

    if not quiet and not args.nosummary:
        summary(i)


if __name__ == "__main__":
    main()
