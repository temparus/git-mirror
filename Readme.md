GitLab-GitHub-sync
==================

This tool synchronizes repositories between GitLab and GitHub. No direct access to the GitLab Server is needed.

## Requirements
* git

## Setup
Just copy the source files to a directory on your machine.

## Configuration File

The default configuration file is `./config.json`. It needs to have the following structure:

```
{
  "name": "Gitlab->GitHub"
  "sync": "public",
  "create": true,
  "source": {
    "type": "gitlab",
    "domain": "gitlab.domain.com",
	"organization": "<gitlab-group",
    "user": "<gitlab-user>",
    "password": "<password>"
  },
  "destination": {
    "type": "github",
	"organization": "<github-organization>",
    "user": "<github-user>",
    "password": "<password>"
  }
}
```

#### Explanation of keys:
* `sync`: specify the repository type to to be synchonized. Possible values: `public`, `internal`, `private`, `all`
* `create`: specify if non-existing repositories should be created at the destination
* `domain`: only needed for type `gitlab`
* `organization`: if this key is missing, the repositories of the specified user are taken.

## Usage
```
usage: gitlab-github-sync.py [-h] [--verbose] [--config config.json] [--version]

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
