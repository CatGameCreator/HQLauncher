import configparser
import os
import sys
import random
from pathlib import Path
from packaging.version import Version
from github import Github
import requests
import zipfile
import glob
import shutil
import subprocess

file_path = os.path.realpath(__file__)
file_directory_path = os.path.dirname(sys.argv[0])
file_directory_path = os.path.abspath(file_directory_path)
assets_path = rf"{file_directory_path}\assets"
settings_path = rf"{file_directory_path}\assets\settings.ini"
#Seting Methods
config = configparser.ConfigParser()
g = Github()
session = requests.Session()
#Settings
minecraft_directory = "appdata/.minecraft"
language = "en"
allow_experimental_settings = "0"
integrity_check = "1"
update_check = "1"
version = "0.1.0"
app_config_version = "0.0.1"
config_version = "0.0.1"
current_user_id = str(random.randint(100000000000000000000000000, 100000000000000000000000000000))


def checkForUpdates():
    repo = g.get_repo("CatGameCreator/HQLauncher")
    release = repo.get_latest_release()
    latest_version = release.tag_name
    print(f"Latest Version is {latest_version}, the current downloaded version is v{version}")
    if Version(version) < Version(latest_version):
        if(query_yes_no("Do you want to update?")):
            print("Updating...")
            asset = release.get_assets()[0]
            download_url = asset.browser_download_url
            response = session.get(download_url, allow_redirects=True)
            assets_path_byte = Path(f"{assets_path}/{asset.name}")
            assets_path_byte.write_bytes(response.content)
            new_version_path = str(assets_path_byte).replace(".zip", "")
            printProgressBar(random.randint(30, 60), 1, prefix='Updating Progress:', suffix='Completed', length=50)
            with zipfile.ZipFile(str(assets_path_byte), 'r') as zip_ref:
                zip_ref.extractall(new_version_path)
            printProgressBar(random.randint(60, 80), 1, prefix='Updating Progress:', suffix='Completed', length=50)
            print("New Version will start soon")
            new_version_exe = str(asset.name).replace("zip", "exe")
            #os.startfile(f"{new_version_exe}")
            latest_version_name = latest_version.replace("v", "")
            version_download_path = os.path.join(f"{assets_path}", f"HQLauncher-{latest_version_name}")
            shutil.move(os.path.join(version_download_path, new_version_exe), file_directory_path)
            print("Closing to restart...")
            f = open("update.bat", "w")
            f.write(f'''move _internal _internal_save
move assets/HQLauncher-{latest_version_name}/_internal
start HQLauncher-{latest_version_name}.exe -update -{version}''')
            f.close()
            os.startfile("update.bat")
            #subprocess.run(['python -c "import os; import time; time.sleep(5); os.rename(' + "'_internal'" + ', ' + "'_internal_save'" + ')"'], shell=True, capture_output=False, text=False)
            #; os.rename(' + f"'assets/HQLauncher-{latest_version_name}/_internal'" + ', ' + "'_internal'" + ')
            sys.exit()
        elif(query_yes_no("Skip update check next time?", default="no")):
            print("You can always go to settings and update there")
            config['DEFAULT']['UpdateCheck'] = "0"
            with open(settings_path, 'w') as configfile:
                config.write(configfile)

def NewVersionUpdate (previous_version):
    for clean_up_file in glob.glob(f'{file_directory_path}/*'):
        if not clean_up_file.title() == f'HQLauncher-{version}.exe':
            if not clean_up_file.title() == f'assets':
                if not clean_up_file.title() == f'_internal':
                    if os.path.isfile(clean_up_file):
                        os.remove(clean_up_file)
                    elif os.path.isdir(clean_up_file):
                        try:
                            os.rmdir(clean_up_file)
                        except OSError as error:
                            shutil.rmtree(clean_up_file)
                    print(f"Deleting: {clean_up_file.title()}")
    version_download_path = os.path.join(f"{assets_path}", f"HQLauncher-{version}")
    file_names = os.listdir(version_download_path)
    for file_name in file_names:
        shutil.move(os.path.join(version_download_path, file_name), file_directory_path)
    os.remove(version_download_path)

