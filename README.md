# PlexMusicRatingsSync

This tool bridges the gap between Plex Media Server and your audio files, ensuring your carefully curated ratings are preserved and synchronized between Plex and your preferred music player. Supports various rating schemes including those used by MusicBee, MediaMonkey, Picard, and other popular players or tools.

## Features

- Bidirectional sync between Plex and audio files
- Import and export ratings between Plex and audio files
- Support for both half-star and full-star ratings
- Supports MP3 (ID3v2), FLAC, M4A (AAC/ALAC), OGG, and Opus formats
- Support for multiple Plex music libraries
- Compatible with rating schemes from multiple applications
- Dry-run mode to preview changes without applying them
- Detailed logging with customizable verbosity levels

## User Guide

### CLI

#### Installation (`pipx`)

> [!NOTE]
> It is recommended to use [`pipx`](https://github.com/pypa/pipx#install-pipx) to install PlexMusicRatingsSync, as it allows you to manage Python applications in isolated environments. However, you can also use `pip` directly with or without `venv` if you prefer.

Start by installing the latest version:

```
pipx install PlexMusicRatingsSync
```

Or, install specific a version:

```
pipx install PlexMusicRatingsSync==x.y.z --force
```

And, to upgrade to the latest version:

```
pipx upgrade PlexMusicRatingsSync
```

#### Usage

> [!IMPORTANT]
> The CLI needs direct access to the same file paths as Plex. Ideally, run it on the same machine that hosts Plex. Otherwise, ensure those paths match exactly (e.g., via network shares or mapped drives) so the CLI can properly read and write your audio files.

Start by checking your system information and locating your config file:

```
plex-music-ratings-sync info
```

- This command creates a configuration file (the path is shown in the output) with placeholders and some initial settings. You’ll need to edit that file to add your own values before the script can run properly.

Now you’re ready to run any of the available commands, that you can view with:

```
plex-music-ratings-sync --help
```

  - For detailed information about any specific command, use:

    ```
    plex-music-ratings-sync COMMAND --help
    ```
    
    - Replace `COMMAND` with the command (e.g., `sync`, `import`, `export`) you want to learn more about.

Lastly, **synchronize** ratings between Plex and your audio files with:

```
plex-music-ratings-sync sync
```

  - Or **import** ratings from audio files into Plex with:

    ```
    plex-music-ratings-sync import
    ```

  - Or **export** ratings from Plex to audio files with:

    ```
    plex-music-ratings-sync export
    ```

### Docker Compose

> [!IMPORTANT]  
> When configuring the Docker volumes, both paths on the left side (`/host/app/data` and `/host/plex/music`) must be changed to match your system’s locations. The `/app/data` container path should not be changed. The `/plex/music` container path must match exactly the path that Plex uses to access your audio files.

Start by setting up your `docker-compose.yml` like this:

```yaml
services:
  plex-music-ratings-sync:
    image: ghcr.io/rfgamaral/plex-music-ratings-sync
    container_name: plex-music-ratings-sync
    network_mode: bridge
    restart: on-failure:2
    volumes:
      - /host/app/data:/app/data
      - /host/plex/music:/plex/music
```

- For a specific version (e.g., `1.2.3`):
  - `ghcr.io/rfgamaral/plex-music-ratings-sync:1.2.3`
- For the latest patch of a minor version (e.g., `1.2`):
  - `ghcr.io/rfgamaral/plex-music-ratings-sync:1.2`
- For the latest patch of a major version (e.g., `1`):
  - `ghcr.io/rfgamaral/plex-music-ratings-sync:1`

Then run the following Docker Compose command:

```
docker compose run --rm plex-music-ratings-sync info
```

- This creates a config file with placeholders and initial settings; which you must edit before the script can run. Thanks to the volume mount, it’s saved on your host path (though the container output will show an internal path).

Now you’re ready to run any of the available commands, that you can view with:

```
docker compose run --rm plex-music-ratings-sync --help
```

  - For detailed information about any specific command, use:

    ```
    docker compose run --rm plex-music-ratings-sync COMMAND --help
    ```
    
    - Replace `COMMAND` with the command (e.g., `sync`, `import`, `export`) you want to learn more about.

Lastly, **synchronize** ratings between Plex and your audio files with:

```
docker compose run --rm plex-music-ratings-sync sync
```

  - Or **import** ratings from audio files into Plex with:

    ```
    docker compose run --rm plex-music-ratings-sync import
    ```

  - Or **export** ratings from Plex to audio files with:

    ```
    docker compose run --rm plex-music-ratings-sync export
    ```

### Windows Executable

If you run Plex Server on a Windows computer or even if you run Plex on a NAS and use
a Windows computer, you may find it easier to run PlexMediaRatingsSync on Windows.

You can use PyInstaller to bundle PlexMusicRatingsSync as a standalone Windows executable.

#### Build Instructions

1. Open Windows Sandbox. (optional)
1. Run PowerShell.
1. Allow scripts: `> Set-ExecutionPolicy RemoteSigned -Scope CurrentUser`
1. Install Scoop: `> Invoke-RestMethod get.scoop.sh | Invoke-Expression`
    ```
    Initializing...
    Downloading...
    Extracting...
    Creating shim...
    Adding ~\scoop\shims to your path.
    Scoop was installed successfully!
    Type 'scoop help' for instructions.
    ```
1. Install Python: `> scoop install python`
    ```
    Installing 'dark' (3.14.1) [64bit] from 'main' bucket
    dark-3.14.1.zip (5.0 MB) [====================================================================================] 100%
    Checking hash of dark-3.14.1.zip ... ok.
    Extracting dark-3.14.1.zip ... done.
    Linking ~\scoop\apps\dark\current => ~\scoop\apps\dark\3.14.1
    Creating shim for 'dark'.
    'dark' (3.14.1) was installed successfully!
    Installing 'python' (3.13.5) [64bit] from 'main' bucket
    python-3.13.5-amd64.exe (27.5 MB) [===========================================================================] 100%
    Checking hash of python-3.13.5-amd64.exe ... ok.
    Running pre_install script...done.
    Running installer script...
       [ NOTE: THIS WILL TAKE MINUTES. ]
    Linking ~\scoop\apps\python\current => ~\scoop\apps\python\3.13.5
    Creating shim for 'python3'.
    Creating shim for 'idle'.
    Creating shim for 'idle3'.
    Adding ~\scoop\apps\python\current\Scripts to your path.
    Adding ~\scoop\apps\python\current to your path.
    Persisting Scripts
    Persisting Lib\site-packages
    Running post_install script...
    done.
    'python' (3.13.5) was installed successfully!
    Notes
    -----
    Allow applications and third-party installers to find python by running:
    "C:\Users\WDAGUtilityAccount\scoop\apps\python\current\install-pep-514.reg"
    ```
1. Install PyInstaller: `> python -m pip install pyinstaller`
    ```
    Collecting pyinstaller
      Downloading pyinstaller-6.14.2-py3-none-win_amd64.whl.metadata (8.3 kB)
    Collecting setuptools>=42.0.0 (from pyinstaller)
      Downloading setuptools-80.9.0-py3-none-any.whl.metadata (6.6 kB)
    Collecting altgraph (from pyinstaller)
      Downloading altgraph-0.17.4-py2.py3-none-any.whl.metadata (7.3 kB)
    Collecting pefile!=2024.8.26,>=2022.5.30 (from pyinstaller)
      Downloading pefile-2023.2.7-py3-none-any.whl.metadata (1.4 kB)
    Collecting pywin32-ctypes>=0.2.1 (from pyinstaller)
      Downloading pywin32_ctypes-0.2.3-py3-none-any.whl.metadata (3.9 kB)
    Collecting pyinstaller-hooks-contrib>=2025.5 (from pyinstaller)
      Downloading pyinstaller_hooks_contrib-2025.6-py3-none-any.whl.metadata (16 kB)
    Collecting packaging>=22.0 (from pyinstaller)
      Downloading packaging-25.0-py3-none-any.whl.metadata (3.3 kB)
    Downloading pyinstaller-6.14.2-py3-none-win_amd64.whl (1.4 MB)
       ---------------------------------------- 1.4/1.4 MB 19.3 MB/s eta 0:00:00
    Downloading packaging-25.0-py3-none-any.whl (66 kB)
    Downloading pefile-2023.2.7-py3-none-any.whl (71 kB)
    Downloading pyinstaller_hooks_contrib-2025.6-py3-none-any.whl (440 kB)
    Downloading pywin32_ctypes-0.2.3-py3-none-any.whl (30 kB)
    Downloading setuptools-80.9.0-py3-none-any.whl (1.2 MB)
       ---------------------------------------- 1.2/1.2 MB 19.3 MB/s eta 0:00:00
    Downloading altgraph-0.17.4-py2.py3-none-any.whl (21 kB)
    Installing collected packages: altgraph, setuptools, pywin32-ctypes, pefile, packaging, pyinstaller-hooks-contrib, pyinstaller
    Successfully installed altgraph-0.17.4 packaging-25.0 pefile-2023.2.7 pyinstaller-6.14.2 pyinstaller-hooks-contrib-2025.6 pywin32-ctypes-0.2.3 setuptools-80.9.0
    ```
1. Install the Python requirements: `> python -m pip install -r requirements.txt`
    ```
    Collecting click==8.1.8 (from -r requirements.txt (line 1))
      Downloading click-8.1.8-py3-none-any.whl.metadata (2.3 kB)
    Requirement already satisfied: colorama==0.4.6 in c:\users\wdagutilityaccount\scoop\apps\python\current\lib\site-packages (from -r requirements.txt (line 2)) (0.4.6)
    Collecting filelock==3.17.0 (from -r requirements.txt (line 3))
      Downloading filelock-3.17.0-py3-none-any.whl.metadata (2.9 kB)
    Collecting mutagen==1.47.0 (from -r requirements.txt (line 4))
      Downloading mutagen-1.47.0-py3-none-any.whl.metadata (1.7 kB)
    Collecting platformdirs==4.3.6 (from -r requirements.txt (line 5))
      Downloading platformdirs-4.3.6-py3-none-any.whl.metadata (11 kB)
    Collecting plexapi==4.16.1 (from -r requirements.txt (line 6))
      Downloading PlexAPI-4.16.1-py3-none-any.whl.metadata (9.3 kB)
    Collecting pyyaml==6.0.2 (from -r requirements.txt (line 7))
      Downloading PyYAML-6.0.2-cp313-cp313-win_amd64.whl.metadata (2.1 kB)
    Requirement already satisfied: requests in c:\users\wdagutilityaccount\scoop\apps\python\current\lib\site-packages (from plexapi==4.16.1->-r requirements.txt (line 6)) (2.32.4)
    Requirement already satisfied: charset_normalizer<4,>=2 in c:\users\wdagutilityaccount\scoop\apps\python\current\lib\site-packages (from requests->plexapi==4.16.1->-r requirements.txt (line 6)) (3.4.2)
    Requirement already satisfied: idna<4,>=2.5 in c:\users\wdagutilityaccount\scoop\apps\python\current\lib\site-packages (from requests->plexapi==4.16.1->-r requirements.txt (line 6)) (3.10)
    Requirement already satisfied: urllib3<3,>=1.21.1 in c:\users\wdagutilityaccount\scoop\apps\python\current\lib\site-packages (from requests->plexapi==4.16.1->-r requirements.txt (line 6)) (2.5.0)
    Requirement already satisfied: certifi>=2017.4.17 in c:\users\wdagutilityaccount\scoop\apps\python\current\lib\site-packages (from requests->plexapi==4.16.1->-r requirements.txt (line 6)) (2025.7.14)
    Downloading click-8.1.8-py3-none-any.whl (98 kB)
    Downloading filelock-3.17.0-py3-none-any.whl (16 kB)
    Downloading mutagen-1.47.0-py3-none-any.whl (194 kB)
    Downloading platformdirs-4.3.6-py3-none-any.whl (18 kB)
    Downloading PlexAPI-4.16.1-py3-none-any.whl (165 kB)
    Downloading PyYAML-6.0.2-cp313-cp313-win_amd64.whl (156 kB)
    Installing collected packages: pyyaml, platformdirs, mutagen, filelock, click, plexapi
    Successfully installed click-8.1.8 filelock-3.17.0 mutagen-1.47.0 platformdirs-4.3.6 plexapi-4.16.1 pyyaml-6.0.2
    ```
1. Clone or copy the PMRS project from GitHub.
1. Change to the new project folder: `> cd PlexMusicRatingsSync`
1. Use PyInstaller to bundle a Windows executable: `> pyinstaller --clean pmrs.exe.spec`
    ```
    180 INFO: PyInstaller: 6.14.2, contrib hooks: 2025.6
    180 INFO: Python: 3.13.5
    203 INFO: Platform: Windows-11-10.0.26100-SP0
    203 INFO: Python environment: C:\Users\WDAGUtilityAccount\scoop\apps\python\current
    207 INFO: Removing temporary files and cleaning cache in C:\Users\WDAGUtilityAccount\AppData\Local\pyinstaller
    208 INFO: Module search paths (PYTHONPATH):
    ['C:\\Users\\WDAGUtilityAccount\\scoop\\apps\\python\\current\\Scripts\\pyinstaller.exe',
     'C:\\Users\\WDAGUtilityAccount\\scoop\\apps\\python\\current\\python313.zip',
     'C:\\Users\\WDAGUtilityAccount\\scoop\\apps\\python\\current\\DLLs',
     'C:\\Users\\WDAGUtilityAccount\\scoop\\apps\\python\\current\\Lib',
     'C:\\Users\\WDAGUtilityAccount\\scoop\\apps\\python\\3.13.5',
     'C:\\Users\\WDAGUtilityAccount\\scoop\\apps\\python\\current',
     'C:\\Users\\WDAGUtilityAccount\\scoop\\apps\\python\\current\\Lib\\site-packages',
     'C:\\Users\\WDAGUtilityAccount\\scoop\\apps\\python\\current\\Lib\\site-packages\\setuptools\\_vendor',
     'C:\\Users\\WDAGUtilityAccount\\Desktop\\PlexMusicRatingsSync\\src']
    425 INFO: Appending 'datas' from .spec
    425 INFO: checking Analysis
    ... BLAH BLAH ...
    11359 INFO: checking EXE
    11359 INFO: Building EXE because EXE-00.toc is non existent
    11360 INFO: Building EXE from EXE-00.toc
    11360 INFO: Copying bootloader EXE to C:\Users\WDAGUtilityAccount\Desktop\PlexMusicRatingsSync\dist\pmrs.exe
    11363 INFO: Copying icon to EXE
    11366 INFO: Copying 0 resources to EXE
    11367 INFO: Embedding manifest in EXE
    11369 INFO: Appending PKG archive to EXE
    11374 INFO: Fixing EXE headers
    11424 INFO: Building EXE from EXE-00.toc completed successfully.
    11425 INFO: Build complete! The results are available in: C:\Users\WDAGUtilityAccount\Desktop\PlexMusicRatingsSync\dist
    ```

#### Validate Windows Executable

 1. Sanity test: `> .\dist\pmrs.exe`
    ```
    Usage: pmrs.exe [OPTIONS] COMMAND [ARGS]...

      PlexMusicRatingsSync keeps your Plex music ratings in sync with your audio files

    Options:
      --version  Show program version and exit
      --help     Show this help message and exit

    Commands:
      export  Export ratings from Plex to audio files.
      import  Import ratings from audio files into Plex.
      info    Show system information and configuration paths.
      sync    Synchronize ratings between Plex and supported audio files.
    ```
1. Basic test: `> .\dist\pmrs.exe --version`
    ```
    PlexMusicRatingsSync v1.1.3
    ```
1. Test output: `> .\dist\pmrs.exe --help`
    ```
    Usage: pmrs.exe [OPTIONS] COMMAND [ARGS]...

      PlexMusicRatingsSync keeps your Plex music ratings in sync with your audio
      files

    Options:
      --version  Show program version and exit
      --help     Show this help message and exit

    Commands:
      export  Export ratings from Plex to audio files.
      import  Import ratings from audio files into Plex.
      info    Show system information and configuration paths.
      sync    Synchronize ratings between Plex and supported audio files.
    ```
1. Test bundled configuration file template: `> .\dist\pmrs.exe info`
    ```
    PlexMusicRatingsSync Version: 1.1.3
    Python Version: 3.13.5
    PlexAPI Version: 4.16.1
    Config Directory: C:\Users\WDAGUtilityAccount\AppData\Local\PlexMusicRatingsSync\PlexMusicRatingsSync
    Config File: C:\Users\WDAGUtilityAccount\AppData\Local\PlexMusicRatingsSync\PlexMusicRatingsSync\config.yml
    Log Directory: C:\Users\WDAGUtilityAccount\AppData\Local\PlexMusicRatingsSync\PlexMusicRatingsSync\Logs
    Log File: C:\Users\WDAGUtilityAccount\AppData\Local\PlexMusicRatingsSync\PlexMusicRatingsSync\Logs\PlexMusicRatingsSync.log
    ```
1. If you built in the Windows Sandbox, copy the executable (`.\dist\pmrs.exe`) to the host.

#### Using the Windows Executable

1. Determine path the Plex Server uses to access the music files.
(Substitute your Plex user token for "YOUR_TOKEN" and,
perhaps, the server's IP address for `localhost`.)
    ```powershell
    > python -c "from plexapi.server import PlexServer; `
    baseurl = 'http://localhost:32400'; `
    token   = 'YOUR_TOKEN'; `
    plex    = PlexServer(baseurl, token); `
    print(plex.library.section('Music').locations)"

    ['/volume1/music']
    ```
1. PMRS will access the music files with the same path the Plex Server uses.
You can create a junction point to mirror how the Plex Server accesses the music files.
PMRS uses this to scan your Plex music library. For example, if the Plex Server is
running on a NAS, you might need to do this:
    ```powershell
    > md \volume1
    > mklink /j "\volume1\music" "C:\OneDrive\Music"
    Junction created for D:\volume1\music <<===>> C:\OneDrive\Music
    ```
1. Run PMRS to create the configuration file: `> .\dist\pmrs.exe info`
1. Use the displayed path to edit the configuration file.

### Automated Synchronization

You can automate the synchronization process to run periodically using different methods depending on your installation.

#### Linux (Cron)

If you installed the app via `pipx`, add a cron job to run the sync command:

```
# Edit your crontab
crontab -e

# Add one of these lines:

# Run daily at 03:00
0 3 * * * $HOME/.local/bin/plex-music-ratings-sync sync

# Run weekly on Sunday at 03:00
0 3 * * 0 $HOME/.local/bin/plex-music-ratings-sync sync

# Run monthly on the 1st at 03:00
0 3 1 * * $HOME/.local/bin/plex-music-ratings-sync sync
```

> [!NOTE]
> The command in the example above may not work as-is. Use `which plex-music-ratings-sync` to locate the PlexMusicRatingsSync executable on your system and update the path accordingly.

#### Windows (Task Scheduler)

If you installed the app via `pipx` on Windows, create a scheduled task:

1. Open Task Scheduler
2. Click "Create Basic Task"
3. Set a name and description
4. Choose your trigger (Daily, Weekly, etc.)
5. For the action, select "Start a program"
6. Program/script: `%USERPROFILE%\.local\bin\plex-music-ratings-sync.exe`
7. Arguments: `sync`

#### Docker (Ofelia Scheduler)

If you’re using Docker, you can use set up your `docker-compose.yml` with [Ofelia](https://github.com/mcuadros/ofelia) as a job scheduler. Here’s an example to synchronize ratings between Plex and your audio files every 6 hours:

```yaml

services:
  plex-music-ratings-sync:
    image: ghcr.io/rfgamaral/plex-music-ratings-sync
    container_name: plex-music-ratings-sync
    network_mode: bridge
    command: sync
    restart: on-failure:2
    volumes:
      - /host/app/data:/app/data
      - /host/plex/music:/plex/music
  ofelia-scheduler:
    image: mcuadros/ofelia
    container_name: ofelia-scheduler
    command: daemon --docker
    restart: unless-stopped
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock:ro
    labels:
      ofelia.job-run.plex-music-ratings-sync.schedule: '@every 6h'
      ofelia.job-run.plex-music-ratings-sync.container: 'plex-music-ratings-sync'
```

First, create both services without starting them:

```
docker compose up --no-start
```

Next, start only the `ofelia-scheduler` service:

```
docker compose up ofelia-scheduler
```

> [!NOTE]
> This two-step process ensures that the synchronization runs only at the scheduled times. Alternatively, you can use `docker compose up` to create and start both services simultaneously, which will force an initial run of the synchronization process.

## Frequently Asked Questions

### How do I ensure file paths match between Plex and PlexMusicRatingsSync?

You can verify the correct path in Plex by opening any track in your library, clicking the ⋮ (three dots) menu, selecting "Get Info", and looking at the file path shown. If you have multiple music libraries in different locations, you'll need to define multiple volume mappings.

For Docker users, this path must match the container's `/plex/music` mount point. For CLI users running on a different machine than Plex, ensure the paths are identical through network shares or mapped drives.

### How are ratings synchronized between Plex and audio files?

Plex is treated as the primary source of truth due to technical limitations - neither Plex nor audio files maintain reliable timestamps for rating changes, making it impossible to determine which rating was set most recently.

The synchronization follows these rules:

1. If ratings match: No action needed
2. If ratings differ: Plex’s rating always wins
3. If only one has a rating:
    - Plex rating exists → Update file
    - File rating exists → Update Plex

This ensures your ratings stay consistent while working within the technical constraints of both systems.

## License

The use of this source code is governed by an MIT-style license that can be found in the [LICENSE](LICENSE) file.
