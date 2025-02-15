# PlexMusicRatingsSync

This tool bridges the gap between Plex Media Server and your audio files, ensuring your carefully curated ratings are preserved and synchronized between Plex and your preferred music player. Supports various rating schemes including those used by MusicBee, MediaMonkey, Picard, and other popular players or tools.

## Features

- Bidirectional sync between Plex and audio files
- Import and export ratings between Plex and audio files
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
