#!/usr/bin/python

import os
import urllib2
import json
from docklib import Dock

dock_url = "https://munki.example.com/dock/"

def get_applications(dock_name):
    '''
    Returns a dictionary of applications from a file called "dock_name.json"
    '''
    response = urllib2.urlopen('%s%s.json' % (dock_url, dock_name))
    app_json = response.read()
    dock_dict = json.loads(app_json)
    return dock_dict

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
    # Clear the dock
    dock = Dock()

    # Get standard applications
    applications_pa = get_app_list("global","persistent-apps")
    applications_po = get_app_list("global","persistent-others")

    # Check for names of munki manifests
    munki_manifests = get_munki_manifests()

    # Check for existence of dock for manifests
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
                os.path.expanduser(item), arrangement=3, displayas=1, showas=1
            )
        else:
            item = dock.makeDockOtherEntry(
                item, arrangement=3, displayas=1, showas=1
            )
        dock.items["persistent-others"] = [item] + dock.items["persistent-others"]    
    dock.save()

if __name__ == "__main__":
    main()