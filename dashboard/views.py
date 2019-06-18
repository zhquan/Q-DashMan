# Create your views here.

from django.http import HttpResponseRedirect
from django.shortcuts import render

import configparser
import json
import logging
import os
import subprocess

import requests
import yaml

from dashboard.models import Backends, DataSource, Project, \
    Repository, Studies

from dashboard.compose import compose_backends, compose_projects, \
    compose_rm_backend, compose_rm_repo, compose_setup, compose_setup_form,\
    compose_studies
from dashboard.get_channel_slack import get_channels
from dashboard.get_group_meetup import get_groups
from dashboard.githubsync import GitHubSync
from dashboard.load_projects_json import load_project
from dashboard.load_setup_cfg import load_setup


CONFIGURATION_URL = 'http://127.0.0.1:8000/#configuration'
log_format = "[%(asctime)s - %(levelname)s] %(message)s"
logging.basicConfig(filename="/tmp/qdashman.log", format=log_format, level=logging.INFO)


def index(request):
    if request.method == 'GET':
        projects = compose_projects()
        projects = json.dumps(projects, indent=4)
        setup = compose_setup()
        remove_repo = compose_rm_repo()
        setup_form = compose_setup_form()
        remove_backend = compose_rm_backend()
        data_sources = compose_backends()
        studies = compose_studies()
        dic = {"porjects_table": projects, "setup_cfg": setup,
               "remove_repo": remove_repo, "setup_form": setup_form,
               "rm_backend": remove_backend, "data_sources": data_sources,
               "studies": studies}

        return render(request, 'index.html', dic)


def remove_database(list):
    for l in list:
        data = l.split()
        type = data[0]
        if type == "project":
            project = data[1]
            remove = Project.objects.get(name=project)
        elif type == "datasource":
            ds = data[1]
            parent = data[2]
            remove = DataSource.objects.get(parent=parent, name=ds)
        elif type == "repository":
            repo = data[1]
            parent = data[2]
            remove = Repository.objects.get(parent=parent, name=repo)

        remove.delete()


def rm_repo(request):
    if request.method == 'POST':
        remove_list = request.POST.getlist("remove")
        remove_database(remove_list)
        return HttpResponseRedirect(CONFIGURATION_URL)


# Up Load #
def upload_projects(request):
    if request.method == 'POST':
        try:
            projects_file = request.FILES['projects']
            projects = json.loads(projects_file.read().decode('utf-8'))
            load_project(projects)
        except json.decoder.JSONDecodeError:
            pass

        return HttpResponseRedirect(CONFIGURATION_URL)


def upload_setup(request):
    if request.method == 'POST':
        try:
            setup_file = request.FILES['setup']
            setup_file = setup_file.read().decode('utf-8')
            load_setup(setup_file)
        except configparser.MissingSectionHeaderError:
            pass

        return HttpResponseRedirect(CONFIGURATION_URL)


def is_cfg_file(data):
    try:
        config = configparser.ConfigParser()
        config.read_string(data)
        return True
    except configparser.MissingSectionHeaderError:
        return False


# Add #
def add_orgs(request):
    if request.method == 'POST':
        org = request.POST.get("org")
        token = request.POST.get("github_token")
        if org == "":
            return HttpResponseRedirect(CONFIGURATION_URL)

        github = GitHubSync(token)
        projects = {}
        try:
            projects = github.sync(projects, org)
            load_project(projects)
        except requests.exceptions.ConnectionError:
            print("Conection ERROR")

        return HttpResponseRedirect(CONFIGURATION_URL)


def add_repo(request):
    if request.method == 'POST':
        org = request.POST.get("org_manual")
        ds = request.POST.get("ds_manual")
        repo = request.POST.get("repo_manual")
        projects = {
            org: {
                ds: [
                    repo
                ]
            }
        }
        load_project(projects)

        return HttpResponseRedirect(CONFIGURATION_URL)


def add_slack(request):
    if request.method == 'POST':
        org = request.POST.get("slack_org_name")
        token = request.POST.get("slack_token")

        if org == "" or token == "":
            return HttpResponseRedirect(CONFIGURATION_URL)

        url = 'https://slack.com/api/channels.list?token=' + token + '&pretty=1'
        try:
            channels = get_channels(url)
            projects = {
                org: {
                    "slack": channels
                }
            }

            load_project(projects)
        except requests.exceptions.ConnectionError:
            print("Conection ERROR")

        return HttpResponseRedirect(CONFIGURATION_URL)


def add_meetup(request):
    if request.method == 'POST':
        org = request.POST.get("meetup_org_name")
        topic = request.POST.get("meetup_topic")

        if org == "" or topic == "":
            return HttpResponseRedirect(CONFIGURATION_URL)

        try:
            groups = get_groups(topic)
            projects = {
                org: {
                    "meetup": groups
                }
            }

            load_project(projects)
        except requests.exceptions.ConnectionError:
            print("Conection ERROR")

        return HttpResponseRedirect(CONFIGURATION_URL)


