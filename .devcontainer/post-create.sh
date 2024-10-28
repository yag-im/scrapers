#!/usr/bin/env bash

mkdir -p /workspaces/scrapers/.vscode
cp /workspaces/scrapers/.devcontainer/artifacts/vscode/* /workspaces/scrapers/.vscode

make bootstrap
