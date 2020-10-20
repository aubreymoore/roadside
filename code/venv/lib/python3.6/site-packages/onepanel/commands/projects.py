""" Command line interface for the OnePanel Machine Learning platform

'ProjectViewControllers' commands group.
"""

import os
import re

import click
import configobj

from onepanel.commands.base import APIViewController
from onepanel.commands.login import login_required


class ProjectViewController(APIViewController):
    """ ProjectViewControllers data model
    """

    PROJECT_FILE = os.path.join('.onepanel','project')
    EXCLUSIONS = [os.path.join('.onepanel','project')]

    account_uid = None
    project_uid = None

    def __init__(self, conn):
        APIViewController.__init__(self, conn)


    def init_credentials_retrieval(self):
        home = os.getcwd()
        onepanel_dir = os.path.join(home, '.onepanel')
        if not os.path.exists(onepanel_dir):
            print("ERROR.Directory does not exist, cannot carry out all projects operations.")
            print("DETAILS." + onepanel_dir)
            exit(-1)
        project_file = os.path.join(home, ProjectViewController.PROJECT_FILE)
        if not os.path.isfile(project_file):
            print("ERROR.Project file does not exist, cannot carry out all projects operations.")
            print("DETAILS." + project_file)
            exit(-1)

        cfg = configobj.ConfigObj(project_file)
        project_account_uid = cfg['account_uid']
        project_uid = cfg['uid']

        if len(project_account_uid) < 1:
            print("ERROR.Project file has invalid credentials. Verify credentials or re-pull project.")
            exit(-1)
        self.account_uid = project_account_uid
        self.project_uid = project_uid

    def save(self, home):
        if not os.path.exists(home):
            os.makedirs(home)
        onepanel_dir = os.path.join(home, '.onepanel')
        if not os.path.exists(onepanel_dir):
            os.makedirs(onepanel_dir)
        project_file = os.path.join(home, ProjectViewController.PROJECT_FILE)

        cfg = configobj.ConfigObj(project_file)
        cfg['uid'] = self.project_uid
        cfg['account_uid'] = self.account_uid
        cfg.write()

    @classmethod
    def from_json(cls, data):
        cls.account_uid = data['account']['uid']
        cls.project_uid = data['uid']

    @classmethod
    def from_directory(cls, home):
        if not cls.exists_local(home):
            print("ERROR.Cannot find path.")
            print("DETAILS."+home)
            exit(-1)

        project_file = os.path.join(home, ProjectViewController.PROJECT_FILE)
        cfg = configobj.ConfigObj(project_file)
        cls.account_uid = cfg['account_uid']
        cls.project_uid = cfg['uid']

    @classmethod
    def is_uid_valid(cls,uid):
        pattern = re.compile('^[a-z0-9][-a-z0-9]{1,23}[a-z0-9]$')
        if pattern.match(uid):
            return True
        else:
            return False

    @classmethod
    def exists_local(cls,home):
        project_file = os.path.join(home, cls.PROJECT_FILE)
        if os.path.isfile(project_file):
            return True
        else:
            return False

    @classmethod
    def exists_remote(cls,project_uid, data):
        exists = False
        if data is None:
            return exists
        if data['uid'] == project_uid:
            exists = True
        return exists


def create_project(ctx, account_uid, home):
    """ Project creation method for 'projects_init' and 'projects_create'
    commands
    """
    vc = ctx.obj['vc']

    if not account_uid:
        account_uid = ctx.obj['connection'].account_uid

    project_uid = os.path.basename(home)
    if not vc.is_uid_valid(project_uid):
        click.echo('Project name {} is invalid.'.format(project_uid))
        click.echo(
            'Name should be 3 to 25 characters long, lower case alphanumeric or \'-\' and must start and end with an alphanumeric character.')
        return False

    url_project_check = '/accounts/{}/projects/{}'.format(account_uid, project_uid)
    response = vc.get(params=url_project_check, uid='', field_path='')
    remote_project = response['data']

    if vc.exists_remote(project_uid, remote_project):
        if vc.exists_local(home):
            click.echo('Project is already created.')
        else:
            vc.account_uid = account_uid
            vc.project_uid = project_uid
            vc.save(home)
            return True
    else:
        if vc.exists_local(home):
            click.echo('Project already exists locally. Switch to the project local directory and use "onepanel projects init" to create it remotely.')
            return False

        data = {
            'uid': project_uid
        }
        url_project_create = '/accounts/{}/projects'.format(account_uid)
        response = vc.post(data, params=url_project_create)
        if response['status_code'] == 200:
            vc.from_json(response['data'])
            vc.save(home)
            return True

    return False


