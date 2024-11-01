# scrapers

This project includes scripts for parsing websites of popular adventure games:

    Adventure Gamers: https://adventuregamers.com/
    IGDB: https://www.igdb.com/
    Lutris: https://lutris.net/games
    MobyGames: https://www.mobygames.com/
    QuestZone: https://questzone.ru/

The resulting output files, stored in the data folder, can be used for internal database (currently, only IGDB output is
in use).

## Run

Before opening project in `devcontainer`, create:

    .devcontainer/secrets.env

file containing:

    IGDB_CLIENT_ID=***VALUE***
    IGDB_CLIENT_SECRET=***VALUE***
    MOBYGAMES_API_KEY=***VALUE***
