"""
Static values used by oGen
"""
# App
VERSION = '0.0.4'
APP_NAME = 'odoo-gen'
TAB_SIZE = 4 # Number of space chars composing a Tab

# Odoo
SUPPORTED_ODOO_VERSIONS = ['15.0', '16.0']
DEF_ODOO_VERSION = '16.0'
DEF_ODOO_REPO = 'https://github.com/odoo/odoo.git'
ODOO_SHALLOW_CLONE = True

# Docker
DEF_DOCKER_COMPOSE_VERSION = '3.9'

# PSQL
DEF_PSQL_VERSION = '14.7'

# Project Structure

# !!! The order of elements in this list is important.
#     E.g. Odoo repo has to cloned before dockerfile is created.
EXPECTED_KEY_PATHS = [
    'odoo',
    'custom_addons',
    'docker_file',
    'docker_compose',
    'env_file',
    'odoo_conf',
    'db_data',
    'odoo_data',
    'conf_dir',
]

DEF_STRUCTURE_YML = 'default.yml'
DEF_PROJECT_STRUCTURE = {
    'odoo': {
        'type': 'dir',
        'repo': 'https://github.com/odoo/odoo.git',
        'key': 'odoo'
    },
    'addons': {
        'type': 'dir',
        'key': 'custom_addons'
    },
    'conf': {
        'type': 'dir',
        'key': 'conf_dir',
        'childs': {
            'odoo.conf': {
                'type': 'file',
                'key': 'odoo_conf',
            }
        }
    },
    'data': {
        'type': 'dir',
        'childs': {
            'db_data': {
                'key': 'db_data',
                'type': 'dir'
            },
            'odoo_data': {
                'key': 'odoo_data',
                'type': 'dir'
            }
        }
    },
    '.env': {
        'type': 'file',
        'key': 'env_file'
    },
    'docker': {
        'type': 'dir',
        'childs': {
            'DOCKERFILE': {
                'type': 'file',
                'key': 'docker_file'
            }
        }
    },
    'docker-compose.yml': {
        'type': 'file',
        'key': 'docker_compose'
    }
}
