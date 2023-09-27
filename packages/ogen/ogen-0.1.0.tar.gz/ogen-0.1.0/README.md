# odoo-gen
Project Generator helping Odoo developers to manage and run their projects.

## Installation

```shell
git clone https://github.com/cix-code/odoo-gen
cd odoo-gen

# Create a dedicated python environment
python3 -m venv venv

venv/bin/pip install -e .
ln -s ~/[path_to_odoo-gen]/venv/bin/ogen ~/.local/bin

```

## Usage

### Create a new project

If this is the first time creating a project, navigate to a folder that you'd like to be a workspace for multiple projects. E.g.

```shell
mkdir ~/odoo_projects
cd ~/odoo_projects
```

Create the project

```shell
ogen create name_your_project
```

### Control the Odoo instance
Run the Odoo instance

```shell
ogen start name_your_project
```
then open http://localhost:8069 .

Stop the project

```shell
ogen stop
```

For more commands run

```shell
ogen --help
```

## Configuration

The generator will create a config file under `[user_config_path]/odoo-gen/ogen.conf`.
It will prompt the you to confirm the workspace folder.
