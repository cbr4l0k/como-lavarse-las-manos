# Snoo.py

_Our solution has been tested in linux only, so we recommend sticking to this operating systems, particularly in arch based distributions, this should also work without effort in other kinds of linux
distributions._

## Table of contents
- [Run project](#run-project)
- [Requirements](#requirements)
- [Installation and setup](#installation-and-setup)
    - [Enviroment variables](#environment-variables)


## Run project 

This is how you can run our project:

```python 
python3 src/snoo.py
```

## Requirements
- Python 3.11 or higher.
- Nodejs.
- JavaScript D3 _(version 7.85)_.
- tree _(version v2.1.1)_.

## Installation and setup
```bash
git clone github.com/cbr4lok/como-lavarse-las-manos.git
cd como-lavarse-las-manos
python -m venv venv 
source ./venv/bin/activate
pip install -r requirements.txt
```

### Environment variables


| Field Name       | Explaination                                                   |
|------------------|----------------------------------------------------------------|
| OUTPUTS_PATH     | `Folder containing the outputs`  |
| PROJECTS_PATH    | `Folder containing the projects that are available for analys. Insert yours here.`|
| OPEN_AI_API_KEY  | `Insert your secret OpenAI api key here.`|
| DEFAULT_LLM      | `Add the default model to use when using the model. This could be one of the OpenAI models like 'gpt-3.5-turbo' or 'gpt-3.5-turbo-16k' our preffered option is 'gpt-3.5-turbo-16k'.` |


