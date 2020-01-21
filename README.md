# dynamic_dock
Dynamic Dock for macOS and munki

***Inspiration (and the framework for this readme!) taken from https://github.com/WardsParadox/dock-maintainer***

## Basic Idea

A script is loaded on every user log in which checks for a group of json files on a server to grab its configuration for the dock.

Manages dock for all users. [docklib](https://github.com/homebysix/docklib/releases) is required. I recommend using this with [Outset](https://github.com/chilcote/outset) and [Munki](https://github.com/munki/munki) (Outset for launching files as needed, Munki for deploying/hosting the `dock` files as it's web server requirements mirror the ones here)

## Deployment:

`dynamic_dock.py` needs to run as a user. I recommend using Outset.  
Deploy `dynamic_dock.py` to `/usr/local/outset/login-every`

I recommend using [Munki-Pkg](https://github.com/munki/munki-pkg) to package it up.

## Edit the url:

```py
dock_url = "https://munki.example.com/dock/" # Path to web server where json files are stored
```

## On the Server

The files on the server should look like this:

```json
{
	"persistent-apps": [
		"/Applications/Launchpad.app",
		"/Applications/Safari.app",
		"/Applications/Firefox.app",
		"/Applications/Microsoft Word.app",
	],
	"persistent-others": [
		"~/Downloads",
		"/Applications"
	]
}
```

A `global.json` file is required. You can also setup docks for the names of any manifests that you have for you machines. For instance, if you have a `music_lab` manifest included in your machines manifest list, you can specify a `music_lab.json` file and it will append to the global app list.

## Roadmap

I'd like to add in order and other options to the json data at some point.
