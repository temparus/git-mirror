# git-mirror

This tool mirrors repositories between GitLab, GitHub and Bitbucket. No direct access to the GitLab Server is required.

## Requirements

* git
* python 3.x
* pip requirements in `requirements.txt`

## Setup

1. Get source files
    * **Docker** Use the official image (<https://hub.docker.com/r/temparus/git-mirror/>)
    * **Standalone**
      Just clone this repository to a directory on your machine and install the dependencies:
      ```bash
      pip install -r requirements.txt
      ```
2. Run git-mirror once
    * **Docker**
      ```bash
      docker run --volume /path/to/config.json:/git-mirror/config.json \
      temparus/git-mirror:latest --verbose
      ```
    * **Standalone**
      ```bash
      python3 /path/to/git-mirror/git-mirror.py --config /path/to/config.json
      ```
3. Run git-mirror with `Cron`
    * **Docker-Compose**
      Use normal cron notation for the environment variable `GIT_MIRROR_DAEMON`.
      ```yaml
      version: "3"
      services:
        git-mirror:
          image: temparus/git-mirror:latest
          environment:
            - GIT_MIRROR_DAEMON=0 * * * *
          volumes:
            - /path/to/config.json:/git-mirror/config.json
      ```
    * **Standalone** execute `crontab -e` and add the following line there
      ```cron
      0 * * * * python3 /path/to/git-mirror/git-mirror.py --config /path/to/config.json
      ```

## Configuration File

The default configuration file is `./config.json`. It needs to have the following structure:

An example configuration file can be found in the file `config.example.json`.

### Explanation of `hoster` keys

* `domain`: Only needed for type `gitlab`
* `organization`: User namespace is used when this key is missing.

### Explanation of `task` keys

* `sync`: Specify the repository type to to be synchonized.
  Possible values: `all`, `public`, `internal`, `private`, `manual` (default: `manual`)
* `create`: Specify if non-existing repositories should be created at the destination 
  (default: `true`)
* `delete`: Specify if mirrored repositories missing on the source should be deleted 
  at the destination (default: `false`)
* `repositories`: An array of repository names to be synced
  (regardless of the `sync` setting)

## Usage

```bash
usage: git-mirror.py [-h] [--verbose] [--config config.json] [--version]

Synchronizes repositories between GitLab and GitHub.

optional arguments:
  -h, --help            show this help message and exit
  --verbose, -v         prints more output to the console
  --config config.json, -c config.json
                        path to the configuration file
  --version             show program's version number and exit

```

## License

Copyright (C) 2018 Sandro Lutz \<<code@temparus.ch>\>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
