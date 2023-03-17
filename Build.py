"""Script to run pyinstaller/nuitka and handle the settings files that are needed"""

import os
import shutil
from typing import Literal

from Root import Constants

def run_nuitka(compile=True, mac_bundle=False):
    dist_dir = 'Main.dist'
    if not compile:
        return dist_dir
    
    base_cmd = 'python3.10 -m nuitka --standalone' # The base command to make a portable binary
    args = ['--enable-plugin=' + '='.join(['tk-inter'])] # Plugins needed or certain libraries
    # Note: per the help printout, numpy plugin is deprecated and should not be used
    if mac_bundle:
        # Make a Mac App, instead of just a binary
        args.append('--macos-create-app-bundle')
    target = 'Main.py' # The entry point

    args = ' '.join(args)
    command = f"{base_cmd} {args} {target}"

    print(f"Command: {command}")
    os.system(command)

    return dist_dir

def run_pyinstaller(compile=True):
    dist_dir = os.path.join('dist', 'Main')
    if not compile:
        return dist_dir

    import PyInstaller.__main__
    args = [
        'Main.py',
        '--noconfirm', # Don't ask for confirmation before deleting
    ]
    hidden_imports = [
        'matplotlib',
        'tkinter'
        'PIL', 'PIL._imagingtk', 'PIL._tkinter_finder',
    ]
    for hi in hidden_imports:
        args.append(f'--hidden-import={hi}')

    print(f"Args: {args}")
    PyInstaller.__main__.run(args)

    return dist_dir

def run(mode: Literal['nuitka', 'pyinstaller'], compile=True, **kwargs):
    if mode == 'nuitka':
        dist_dir = run_nuitka(compile=compile, **kwargs)
    elif mode == 'pyinstaller':
        dist_dir = run_pyinstaller(compile=compile, **kwargs)
    else:
        raise NotImplementedError()

    folders = [
        'Categorize',
        'Parsing',
        'Raw_Data',
        'Root',
    ]
    for folder in folders:
        target = os.path.join(dist_dir, folder)
        if not os.path.isdir(target):
            os.mkdir(target)

    for filepath in Constants.filepaths:
        shutil.copy2(filepath, os.path.join(dist_dir, filepath))

    for file in os.listdir('Raw_Data'):
        if file == '.git': continue # Don't need .git directory, and it will error in copy anyway
        src = os.path.join('Raw_Data', file)
        dst = os.path.join(dist_dir, src)
        if os.path.isfile(dst):
            os.remove(dst)
        shutil.copy2(src, dst)

if __name__ == "__main__":
    run('pyinstaller', compile=True)