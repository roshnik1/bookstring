# Bookstring Development
This is the development project for Bookstring.

## Installing
So far I've only tested Bookstring on Ubuntu 20.04 but it should work on most Linux or MacOS environments.

Of course, the first step for the initial install is to clone the repo:

```shell
$ git clone git@github.com:roshnik1/bookstring.git
```

### Server
[Install uv](https://docs.astral.sh/uv/getting-started/installation/#standalone-installer) using the installation script provided by Astral:

```shell
$ curl -LsSf https://astral.sh/uv/install.sh | sh
```

Enter the Bookstring directory and synchronize to create your [uv-managed virtual environment](https://docs.astral.sh/uv/pip/environments/).

```shell
cd bookstring
uv sync
```

You should see the python packages install, if that process completes successfully then everything needed to run the server is ready!

### CLI
Installing the CLI follows the same steps as the server at the moment as they share a uv project and dependencies.

@todo - Currently the CLI is run with `uv run cli`, which is less ergonomic than a system install.

### App
[Install deno](https://docs.deno.com/runtime/getting_started/installation/) using the installation script they provide:

```shell
curl -fsSL https://deno.land/install.sh | sh
```

Enter the app directory and install the typescript dependencies.

```shell
cd bookstring/app
deno install
```

You should see the typescript and javascript packages install, if that process completes successfully then everything needed to run the app is ready!


## Running
The CLI utility can handle running the core parts of Bookstring. However, if desired you can always fall back to the underlying tools (`uv` and `deno`) to run things.

### Server
**With the CLI**

```shell
uv run cli server start
```

**With UV**

```shell
cd server
uv run fastapi dev --port 8181
```

### App
**With the CLI**

```shell
uv run cli app start
```

**With deno**

```shell
cd app
deno run dev --port 8080
```

### Documentation
@todo - documentation building not ready yet

### Checks
@todo - code checks not ready yet


## Development
Useful information for developing in Bookstring.

### Local Dev Sites
  + Server: <http://localhost:8181/>
  + App: <http://localhost:8080/>

### Branches
Since this is (at least for now) just a two-person development project and there's no production deployment to worry about I think we can take advantage of cheap git branches to explore ideas more easily. Here's what I'm thinking:

  + `setup` - This is my branch to handle the initial setup of the project. Once everything is ready for proper development to start it will be merged directly into `main` and then `dev` will be branched off `main`.
  + `main` - The 'canonical' version of the project. We should keep `main` in a stable state (so resolve bugs and skeleton work before merging there) and be relatively conservative about introducing code we aren't sure about there. When there's an actual prod version of the site, this will be the branch we deploy from.
  + `dev` - The development branch, allowed to be a little messy but we do want to fix any bugs that arise here before merging into `main`.
  + `experimental/<idea>` - For speculative concepts that may or may not work out (like this whole declarative project management thing). Experimental branches can break things and even if the idea works out they may not get merged because we want to do it differently when it's 'for real'.
  + `feature/<name>` - For implementing a new feature, something at least somewhat well-defined and that we know we want to include in the full project.
  + `bugfix/<name>` - For fixing a known bug in the code.
  + `cleanup/<name>` - For refactoring, cleaning out old code, or handling other minor chores.
  + `planning/<name>` - For planning project development.
  + `docs/<name>` - For writing and expanding code documentation.

### Project Overview
This is a quick map of the project's directories and what they're for.

  + `app/` - Frontend application code.
  + `cli/` - CLI utility code.
  + `docs/` - Generated documentation XMLs.
  + `project/` - Project management and top-level planning.
  + `server/` - Backend API server code.