@click.group(help='Project commands')
@click.pass_context
def projects(ctx):
    ctx.obj['vc'] = ProjectViewController(ctx.obj['connection'])


@projects.command('list', help='Display a list of all projects.')
@click.pass_context
@login_required
def projects_list(ctx):
    vc = ctx.obj['vc']
    data = vc.list(params='/projects')
    empty_message = "No projects found"
    items = []
    if data is not None:
        items = data['data']
    vc.print_items(
        items,
        fields=['uid', 'instanceCount', 'jobCount'],
        field_names=['NAME', 'INSTANCES', 'JOBS'],
        empty_message=empty_message
    )

@projects.command('init', help='Initialize project in current directory.')
@click.pass_context
@login_required
def projects_init(ctx):
    home = os.getcwd()
    vc = ctx.obj['vc']

    name = os.path.basename(home)
    if not vc.is_uid_valid(os.path.basename(home)):
        name = click.prompt('Please enter a valid project name')
        home = os.path.join(home, name)

    if create_project(ctx, None, home):
        account_uid = ctx.obj['connection'].account_uid
        click.echo('Project is initialized in current directory and created remotely at "{account_uid}/{name}".'
            .format(account_uid=account_uid, name=name))


@projects.command('create', help='Create project in new directory.')
@click.argument('name', default="", type=str)
@click.pass_context
@login_required
def projects_create(ctx, name):
    if name == "":
        name = click.prompt("Enter project name", type=str)
    home = os.path.join(os.getcwd(), name)
    if create_project(ctx, None, home):
        account_uid = ctx.obj['connection'].account_uid
        click.echo('Project is created in directory "{home}" locally and remotely at "{account_uid}/{project_uid}".'
            .format(home=home, account_uid=account_uid, project_uid=name))

@projects.command('clone', help='Clone a project from Onepanel.')
@click.argument('path', default="", type=str)
@click.argument('directory', default=None, type=str, required=False)
@click.pass_context
@login_required
def projects_clone(ctx, path, directory):
    vc = ctx.obj['vc']

    values = path.split('/')
    if len(values) == 3:
        try:
            account_uid, projects_dir, project_uid = values
            assert (projects_dir == 'projects')
        except:
            click.echo('Invalid project path. Please use <account_uid>/projects/<project_uid>')
            return
    else:
        click.echo('Invalid project path. Please use <account_uid>/projects/<project_uid>')
        return

    # check project path, account_uid, project_uid
    if directory is None:
        home = os.path.join(os.getcwd(), project_uid)
    elif directory == '.':
        home = os.getcwd()
    else:
        home = os.path.join(os.getcwd(), directory)

    # check if the project exists
    url_project_check = '/accounts/{}/projects/{}'.format(account_uid, project_uid)
    response = vc.get(params=url_project_check,uid="",field_path='')
    response_code = response['status_code']
    if response_code == 200:
        remote_project = response['data']
    elif response_code == 401 or response_code == 404:
        print('Project does not exist.')
        return
    else:
        print('Error: {}'.format(response_code))
        return

    if not vc.exists_remote(project_uid, remote_project):
        click.echo('Project {}/projects/{} does not exist.'.format(account_uid, project_uid))
        return

    if vc.exists_local(home):
        click.echo('Directory already exists, please use a different target directory.')
        return

    vc.account_uid = account_uid
    vc.project_uid = project_uid
    vc.save(home)