# CONF #
def conf_setup(request):
    if request.method == 'POST':
        cfg = '[general]\n'
        cfg += 'short_name = ' + str(request.POST.get("s_short_name")) + '\n'
        cfg += 'update = ' + str(request.POST.get("s_update")) + '\n'
        cfg += 'min_update_delay = ' + str(request.POST.get("s_min_update_delay")) + '\n'
        cfg += 'debug = ' + str(request.POST.get("s_debug")) + '\n'
        cfg += 'logs_dir = ' + str(request.POST.get("s_logs_dir")) + '\n'
        cfg += 'bulk_size = ' + str(request.POST.get("s_bulk_size")) + '\n'
        cfg += 'scroll_size = ' + str(request.POST.get("s_scroll_size")) + '\n'
        cfg += 'aliases_file = ' + str(request.POST.get("s_aliases_file")) + '\n'

        cfg += '[projects]\n'
        cfg += 'projects_file = ' + str(request.POST.get("s_projects_file")) + '\n'

        cfg += '[es_collection]\n'
        cfg += 'url = ' + str(request.POST.get("s_co_url")) + '\n'

        cfg += '[es_enrichment]\n'
        cfg += 'url = ' + str(request.POST.get("s_en_url")) + '\n'
        cfg += 'autorefresh = ' + str(request.POST.get("s_autorefresh")) + '\n'

        cfg += '[sortinghat]\n'
        cfg += 'host = ' + str(request.POST.get("s_host")) + '\n'
        cfg += 'user = ' + str(request.POST.get("s_user")) + '\n'
        cfg += 'password = ' + str(request.POST.get("s_password")) + '\n'
        cfg += 'database = ' + str(request.POST.get("s_database")) + '\n'
        cfg += 'load_orgs = ' + str(request.POST.get("s_load_orgs")) + '\n'
        cfg += 'orgs_file = ' + str(request.POST.get("s_orgs_file")) + '\n'
        cfg += 'autoprofile = ' + str(request.POST.get("s_autoprofile")) + '\n'
        cfg += 'matching = ' + str(request.POST.get("s_matching")) + '\n'
        cfg += 'sleep_for = ' + str(request.POST.get("s_sleep_for")) + '\n'
        cfg += 'bots_names = ' + str(request.POST.get("s_bots_names")) + '\n'
        cfg += 'unaffiliated_group = ' + str(request.POST.get("s_unaffiliated_group")) + '\n'
        cfg += 'affiliate = ' + str(request.POST.get("s_affiliate")) + '\n'

        cfg += '[phases]\n'
        cfg += 'collection = ' + str(request.POST.get("s_collection")) + '\n'
        cfg += 'identities = ' + str(request.POST.get("s_identities")) + '\n'
        cfg += 'enrichment = ' + str(request.POST.get("s_enrichment")) + '\n'
        cfg += 'panels = ' + str(request.POST.get("s_panels")) + '\n'

        cfg += '[panels]\n'
        cfg += 'kibiter_time_from = ' + str(request.POST.get("s_kibiter_time_from")) + '\n'
        cfg += 'kibiter_default_index = ' + str(request.POST.get("s_kibiter_default_index")) + '\n'
        cfg += 'kibiter_url = ' + str(request.POST.get("s_kibiter_url")) + '\n'
        cfg += 'kibiter_version = ' + str(request.POST.get("s_kibiter_version")) + '\n'
        cfg += 'community = ' + str(request.POST.get("s_community")) + '\n'
        cfg += 'gitlab-issues = ' + str(request.POST.get("s_gitlab_issues")) + '\n'
        cfg += 'gitlab-merges = ' + str(request.POST.get("s_gitlab_merges")) + '\n'

        load_setup(cfg)
    elif request.method == 'GET':
        compose_setup_form()

    return HttpResponseRedirect(CONFIGURATION_URL)


def conf_backend(request):
    if request.method == 'POST':
        backend = '['+request.POST.get("s_data_source")+']\n'
        backend += 'raw_index = '+request.POST.get("s_raw_index")+'\n'
        backend += 'enriched_index = '+request.POST.get("s_enriched_index")+'\n'
        backend += 'no-archive = '+request.POST.get("s_no_archive")+'\n'
        backend += 'api-token = '+request.POST.get("s_api_token")+'\n'
        backend += 'sleep_time = '+request.POST.get("s_sleep_time")+'\n'
        backend += 'sleep-for-rate = '+request.POST.get("s_sleep_for_rate")+'\n'
        backend += 'studies = '+request.POST.get("s_studies")+'\n'
        backend += 'latest-items = '+request.POST.get("s_latest_items")+'\n'
        load_setup(backend)

    return HttpResponseRedirect(CONFIGURATION_URL)


