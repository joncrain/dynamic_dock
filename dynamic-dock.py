#!/usr/bin/python

import stat
import os
import json
import sys
from docklib import Dock

try:
    from urllib.request import urlopen  # Python 3
    from urllib.error import HTTPError, URLError
except ImportError:
    from urllib2 import urlopen, HTTPError, URLError  # Python 2

dock_url = "https://domain.org/dock/"
dock_backup = "/Users/Shared/dock/"
if not os.path.exists(dock_backup):
    os.makedirs(dock_backup)
    os.chmod(dock_backup, 0o777)


def get_applications(dock_name):
    """
    Returns a dictionary of applications from a file called "dock_name.json"
    """
    try:
        response = urlopen("%s%s.json" % (dock_url, dock_name))
        backup_file = "%s%s.json" % (dock_backup, dock_name)
        if not os.path.exists(backup_file):
            f = open(backup_file, "w")
            f.close()
            os.chmod(backup_file, 0o777)
        f = open(backup_file, "w")
        app_json = response.read()
        f.write(app_json)
        f.close()
        dock_dict = json.loads(app_json)
    except HTTPError:
        """
        404 connection error - 
        The json for this manifest doesn't exist
        """
        dock_dict = {}
        pass
    except URLError:
        """
        Most likely we have lost connection
        so we will fall back to the standard dock
        """
        f = open("%s%s.json" % (dock_backup, dock_name), "r")
        app_json = f.read()
        dock_dict = json.loads(app_json)
    except Exception as e:
        print(e)
    return dock_dict


def backup_dock(dock_name):
    """
    Create a backup of the dock files in case the machine or server goes offline
    """
    response = urlopen("%s%s.json" % (dock_url, dock_name))
    return response


def get_munki_manifests():
    """
    Returns a list of munki_manifests
    """
    manifests = "/Library/Managed Installs/manifests"
    munki_manifests = []
    for manifest in os.listdir(manifests):
        munki_manifests.append(manifest)
    return munki_manifests


def get_app_list(target, key):
    """
    Returns a list of applications from target
    """
    target_dock_dict = get_applications(target)
    target_applications = target_dock_dict[key]
    return target_applications


def main():
    """
    Run the program
    """

    dock = Dock()
    if dock.mod_count > 3:
        sys.exit()

    applications_pa = []
    applications_po = []
    # Get standard applications
    try:
        applications_pa = get_app_list("global_staff", "persistent-apps")
        applications_po = get_app_list("global_staff", "persistent-others")
    except:
        pass

    # Check for names of munki manifests
    munki_manifests = get_munki_manifests()

    # Check for existence of dock for manifests and clear if one doesn't want global
    for munki_manifest in munki_manifests:
        try:
            if get_app_list(munki_manifest, "use-global") is False:
                applications_pa = []
                applications_po = []
        except:
            pass

    # Add the applications
    for munki_manifest in munki_manifests:
        try:
            applications_pa = applications_pa + get_app_list(
                munki_manifest, "persistent-apps"
            )
            applications_po = applications_po + get_app_list(
                munki_manifest, "persistent-others"
            )
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
            item = dock.makeDockOtherEntry(item, arrangement=1, displayas=1, showas=3)
        dock.items["persistent-others"] = [item] + dock.items["persistent-others"]
    dock.save()


if __name__ == "__main__":
    main()
