<a name="readme-top"></a>

<br/>

<div align="center">
  <img src="assets/bot_nana_logo.png" alt="logo" height="40%" width="50%"/>
  <br/>

  <h3><b>Tenx Chatbot</b></h3>

</div>

<!-- TABLE OF CONTENTS -->
<br/>

# Contents

- [Contents](#contents)
    - [Setup](#setup)
    - [Install](#install)
- [s3pipeline](#s3pipeline)
  - [Overview](#overview)
  - [Rules and guidelines](#rules-and-guidelines)
  - [How to install dependencies](#how-to-install-dependencies)
  - [How to run your Kedro pipeline](#how-to-run-your-kedro-pipeline)
  - [How to test your Kedro project](#how-to-test-your-kedro-project)
  - [Project dependencies](#project-dependencies)
  - [How to work with Kedro and notebooks](#how-to-work-with-kedro-and-notebooks)
    - [Jupyter](#jupyter)
    - [JupyterLab](#jupyterlab)
    - [IPython](#ipython)
    - [How to convert notebook cells to nodes in a Kedro project](#how-to-convert-notebook-cells-to-nodes-in-a-kedro-project)
    - [How to ignore notebook output cells in `git`](#how-to-ignore-notebook-output-cells-in-git)
  - [Package your Kedro project](#package-your-kedro-project)

### Setup

Clone this repository:

```bash
git clone git@github.com:10xac/tenx-chatbot.git
cd tenx-chatbot
```

Create credentials:

1. Create an environment file and a .credentials folder in the root directory:

```sh
mkdir .credentials
touch .env
```
2. Put your OAuth 2.0 credentials for the data extraction api's in the ".credentials/" folder (JSON)

``` 
.credentails/
        oauth_{extraction_api}.json
```
- Create a credential by looking at the description [here](https://developers.google.com/youtube/registering_an_application)
3. Setup environment variables on `~/.bashrc` or `.env`:

```bash
# Weaviate instance credentials
export WEAVIATE_URL=""
export WEAVIATE_API_KEY=""
export OPENAI_API_KEY=""
export WEAVIATE_MODEL="gpt-3.5-turbo"

# Data extraction API's
export oauth_youtube=""
export oauth_slack=""
export oauth_email=""
export oauth_notion=""
export oauth_gdrive=""

# Tenx aws s3 access keys
export Access_Key_ID=""
export Secret_Access_Key=""
```

## Install
### Build from source

**Run** this to build and run the application:

`(After the build runs use the backend domain 'http://0.0.0.0:8000/docs' to test since the frontend is decoupled.)`

```bash
chmod +x build.sh
./build.sh
```

### Deploy With Docker

**Run** this to build a docker and run the application:

`(After the docker runs use the backend domain 'http://0.0.0.0:8000/docs' to test since the frontend is decoupled.)`

```bash
git clone git@github.com:10xac/tenx-chatbot.git
cd tenx-chatbot
docker-compose up
```
<br/>

<p align="right">(<a href="#readme-top">back to top</a>)</p>

---

# s3pipeline (ingest data to chatbot)

## Overview

This is your new Kedro project, which was generated using `Kedro 0.18.7`.

Take a look at the [Kedro documentation](https://docs.kedro.org) to get started.

## Rules and guidelines

In order to get the best out of the template:

* Don't remove any lines from the `.gitignore` file we provide
* Make sure your results can be reproduced by following a data engineering convention
* Don't commit data to your repository
* Don't commit any credentials or your local configuration to your repository. Keep all your credentials and local configuration in `conf/local/`

## How to install dependencies

Declare any dependencies in `src/requirements.txt` for `pip` installation and `src/environment.yml` for `conda` installation.

To install them, run:

```
cd prompt/extraction
pip install -r src/requirements.txt
```

## How to run your Kedro pipeline

You can run your Kedro project with:

```
kedro run
```

## How to test your Kedro project

Have a look at the file `src/tests/test_run.py` for instructions on how to write your tests. You can run your tests as follows:

```
kedro test
```

To configure the coverage threshold, go to the `.coveragerc` file.

## Project dependencies

To generate or update the dependency requirements for your project:

```
kedro build-reqs
```

This will `pip-compile` the contents of `src/requirements.txt` into a new file `src/requirements.lock`. You can see the output of the resolution by opening `src/requirements.lock`.

After this, if you'd like to update your project requirements, please update `src/requirements.txt` and re-run `kedro build-reqs`.

[Further information about project dependencies](https://docs.kedro.org/en/stable/kedro_project_setup/dependencies.html#project-specific-dependencies)

## How to work with Kedro and notebooks

> Note: Using `kedro jupyter` or `kedro ipython` to run your notebook provides these variables in scope: `context`, `catalog`, and `startup_error`.
>
> Jupyter, JupyterLab, and IPython are already included in the project requirements by default, so once you have run `pip install -r src/requirements.txt` you will not need to take any extra steps before you use them.

### Jupyter
To use Jupyter notebooks in your Kedro project, you need to install Jupyter:

```
pip install jupyter
```

After installing Jupyter, you can start a local notebook server:

```
kedro jupyter notebook
```

### JupyterLab
To use JupyterLab, you need to install it:

```
pip install jupyterlab
```

You can also start JupyterLab:

```
kedro jupyter lab
```

### IPython
And if you want to run an IPython session:

```
kedro ipython
```

### How to convert notebook cells to nodes in a Kedro project
You can move notebook code over into a Kedro project structure using a mixture of [cell tagging](https://jupyter-notebook.readthedocs.io/en/stable/changelog.html#release-5-0-0) and Kedro CLI commands.

By adding the `node` tag to a cell and running the command below, the cell's source code will be copied over to a Python file within `src/<package_name>/nodes/`:

```
kedro jupyter convert <filepath_to_my_notebook>
```
> *Note:* The name of the Python file matches the name of the original notebook.

Alternatively, you may want to transform all your notebooks in one go. Run the following command to convert all notebook files found in the project root directory and under any of its sub-folders:

```
kedro jupyter convert --all
```

### How to ignore notebook output cells in `git`
To automatically strip out all output cell contents before committing to `git`, you can run `kedro activate-nbstripout`. This will add a hook in `.git/config` which will run `nbstripout` before anything is committed to `git`.

> *Note:* Your output cells will be retained locally.

## Package your Kedro project

[Further information about building project documentation and packaging your project](https://docs.kedro.org/en/stable/tutorial/package_a_project.html)
