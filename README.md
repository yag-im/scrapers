# scrapers

This project contains scripts for parsing popular games websites.

Currently supporting:

    Adventure Gamers: https://adventuregamers.com/
    IGDB: https://www.igdb.com/
    Lutris: https://lutris.net/games
    MobyGames: https://www.mobygames.com/
    QuestZone: https://questzone.ru/

The resulting output files can be used for internal SQL DB (only IGDB output is in use currently).

## Development

### Prerequisite

Create folder for output data:

    mkdir -p ~/yag/data/scrapers

Generated data is used to initialize the [SQL Database](https://github.com/yag-im/sqldb).

Create `.devcontainer/secrets.env` file:

    IGDB_CLIENT_ID=***VALUE***
    IGDB_CLIENT_SECRET=***VALUE***
    MOBYGAMES_API_KEY=***VALUE***

- retrieve secret values from the relevant websites.

Then simply open this project in any IDE that supports devcontainers (VSCode is recommended).

### Run scrapers

    python run.py --target=igdb --index
