# Builder helper

Deployer is automated build tool for TennaGraph.

The workflow is following:

1. You build specific apps;

## Prerequisites

* Unix console: Linux, Mac or WSL
* Python 3.7+
* Pipenv
* Minion assumes it is ran from _tennagraphdeploy_ directory and _TennaGraph_ directory with main project is stored one level above, e.g. _tenna_graph_deploy_ and _TennaGraph_ are names exactly like this and placed on the same level.

## Running in interactive mode

`pipenv run python start.py build`


## On-liner

`python start.py build --environment testing --apps app,web --noninteractive`

`python start.py build --environment testing --apps app --noninteractive`

`python start.py build --environment testing --apps web --noninteractive`

