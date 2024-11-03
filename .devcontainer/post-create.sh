#!/usr/bin/env bash

mkdir -p /workspaces/scrapers/.vscode
cp /workspaces/scrapers/.devcontainer/vscode/* /workspaces/scrapers/.vscode

make bootstrap
