---
layout: post
title:  "Ubuntu tracker ignore directories"
categories: foss, ubuntu
published: true
---

Today I noticed `tracker-store` was eating a lot of CPU on my machine. So I digged a little into this program to figure out what it's doing. I had no idea on this program, here's how I figured out some things. 

I figured the problem was with some datasets with many files, millions of files, that the indexer was at least looking at, allthough hopefully not reading them, allthough there were `jpg` images in there, perhaps the tracker would actually start indexing some metadata of those. 

So I wanted `tracker` to ignore all directories named `data`, and for good measure, I wanted it to exclude `venv` directories as well, because I have a lot of those for different projects, and they contain a lot of python source files. After some googling, I found out that you can add a `.trackerignore` file to a directory that will work, but I didn't want to start adding this file to all `data` or `venv` directories I will be creating in the feature. 

## 1. The tracker tool

There is a `tracker` tool which can influence some things, for example, you can reset the index and pause the mining process. 

```
usage: tracker [--version] [--help]
               <command> [<args>]

Available tracker commands are:
   daemon    Start, stop, pause and list processes responsible for indexing content
   extract   Extract information from a file
   info      Show information known about local files or items indexed
   index     Backup, restore, import and (re)index by MIME type or file name
   reset     Reset or remove index and revert configurations to defaults
   search    Search for content indexed or show content by type
   sparql    Query and update the index using SPARQL or search, list and tree the ontology
   sql       Query the database at the lowest level using SQL
   status    Show the indexing progress, content statistics and index state
   tag       Create, list or delete tags for indexed content

See “tracker help <command>” to read about a specific subcommand.
```

But I didn't really find what I was looking for here.

## 2. Finding documentation

I found all files this package was using with the following command. 

```
$ dpkg -L tracker
```

This shows many files and directories, among others:

```
/usr/lib/tracker
...
/usr/share/doc/tracker/AUTHORS
/usr/share/doc/tracker/NEWS.gz
/usr/share/doc/tracker/README.md.gz
/usr/share/doc/tracker/copyright
...
/usr/share/glib-2.0/schemas/org.freedesktop.Tracker.gschema.xml
...
```

Some documentation is available in the `README.md` file, which also points to https://wiki.gnome.org/Projects/Tracker/Documentation/GettingStarted. On that link I found you can view the settings with this oneliner. 

## 3. Accessing tracker settings

```
$ gsettings list-recursively | grep -i org.freedesktop.Tracker | sort | uniq
```

Which shows approximately 40 records, among others;

```
org.freedesktop.Tracker.DB journal-chunk-size 50
...
org.freedesktop.Tracker.Miner.Files ignored-directories-with-content ['.trackerignore', '.git', '.hg', '.nomedia']
org.freedesktop.Tracker.Miner.Files ignored-files ['*~', '*.o', '*.la', '*.lo', '*.loT', '*.in', '*.csproj', '*.m4', '*.rej', '*.gmo', '*.orig', '*.pc', '*.omf', '*.aux', '*.tmp', '*.vmdk', '*.vm*', '*.nvram', '*.part', '*.rcore', '*.lzo', 'autom4te', 'conftest', 'confstat', 'Makefile', 'SCCS', 'ltmain.sh', 'libtool', 'config.status', 'confdefs.h', 'configure', '#*#', '~$*.doc?', '~$*.dot?', '~$*.xls?', '~$*.xlt?', '~$*.xlam', '~$*.ppt?', '~$*.pot?', '~$*.ppam', '~$*.ppsm', '~$*.ppsx', '~$*.vsd?', '~$*.vss?', '~$*.vst?', 'mimeapps.list', 'mimeinfo.cache', 'gnome-mimeapps.list', 'kde-mimeapps.list', '*.directory']
org.freedesktop.Tracker.Miner.Files index-on-battery-first-time true
...
```

I wanted tracker to ignore all directories called `data` and `venv`, since these have many files, and they shouldn't be indexed. 

```
$ gsettings get org.freedesktop.Tracker.Miner.Files ignored-directories
```

```
['po', 'CVS', 'core-dumps', 'lost+found']```
```

So finally I added the new entries, and then reset the whole index with the following commands.

## 4. TL;DR

```
$ gsettings set org.freedesktop.Tracker.Miner.Files ignored-directories "['po', 'CVS', 'core-dumps', 'lost+found', 'data', 'venv']"
$ tracker reset -r
```

And I learned more on the wonderful programs that are runnning on my pc. Hope it helps you! 
