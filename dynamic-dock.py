#!/usr/bin/python

import stat
import os
import urllib2
import json
import sys
from docklib import Dock
from Foundation import CFPreferencesCopyAppValue

dock_url = "https://munki.example.org/dock/"
dock_backup = "/Users/Shared/dock/"
if not os.path.exists(dock_backup):
    os.makedirs(dock_backup)
    os.chmod(dock_backup, 0o777 )

def get_applications(dock_name):
    '''
    Returns a dictionary of applications from a file called "dock_name.json"
    '''
    try:
        response = urllib2.urlopen('%s%s.json' % (dock_url, dock_name))
        backup_file = '%s%s.json' % (dock_backup, dock_name)
        if not os.path.exists(backup_file):
            f = open(backup_file, "w")
            f.close()
            os.chmod(backup_file, 0o777 )
        f = open(backup_file, "w")
        app_json = response.read()
        f.write(app_json)
        f.close()
        dock_dict = json.loads(app_json)
    except urllib2.HTTPError as err:
        '''
        404 connection error - 
        The json for this manifest doesn't exist
        '''
        pass
    except urllib2.URLError as err:
        '''
        Most likely we have lost connection
        so we will fall back to the standard dock
        '''
        f = open('%s%s.json' % (dock_backup, dock_name), "r")
        app_json = f.read()
        dock_dict = json.loads(app_json)
    except Exception as e:
        print(e)
    return dock_dict

def dock_altered():
    '''
    Checking to see if dock has been altered by user returns False if mod-count < 3
    '''
    plist_to_check = "com.apple.dock.plist"
    check = CFPreferencesCopyAppValue("mod-count", plist_to_check)
    if check <  3: 
        altered = False
    else:
        altered = True
    return altered

def backup_dock(dock_name):
    '''
    Create a backup of the dock files in case the machine or server goes offline
    '''
    response = urllib2.urlopen('%s%s.json' % (dock_url, dock_name))
    return response

def get_munki_manifests():
    '''
    Returns a list of munki_manifests
    '''
    manifests = "/Library/Managed Installs/manifests"
    munki_manifests = []            
    for manifest in os.listdir(manifests):
        munki_manifests.append(manifest)
    return munki_manifests

def get_app_list(target,key):
    '''
    Returns a list of applications from target
    '''
    target_dock_dict = get_applications(target)
    target_applications = target_dock_dict[key]
    return target_applications

def main():
    '''
    Run the program
    '''
    if dock_altered() == True:
        sys.exit()

    # Clear the dock
    dock = Dock()
    global_clear = []
    applications_pa = []
    applications_po = []
    # Get standard applications
    try:
        applications_pa = get_app_list("global","persistent-apps")
        applications_po = get_app_list("global","persistent-others")
    except:
        pass
    
    # Check for names of munki manifests
    munki_manifests = get_munki_manifests()

    # Check for existence of dock for manifests and clear if one doesn't want global
    for munki_manifest in munki_manifests:
        try:
            if get_app_list(munki_manifest,"use-global") == False:
                applications_pa = []
                applications_po = []
        except:
            pass

    # Add the applications
    for munki_manifest in munki_manifests:
        try:
            applications_pa = applications_pa + get_app_list(munki_manifest,"persistent-apps")
            applications_po = applications_po + get_app_list(munki_manifest,"persistent-others")
        except:
            pass

    # Iterate over applications
    dock.items["persistent-apps"] = []
    for item in applications_pa:
        if os.path.exists(item):
            item = dock.makeDockAppEntry(item)
            dock.items["persistent-apps"].append(item)

    # iterate over others
    dock.items["persistent-others"] = []
    for item in applications_po:
        if "~" in item:
            item = dock.makeDockOtherEntry(
                os.path.expanduser(item), arrangement=1, displayas=1, showas=3
            )
        else:
            item = dock.makeDockOtherEntry(
                item, arrangement=1, displayas=1, showas=3
            )
        dock.items["persistent-others"] = [item] + dock.items["persistent-others"]    
    dock.save()

if __name__ == "__main__":
    main()