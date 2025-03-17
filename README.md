# scrapers

This project contains scripts for extracting data from popular gaming websites by parsing HTML files or utilizing
official APIs (e.g. [IGDB API](https://api-docs.igdb.com/)).

Currently supporting:

    Adventure Gamers: https://adventuregamers.com/
    IGDB: https://www.igdb.com/
    Lutris: https://lutris.net/games
    MobyGames: https://www.mobygames.com/
    QuestZone: https://questzone.ru/

The generated data files are used to initialize the [SQL DB](https://github.com/yag-im/sqldb).
Currently, only the IGDB output is utilized for SQL DB initialization.

## Development

### Prerequisite

Ensure that a data directory is available for storing the generated data:

    ~/yag/data/scrapers

This directory will be mounted within the devcontainer as `/mnt/data`.

Create a `.devcontainer/secrets.env` file (obtain the secret values from the respective websites):

    IGDB_CLIENT_ID=***VALUE***
    IGDB_CLIENT_SECRET=***VALUE***
    MOBYGAMES_API_KEY=***VALUE***

Next, open this project in any IDE that supports devcontainers (VSCode is recommended).

### Run

Scrape index of a specific website:

    python run.py --target=igdb --index

This will generate several CSV files in the `/mnt/data/igdb` directory, which can be used to initialize the SQL DB
during local system setup.

Get game info:

    python run.py --target=igdb --game=217940
