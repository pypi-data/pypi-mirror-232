"""
DockerFile generator class
"""

import os
import platform

from ..constants import TAB_SIZE


class DockerFile:
    """
    DockerFile generator class
    """

    odoo_version: str
    file_content: str
    last_indent: int
    key_paths: dict

    def __init__(self, odoo_version, key_paths):
        self.odoo_version = odoo_version
        self.key_paths = key_paths
        self.file_content = ''
        self.last_indent = 0

    def _al(self, content: str, indent: int = False) -> str:
        """
        Adds line to an existing string

        Args:
            content (str): content to be added.
            indent (int): Indent. Defaults to False. Accepted values are:
                -1 to reduce indent by one tab
                1 to increase the indent
                0 to removes the indent
                False keeps the same indent

        Returns:
            str: Resulted string.
        """
        ind = self.last_indent

        if indent is not False and indent == 0:
            ind = 0

        if indent in [-1, 1]:
            ind = self.last_indent + indent
            ind = 0 if ind < 0 else ind  # ! Ensure >=0

        ind_content = ' ' * ind * TAB_SIZE
        self.last_indent = ind

        prefix = os.linesep if self.file_content else ''

        self.file_content += prefix + ind_content + content

    def _add_spacer(self) -> None:
        self._al('', 0)

    def _add_header_part(self) -> None:
        self._al('FROM python:3.11.5-bookworm')
        self._al('SHELL ["/bin/bash", "-xo", "pipefail", "-c"]')

        self._add_spacer()

        self._al('ENV LANG C.UTF-8')

        self._add_spacer()

    def _add_sys_dependencies(self) -> None:
        self._al('RUN apt-get update \\', 0)
        self._al('&& apt-get install -y --no-install-recommends \\', indent=1)

        deps = [
            'ca-certificates',      'curl',
            'dirmngr',              'fonts-noto-cjk',
            'gnupg',                'libssl-dev',
            'node-less',            'npm',
            'python3-num2words',    'python3-pdfminer',
            'python3-pip',          'python3-phonenumbers',
            'python3-pyldap',       'python3-qrcode',
            'python3-renderpm',     'python3-setuptools',
            'python3-slugify',      'python3-vobject',
            'python3-watchdog',     'python3-xlrd',
            'python3-xlwt',         'xz-utils',
            'build-essential',      'libmagic1',
            'python3-dev',          'libc6-dev',
            'libffi-dev',           'zlib1g',
            'zlib1g-dev',           'libxml2',
            'libxml2-dev',          'libxslt1-dev',
            'libsasl2-dev',         'libldap2-dev',
            'libx11-dev',           'fontconfig',
            'libfreetype6-dev',     'libxrender-dev',
            'libxtst-dev',          'libbz2-dev',
            'libfontconfig1-dev',   'fonts-crosextra-carlito',
            'cargo',                'libpq-dev',
        ]

        ind = 1
        for dep in deps:
            self._al(f'{dep} \\', indent=ind)
            ind = False

        wk_urls = {
            'x86_64': {
                'checksum': 'e9f95436298c77cc9406bd4bbd242f4771d0a4b2',
                'url': 'https://github.com/wkhtmltopdf/packaging/releases/'
                        'download/0.12.6.1-3/wkhtmltox_0.12.6.1-3.bookworm_amd64.deb'
            },
            'arm': {
                'checksum': '77bc06be5e543510140e6728e11b7c22504080d4',
                'url': 'https://github.com/wkhtmltopdf/packaging/releases/'
                        'download/0.12.6.1-3/wkhtmltox_0.12.6.1-3.bookworm_arm64.deb'
            },
            'i386': {
                'checksum': '4bc83b4e45224000813c81ce6b52732565cb293e',
                'url': 'https://github.com/wkhtmltopdf/packaging/releases/'
                        'download/0.12.6.1-3/wkhtmltox_0.12.6.1-3.bookworm_i386.deb'
            },
        }

        # Determine CPU type and fallback on amd64 if not valid
        cpu_arch = platform.processor()
        if not isinstance(cpu_arch, str) or cpu_arch not in wk_urls:
            cpu_arch = 'x86_64'

        wk_url = wk_urls[cpu_arch]['url']
        wk_chk = wk_urls[cpu_arch]['checksum']

        self._al(f'&& curl -o wkhtmltox.deb -sSL {wk_url} \\', -1)
        self._al(f"&& echo '{wk_chk} wkhtmltox.deb' | sha1sum -c - \\")
        self._al("&& apt-get install -y --no-install-recommends ./wkhtmltox.deb \\")
        self._al("&& rm -rf /var/lib/apt/lists/* wkhtmltox.deb")

        self._add_spacer()

    def _add_install_rust(self) -> None:
        self._al("RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs"
                 " | bash -s -- -y", 0)
        self._add_spacer()

    def _add_install_pg_client(self):
        self._al('# Install latest postgresql-client', 0)
        self._al("RUN echo 'deb http://apt.postgresql.org/pub/repos/apt/ "
                 "bookworm-pgdg main' > /etc/apt/sources.list.d/pgdg.list \\", 0)
        self._al('&& GNUPGHOME="$(mktemp -d)" \\', 1)
        self._al('&& export GNUPGHOME \\')
        self._al("&& repokey='B97B0AFCAA1A47F044F244A07FCC7D46ACCC4CF8' \\")
        self._al('&& gpg --batch --keyserver keyserver.ubuntu.com '
                 '--recv-keys "${repokey}" \\')
        self._al('&& gpg --batch --armor --export "${repokey}" '
                 '> /etc/apt/trusted.gpg.d/pgdg.gpg.asc \\')
        self._al('&& gpgconf --kill all \\')
        self._al('&& rm -rf "$GNUPGHOME" \\')
        self._al('&& apt-get update  \\')
        self._al('&& apt-get install --no-install-recommends -y postgresql-client \\')
        self._al('&& rm -f /etc/apt/sources.list.d/pgdg.list \\')
        self._al('&& rm -rf /var/lib/apt/lists/*')
        self._add_spacer()

    def _add_rtlcss(self) -> None:
        # Install rtlcss
        # RUN npm install -g rtlcss
        self._al('# Install rtlcss', 0)
        self._al('RUN npm install -g rtlcss', 0)
        self._add_spacer()

    def _add_user(self):
        self._al('# Create odoo user', 0)
        self._al('RUN useradd -ms /bin/bash -d /var/lib/odoo odoo \\', 0)
        self._al('&& apt-get update \\', 1)
        self._al('&& apt-get install -y locales \\')
        self._al('&& locale-gen "en_US.UTF-8" # Fix broken locales')
        self._add_spacer()

    def _add_pip_requirements(self) -> None:
        """
        Populates the docker file with instructions
        to install specific pip libraries.
        """

        # Determine the path to odoo and custom_addons folders
        # and check if they contain a requirements.txt file.
        project_path = self.key_paths.get('project', '')
        odoo_path = self.key_paths.get('odoo', '').replace(project_path, '.')
        addons_path = self.key_paths.get('custom_addons', '')
        addons_req_exists = os.path.exists(
            os.path.join(addons_path, 'requirements.txt'))

        if not odoo_path:
            return

        self._al(
            f'COPY {odoo_path}/requirements.txt /tmp/odoo_requirements.txt', 0)

        if addons_req_exists:
            addons_path = addons_path.replace(project_path, '.')
            self._al(
                f'COPY {addons_path}/requirements.txt /tmp/addons_requirements.txt', 0)

        self._add_spacer()
        self._al('RUN pip3 install --upgrade pip \\', 0)
        self._al('&& pip3 install wheel \\', 1)
        self._al('&& pip3 install setuptools_rust \\')
        self._al('&& pip3 install -r /tmp/odoo_requirements.txt \\')
        if addons_req_exists:
            self._al('&& pip3 install -r /tmp/addons_requirements.txt \\')
        self._al('&& rm -rf /tmp/*requirements*.txt')

        self._add_spacer()

    def _add_init_scripts(self):
        project_path = self.key_paths.get('project', '')
        docker_file_path = self.key_paths.get('docker_file', '')

        docker_path = os.path.dirname(
            docker_file_path).replace(project_path, '.')

        self._al(f'COPY --chown=odoo:odoo {docker_path}/wait-for-psql.py '
                 '/usr/local/bin/wait-for-psql.py', 0)
        self._al(
            f'COPY --chown=odoo:odoo {docker_path}/entrypoint.sh /entrypoint.sh', 0)
        self._add_spacer()
        self._al('RUN chmod +x /entrypoint.sh', 0)
        self._add_spacer()

    def _add_ending_part(self) -> None:
        self._al('# Set the default config file', 0)
        self._al('ENV ODOO_RC /etc/odoo/odoo.conf', 0)
        self._add_spacer()

        self._al('VOLUME ["/var/lib/odoo", "/mnt/addons"]', 0)
        self._add_spacer()

        self._al('# Expose Odoo services', 0)
        self._al('EXPOSE 8069 8071 8072', 0)
        self._add_spacer()

        self._al('# Set default user when running the container', 0)
        self._al('USER odoo', 0)
        self._add_spacer()

        self._al('ENTRYPOINT ["/entrypoint.sh"]', 0)
        self._al('CMD ["odoo"]', 0)
        self._add_spacer()

    def get_content(self) -> str:
        """
        Aggregates and returns the content of the dockerfile based on specific Odoo version

        Returns:
            str: Content of the dockerfile
        """
        self._add_header_part()
        self._add_sys_dependencies()
        self._add_install_rust()
        self._add_install_pg_client()
        self._add_rtlcss()
        self._add_user()
        self._add_pip_requirements()
        self._add_init_scripts()
        self._add_ending_part()

        return self.file_content

    @staticmethod
    def get_entrypoint_content() -> str:
        """
        Returns the content of the entrypoint.sh file
        to be placed inside the docker folder.
        """
        return r"""#!/bin/bash

set -e

if [ -v PASSWORD_FILE ]; then
    PASSWORD="$(< $PASSWORD_FILE)"
fi

# set the postgres database host, port, user and password according to the environment
# and pass them as arguments to the odoo process if not present in the config file
: ${HOST:=${DB_PORT_5432_TCP_ADDR:='db'}}
: ${PORT:=${DB_PORT_5432_TCP_PORT:=5432}}
: ${USER:=${DB_ENV_POSTGRES_USER:=${POSTGRES_USER:='odoo'}}}
: ${PASSWORD:=${DB_ENV_POSTGRES_PASSWORD:=${POSTGRES_PASSWORD:='odoo'}}}

DB_ARGS=()
function check_config() {
    param="$1"
    value="$2"
    if grep -q -E "^\s*\b${param}\b\s*=" "$ODOO_RC" ; then       
        value=$(grep -E "^\s*\b${param}\b\s*=" "$ODOO_RC" |cut -d " " -f3|sed 's/["\n\r]//g')
    fi;
    DB_ARGS+=("--${param}")
    DB_ARGS+=("${value}")
}
check_config "db_host" "$HOST"
check_config "db_port" "$PORT"
check_config "db_user" "$USER"
check_config "db_password" "$PASSWORD"

case "$1" in
    -- | odoo)
        shift
        if [[ "$1" == "scaffold" ]] ; then
            exec python3 /mnt/odoo/odoo-bin "$@"
        else
            python3 /usr/local/bin/wait-for-psql.py ${DB_ARGS[@]} --timeout=30
            exec python3 /mnt/odoo/odoo-bin "$@" "${DB_ARGS[@]}"
        fi
        ;;
    -*)
        python3 /usr/local/bin/wait-for-psql.py ${DB_ARGS[@]} --timeout=30
        exec python3 /mnt/odoo/odoo-bin "$@" "${DB_ARGS[@]}"
        ;;
    *)
        exec "$@"
esac

exit 1
"""

    @staticmethod
    def get_wait_sql_content() -> str:
        """
        Returns the content of the entrypoint.sh file
        to be placed inside the docker folder.
        """
        return r"""#!/usr/bin/env python3

import argparse
import psycopg2
import sys
import time


if __name__ == '__main__':
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('--db_host', required=True)
    arg_parser.add_argument('--db_port', required=True)
    arg_parser.add_argument('--db_user', required=True)
    arg_parser.add_argument('--db_password', required=True)
    arg_parser.add_argument('--timeout', type=int, default=5)

    args = arg_parser.parse_args()

    start_time = time.time()
    while (time.time() - start_time) < args.timeout:
        try:
            conn = psycopg2.connect(user=args.db_user, host=args.db_host, port=args.db_port, password=args.db_password, dbname='postgres')
            error = ''
            break
        except psycopg2.OperationalError as e:
            error = e
        else:
            conn.close()
        time.sleep(1)

    if error:
        print("Database connection failure: %s" % error, file=sys.stderr)
        sys.exit(1)
"""
