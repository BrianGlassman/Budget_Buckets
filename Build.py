"""Script to run pyinstaller and handle the settings files that are needed"""

import PyInstaller.__main__
import os
import shutil

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

PyInstaller.__main__.run(args)
dist_dir = os.path.join('dist', 'Main')

folders = [
    'Categorize',
    'Parsing',
    'Raw_Data',
    'Root',
]
for folder in folders:
    os.mkdir(os.path.join(dist_dir, folder))

filepaths = [
    ['Categorize', 'AutoTemplates.json'],
    ['Categorize', 'Templates.json'],
    ['Categorize', 'ManualAccountHandling.json'],
    ['Parsing', 'ParseSettings.json'],
    ['Root', 'Constants.py'], # Not used, but good for the user to have
]
for dir, file in filepaths:
    filepath = os.path.join(dir, file)
    shutil.copy2(filepath, os.path.join(dist_dir, filepath))

for file in os.listdir('Raw_Data'):
    if file == '.git': continue # Don't need .git, and it will error in copy anyway
    filepath = os.path.join('Raw_Data', file)
    shutil.copy2(filepath, os.path.join(dist_dir, filepath))