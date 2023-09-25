# SyncDir

SyncDir is a program that synchronises two folders: source and replica.

## Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install syncdirs.

```bash
pip install syncdirs
```

## Usage

```bash
$ syncdirs -h
usage: syncdirs [-h] [--logfile LOGFILE] [--interval INTERVAL] SOURCE REPLICA

Periodical synchronization of 2 folders

positional arguments:
  SOURCE               The path to the source file or directory
  REPLICA              The path to the replica file or directory

options:
  -h, --help           show this help message and exit
  --logfile LOGFILE    Name of a log file. Default is syncdir.log
  --interval INTERVAL  Interval of synchronization in seconds. Default is 60s
```
