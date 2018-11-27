import os
import sys
import subprocess
import click

VALID_APPS = ['app', 'web']
VALID_ENVIRONMENTS = ['testing']
GIT_EXECUTABLE = os.getenv('GIT_EXECUTABLE', 'git')
ENVIRONMENTS = {
    'testing': {
        'head_title': 'Tenna Graph',
        'head_description': 'Tenna Graph',
    },
}


@click.group(chain=True)
def cli():
    """Automcatically build & deploy TennaGraph"""


@click.command()
@click.option('--environment', default='testing',
              type=click.Choice(VALID_ENVIRONMENTS),
              help="Environment to deploy: %s" % ', '.join(VALID_ENVIRONMENTS),
              prompt="Environment to deploy: %s" % ', '.join(VALID_ENVIRONMENTS))
@click.option('--apps', default='all',
              help="Apps to build: %s" % ', '.join(VALID_APPS),
              prompt="Apps to build: %s, use commas for multiple" % ', '.join(VALID_APPS))
@click.option('--details/--no-details', default=False, help='Show detailed output')
@click.option('--interactive/--noninteractive', default=False, help='Enabled/Disabled interactive prompts')
def build(environment, apps, details, interactive):
    """Build microservices into Docker images"""
    apps_list = apps.split(',')
    # click.clear()

    if 'all' in apps_list:
        warning = 'Building all apps make take a few minutes.'
        click.echo(click.style(warning, fg='yellow'))
        if not interactive:
            build_app(environment, details=details)
            build_web(environment, details=details)
        else:
            # Changing abort to True will abort whole program execution
            if click.confirm('Do you want to continue?', abort=False):
                build_app(environment, details=details)
                build_web(environment, details=details)
    else:
        for app in apps_list:
            if app not in VALID_APPS:
                raise click.ClickException("Invalid app %s" % app)
            if not interactive:
                getattr(sys.modules[__name__], "build_%s" % app)(environment, details=details)
            else:
                if click.confirm("Do you want to continue building %s?" % app):
                    getattr(sys.modules[__name__], "build_%s" % app)(environment, details=details)
    # click.pause()

cli.add_command(build)


def build_app(environment, *args, **kwargs):
    details = __details_helper(kwargs)
    click.echo(click.style("Building 'app'", blink=True, bold=True))
    if 'app_path' in kwargs:
        app_path = kwargs['app_path']
    else:
        app_path = os.path.abspath(os.path.join('.', os.pardir, 'TennaGraph', 'app'))

    version_path = os.path.join(app_path, 'VERSION')
    version_file = open(version_path, 'r')
    version = version_file.readline()

    cmd = "cd %s; /bin/sh bin/release.sh" % app_path
    build_result = subprocess.check_output(cmd, shell=True)
    if details:
        click.echo(click.style(build_result.decode('utf-8'), fg='magenta'))

    new_version_file = open(version_path, 'r')
    new_version = new_version_file.readline()
    if new_version == version:
        raise click.ClickException("App build failed, staying at version %s" % version)

    click.echo(click.style("Successfully built App version %s" % new_version, fg='green'))


def build_web(environment, *args, **kwargs):
    details = __details_helper(kwargs)
    click.echo(click.style("Building 'web'", blink=True, bold=True))
    if 'app_path' in kwargs:
        app_path = kwargs['app_path']
    else:
        app_path = os.path.abspath(os.path.join('.', os.pardir, 'TennaGraph', 'web'))

    version_path = os.path.join(app_path, 'VERSION')
    version_file = open(version_path, 'r')
    version = version_file.readline()

    api_base = ENVIRONMENTS[environment]['api_base']
    head_title = ENVIRONMENTS[environment]['head_title']
    head_description = ENVIRONMENTS[environment]['head_description']
    
    cmd = 'cd %s; API_BASE_URL=%s HEAD_TITLE=%s HEAD_DESCRIPTION=%s /bin/sh bin/release.sh' % (app_path, head_title, head_description, api_base)
    build_result = subprocess.check_output(cmd, shell=True)
    
    if details:
        click.echo(click.style(build_result.decode('utf-8'), fg='magenta'))

    new_version_file = open(version_path, 'r')
    new_version = new_version_file.readline()
    if new_version == version:
        raise click.ClickException("Web build failed, staying at version %s" % version)

    click.echo(click.style("Successfully built Web version %s" % new_version, fg='green'))



def __details_helper(kwargs):
    if 'details' in kwargs and kwargs['details']:
        return True
    return False


def __write_build_version(file_path, identifier, version):
    """Update Kubernetes config file with new image version"""

    with open(file_path) as fp:
        lines = fp.readlines()

    new_lines = []
    for line in lines:
        if line.find(identifier) > -1:
            parts = line.split(identifier)
            parts[-1] = version + '\n'
            new_line = identifier.join(parts)
            new_lines.append(new_line)
        else:
            new_lines.append(line)

    fp2 = open(file_path, 'w')
    fp2.write(''.join(new_lines))
    fp2.close()


if __name__ == '__main__':
    cli()