def conf_study(request):
    if request.method == 'POST':
        study = '['+request.POST.get("s_study")
        study += ':'+request.POST.get("s_data_source_study")
        study += ']\n'
        study += 'in_index = '+request.POST.get("s_in_index")+'\n'
        study += 'out_index = '+request.POST.get("s_out_index")+'\n'
        study += 'data_source = '+request.POST.get("s_data_source_s")+'\n'
        study += 'contribs_field = '+request.POST.get("s_contribs_field")+'\n'
        study += 'timeframe_field = '+request.POST.get("s_timeframe_field")+'\n'
        study += 'sort_on_field = '+request.POST.get("s_sort_on_field")+'\n'
        study += 'no_incremental = '+request.POST.get("s_no_incremental")+'\n'
        study += 'seconds = '+request.POST.get("s_seconds")+'\n'
        load_setup(study)

    return HttpResponseRedirect(CONFIGURATION_URL)


# REMOVE #
def rm_backend(request):
    if request.method == 'POST':
        name = str(request.POST.get("rm_ds"))
        try:
            ds = Backends.objects.get(name=name)
            ds.delete()
            ds.save()
        except Backends.DoesNotExist:
            print("Data source does not exist: "+name)

    return HttpResponseRedirect(CONFIGURATION_URL)


def rm_study(request):
    if request.method == 'POST':
        name = str(request.POST.get("rm_study"))
        try:
            s = Studies.objects.get(name=name)
            s.delete()
            s.save()
        except Studies.DoesNotExist:
            print("Study does not exist: "+name)

    return HttpResponseRedirect(CONFIGURATION_URL)


# WRITE #
def write_json(filename, data):
    with open(filename, 'w+') as f:
        json.dump(data, f, sort_keys=True, indent=4)


def write_cfg(filename, data):
    """ Write setup.cfg

    :param filename: file name
    :param data: data
    """
    config = configparser.ConfigParser()
    config.read_string(data)

    with open(filename, 'w') as configfile:
        config.write(configfile)


def execute_cmd(cmd):
    """ Execute command

    :param cmd: command
    """
    try:
        subprocess.check_output(cmd, stderr=subprocess.DEVNULL)
        print("\t[OK] {}".format(cmd))
    except subprocess.CalledProcessError as e:
        print("\t[ERROR] {}: {}".format(cmd, e))


# GENERATE DASHBOARD #
def dash_stop(request):
    cwd = os.getcwd()
    if request.method == 'POST':
        path = request.POST.get("path_stop")
        os.chdir(path)
        cmd = ['docker-compose', 'down']
        execute_cmd(cmd)

    os.chdir(cwd)
    return HttpResponseRedirect(CONFIGURATION_URL)


def create_docker_mordred(path, version):
    docker_compose = {
        "redis": {
            "image": "redis"
        },
        "mordred": {
            "restart": "on-failure:5",
            "image": "bitergia/mordred:" + version,
            "volumes": [
                path + ":/home/bitergia/conf",
                path + "/logs:/home/bitergia/logs",
                path + "/perceval-cache/:/home/bitergia/.perceval"
            ],
            "links": [
                "redis"
            ],
            "external_links": [
                "mariadb_mariadb_1:mariadb",
                "elastic_elasticsearch_1:elasticsearch",
                "elastic_kibiter_1:kibiter"
            ],
            "log_driver": "json-file",
            "log_opt": {
                "max-size": "100m",
                "max-file": "3"
            }
        }
    }

    file_name = path+'/docker-compose.yml'
    write_compose_yml(file_name, docker_compose)


def write_compose_yml(file_name, data):
    with open(file_name, 'w') as f:
        yaml.dump(data, f, default_flow_style=False)
    print("[OK] {} created".format(file_name))


def up_docker_compose(mordred_path):
    cwd = os.getcwd()
    elastic_path = cwd + "/elastic"
    elastic_cmd = ['docker-compose', '-f', elastic_path + "/docker-compose.yml", 'up', '-d']
    execute_cmd(elastic_cmd)

    mariadb_path = cwd + "/mariadb"
    mariadb_cmd = ['docker-compose', '-f', mariadb_path + "/docker-compose.yml", 'up', '-d']
    execute_cmd(mariadb_cmd)

    create_docker_mordred(mordred_path, "grimoirelab-0.2.24")
    mordred_cmd = ['docker-compose', '-f', mordred_path + "/docker-compose.yml", 'up', '-d']
    execute_cmd(mordred_cmd)


def generate_dashboard(request):
    if request.method == 'POST':
        path = request.POST.get("path")
        if not os.path.exists(path):
            os.makedirs(path)
            os.makedirs(path + "/sources")
            os.makedirs(path + "/logs")
            os.makedirs(path + "/perceval-cache")
            print("[OK] {} created".format(path))
            print("[OK] {}/sources created".format(path))
        projects = compose_projects()
        write_json(path+'/sources/projects.json', projects)
        print("[OK] " + path + "/sources/projects.json created")
        setup = compose_setup()
        write_cfg(path+'/setup.cfg', setup)
        print("[OK] " + path + "/setup.cfg created")

        up_docker_compose(path)


    return HttpResponseRedirect('http://127.0.0.1:8000/')