def printProgressBar (iteration, total, prefix = '', suffix = '', decimals = 1, length = 100, fill = '█', printEnd = "\r"):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
        printEnd    - Optional  : end character (e.g. "\r", "\r\n") (Str)
    """
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    print(f'\r{prefix} |{bar}| {percent}% {suffix}', end = printEnd)
    # Print New Line on Complete
    if iteration == total:
        print()
def query_yes_no(question, default="yes"):
    """Ask a yes/no question via raw_input() and return their answer.

    "question" is a string that is presented to the user.
    "default" is the presumed answer if the user just hits <Enter>.
            It must be "yes" (the default), "no" or None (meaning
            an answer is required of the user).

    The "answer" return value is True for "yes" or False for "no".
    """
    valid = {"yes": True, "y": True, "ye": True, "no": False, "n": False}
    if default is None:
        prompt = " [y/n] "
    elif default == "yes":
        prompt = " [Y/n] "
    elif default == "no":
        prompt = " [y/N] "
    else:
        raise ValueError("invalid default answer: '%s'" % default)

    while True:
        sys.stdout.write(question + prompt)
        choice = input().lower()
        if default is not None and choice == "":
            return valid[default]
        elif choice in valid:
            return valid[choice]
        else:
            sys.stdout.write("Please respond with 'yes' or 'no' " "(or 'y' or 'n').\n")

def initialize(command = None, command_arg1 = None):
    global minecraft_directory
    global language
    global allow_experimental_settings
    global integrity_check
    global update_check
    global app_config_version
    global config_version
    global current_user_id
    print(command)
    print(command_arg1)
    if(command == "-update"):
        previous_version = command_arg1
        NewVersionUpdate(previous_version)
    if not os.path.exists(assets_path):
        os.makedirs(assets_path)
    if not os.path.isfile(settings_path):
        config['DEFAULT'] = {'MinecraftDirectory': f"{minecraft_directory}",
                             'Language': language,
                             'AllowExperimentalSettings': allow_experimental_settings,
                             'IntegrityCheck': integrity_check,
                             'UpdateCheck': update_check,
                             'ConfigVersion': app_config_version}
        config['EXPERIMENTAL'] = {'UI': "0",
                                  'CustomSkinSystem': "0",
                                  'SpeedrunMode': "0",
                                  'ModpackSupportMode': "0"}
        config['USERS'] = {'CurrentUserID': current_user_id,
                                  'UserSwitchMode': "0"}
        print(f"Your User ID: {current_user_id}")
        with open(settings_path, 'w') as configfile:
            config.write(configfile)
    else:
        config.read(settings_path)
        try:
            config_version = config['DEFAULT']['ConfigVersion']
            minecraft_directory = config['DEFAULT']['MinecraftDirectory']
            language = config['DEFAULT']['Language']
            allow_experimental_settings = config['DEFAULT']['AllowExperimentalSettings']
            integrity_check = config['DEFAULT']['IntegrityCheck']
            update_check = config['DEFAULT']['UpdateCheck']
            current_user_id = config['USERS']['CurrentUserID']
        except:
            if Version(config_version) < Version(app_config_version):
                print("It seems that config version was changed, please visit settings.ini after the update to see if everything is correct")
            else:
                print("It seems the config file was corrupted, try reverting the changes or deleting it. Also please contact support")
    if Version(config_version) < Version(app_config_version):
        #Function for merging two configs new and the old
        pass
    if(int(update_check) == 1):
        checkForUpdates()

if __name__ == "__main__":
    command = None
    command_arg1 = None
    try:
        command = str(sys.argv[1])
        command_arg1 = str(sys.argv[2])
    except:
        print("Staritng with no arguments")
    initialize(command, command_arg1)
