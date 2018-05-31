# Create your views here.

from django.http import HttpResponseRedirect
from django.shortcuts import render

import configparser
import json
import os
import subprocess

import requests

from dashboard.models import DataSource, Project, Repository, Setup, Backends

from dashboard.get_channel_slack import get_channels
from dashboard.get_group_meetup import get_groups
from dashboard.githubsync import GitHubSync
from dashboard.load_projects_json import load_project
from dashboard.load_setup_cfg import load_setup


DATA_SOURCES = ['git', 'bugzilla', 'jira', 'phabricator', 'gerrit', 'github',
                'jenkins', 'askbot', 'discourse', 'pipermail', 'stackexchange',
                'slack', 'confluence', 'mediawiki', 'meetup']


def index(request):
    if request.method == 'GET':

        projects = compose_projects()
        projects = json.dumps(projects, indent=4)
        setup = compose_setup()
        rm_repo = compose_rm_repo()
        setup_form = compose_setup_form()
        rm_backend = compose_rm_backend()
        data_sources = compose_backends()
        dic = {"porjects_table": projects, "setup_cfg": setup,
               "remove_repo": rm_repo, "setup_form": setup_form,
               "rm_backend": rm_backend, "data_sources": data_sources}
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
        return HttpResponseRedirect('http://127.0.0.1:8000/')


def compose_backends():
    html = ""
    for ds in DATA_SOURCES:
        html += '<option value="'+ds+'">'+ds+'</option>'

    return html


def compose_rm_backend():
    html = '<div class ="form-group">'
    html += '<label for="sel1"> Select list (select one):</label>'
    html += '<select class ="form-control" name="rm_ds">'
    try:
        setup_table = Setup.objects.get(name='setup')
        backends = setup_table.backends.all()
        for backend in backends:
            html += '<option value="'+backend.name+'">'+backend.name+'</option>'
    except Setup.DoesNotExist:
        pass
    html += '</select>'
    html += '</div>'

    return html


def compose_rm_repo():
    html = ''
    all_projects = Project.objects.all()
    if len(all_projects) < 0:
        return 'Upload or configure projects.json'
    for p in all_projects:
        project = Project.objects.get(name=p)
        html += '<input type="checkbox" name="remove" value="project '+str(project)+'">'+str(project)+'<br>'
        all_datasources = project.data_source.all()
        for ds in all_datasources:
            html += '&#8195;<input type="checkbox" name="remove" value="datasource '+str(ds)+' '+str(project)+'">'+str(ds)+'<br>'
            data_source = project.data_source.get(parent=p, name=ds)
            all_repos = data_source.repository.all()
            for repos in all_repos:
                html += '&#8195;&#8195;<input type="checkbox" name="remove" value="repository '+str(repos)+' '+str(project)+'">'+str(repos)+'<br>'
            html += '<br>'

    return html


def compose_projects():
    all_projects = Project.objects.all()
    if len(all_projects) < 0:
        return 'Upload or configure projects.json'
    projects = {}
    for p in all_projects:
        projects[str(p)] = {}
        project = Project.objects.get(name=p)
        all_datasources = project.data_source.all()
        for ds in all_datasources:
            projects[str(p)][str(ds)] = {}
            data_source = project.data_source.get(parent=p, name=ds)
            all_repos = data_source.repository.all()
            projects[str(p)][str(ds)] = []
            for repo in all_repos:
                projects[str(p)][str(ds)].append(str(repo).split()[0])

    return projects


def compose_data_source(ds, fields, name):
    cfg = '\n['+name+']\n'
    field_not_valid = ['setup>', 'id', 'name']
    for f in fields:
        field = str(f).split(".")[-1]
        if field == 'latest_items' and getattr(ds, field) != '':
            cfg += 'latest-items = '+ds.latest_items+'\n'
        elif field == 'no_archive' and getattr(ds, field) != '':
            cfg += 'no-archive = '+ds.no_archive+'\n'
        elif field == 'api_token' and getattr(ds, field) != '':
            cfg += 'api-token = '+ds.api_token+'\n'
        elif field == 'sleep_for_rate' and getattr(ds, field) != '':
            cfg += 'sleep-for-rate = '+ds.sleep_for_rate+'\n'
        elif field == 'sleep_time' and getattr(ds, field) != '':
            cfg += 'sleep_time = '+ds.sleep_time+'\n'
        elif field == 'studies' and getattr(ds, field) != '':
            cfg += 'studies = '+ds.studies+'\n'
        elif field not in field_not_valid and getattr(ds, field) != '':
            cfg += field+' = '+getattr(ds, field)+'\n'

    return cfg


def compose_setup():
    try:
        setup = Setup.objects.get(name='setup')
    except Setup.DoesNotExist:
        return 'Upload or configure setup.cfg'

    cfg = '[general]\n'
    cfg += 'short_name = '+setup.short_name+'\n'
    cfg += 'update = '+setup.update+'\n'
    cfg += 'min_update_delay = '+setup.min_update_delay+'\n'
    cfg += 'debug = '+setup.debug+'\n'
    cfg += 'logs_dir = '+setup.logs_dir+'\n'

    cfg += '\n[projects]\n'
    cfg += 'projects_file = '+setup.projects_file+'\n'

    cfg += '\n[es_collection]\n'
    cfg += 'url = '+setup.es_collection+'\n'

    cfg += '\n[es_enrichment]\n'
    cfg += 'url = '+setup.es_enrichment+'\n'
    cfg += 'autorefresh = '+setup.autorefresh+'\n'

    cfg += '\n[sortinghat]\n'
    cfg += 'host = '+setup.host+'\n'
    cfg += 'user = '+setup.user+'\n'
    cfg += 'password = '+setup.password+'\n'
    cfg += 'database = '+setup.database+'\n'
    cfg += 'load_orgs = '+setup.load_orgs+'\n'
    cfg += 'orgs_file = '+setup.orgs_file+'\n'
    cfg += 'autoprofile = '+setup.autoprofile+'\n'
    cfg += 'matching = '+setup.matching+'\n'
    cfg += 'sleep_for = '+setup.sleep_for+'\n'
    cfg += 'bots_names = '+setup.bots_names+'\n'
    cfg += 'unaffiliated_group = '+setup.unaffiliated_group+'\n'
    cfg += 'affiliate = '+setup.affiliate+'\n'

    cfg += '\n[phases]\n'
    cfg += 'collection = '+setup.identities+'\n'
    cfg += 'identities = '+setup.identities+'\n'
    cfg += 'enrichment = '+setup.enrichment+'\n'
    cfg += 'panels = '+setup.panels+'\n'

    backends = setup.backends.all()
    for b in backends:
        backend = setup.backends.get(name=b)
        fields = backend._meta.get_fields()
        cfg += compose_data_source(backend, fields, str(b))
    return cfg


def upload_projects(request):
    if request.method == 'POST':
        try:
            projects_file = request.FILES['projects']
            projects = json.loads(projects_file.read().decode('utf-8'))
            load_project(projects)
        except json.decoder.JSONDecodeError:
            pass

        return HttpResponseRedirect('http://127.0.0.1:8000/')


def is_cfg_file(data):
    try:
        config = configparser.ConfigParser()
        config.read_string(data)
        return True
    except configparser.MissingSectionHeaderError:
        return False


def upload_setup(request):
    if request.method == 'POST':
        try:
            setup_file = request.FILES['setup']
            setup_file = setup_file.read().decode('utf-8')
            load_setup(setup_file)
        except configparser.MissingSectionHeaderError:
            pass

        return HttpResponseRedirect('http://127.0.0.1:8000/')


def add_orgs(request):
    if request.method == 'POST':
        org = request.POST.get("org")
        token = request.POST.get("github_token")
        if org == "":
            return HttpResponseRedirect('http://127.0.0.1:8000/')

        github = GitHubSync(token)
        projects = {}
        try:
            projects = github.sync(projects, org)
            load_project(projects)
        except requests.exceptions.ConnectionError:
            print("Conection ERROR")

        return HttpResponseRedirect('http://127.0.0.1:8000/')


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

        return HttpResponseRedirect('http://127.0.0.1:8000/')


def add_slack(request):
    if request.method == 'POST':
        org = request.POST.get("slack_org_name")
        token = request.POST.get("slack_token")

        if org == "" or token == "":
            return HttpResponseRedirect('http://127.0.0.1:8000/')

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

        return HttpResponseRedirect('http://127.0.0.1:8000/')


def add_meetup(request):
    if request.method == 'POST':
        org = request.POST.get("meetup_org_name")
        topic = request.POST.get("meetup_topic")

        if org == "" or topic == "":
            return HttpResponseRedirect('http://127.0.0.1:8000/')

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

        return HttpResponseRedirect('http://127.0.0.1:8000/')


def conf_setup(request):
    if request.method == 'POST':
        cfg = '[general]\n'
        cfg += 'short_name = ' + str(request.POST.get("s_short_name")) + '\n'
        cfg += 'update = ' + str(request.POST.get("s_update")) + '\n'
        cfg += 'min_update_delay = ' + str(request.POST.get("s_min_update_delay")) + '\n'
        cfg += 'debug = ' + str(request.POST.get("s_debug")) + '\n'
        cfg += 'logs_dir = ' + str(request.POST.get("s_logs_dir")) + '\n'

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

        load_setup(cfg)
    elif request.method == 'GET':
        compose_setup_form()

    return HttpResponseRedirect('http://127.0.0.1:8000/')


def compose_setup_form():
    try:
        setup_table = Setup.objects.get(name='setup')
    except Setup.DoesNotExist:
        setup_table = Setup(name='setup')
        setup_table.save()

    cfg = '[general] <br>'
    if setup_table.short_name:
        cfg += 'short_name: <input id="s_short_name" type="text" name="s_short_name" value="' + setup_table.short_name + '"required="required">'
    else:
        cfg += 'short_name: <input id="s_short_name" type="text" name="s_short_name" required="required">'
    if setup_table.update:
        cfg += 'update: <input id="s_update" type="text" name="s_update" value="' + setup_table.update + '" required="required">'
    else:
        cfg += 'update: <input id="s_update" type="text" name="s_update" value="true" required="required">'
    if setup_table.min_update_delay:
        cfg += 'min_update_delay: <input id="s_min_update_delay" type="text" name="s_min_update_delay" value="' + setup_table.min_update_delay + '" required="required">'
    else:
        cfg += 'min_update_delay: <input id="s_min_update_delay" type="text" name="s_min_update_delay" value="720" required="required">'
    if setup_table.debug:
        cfg += 'debug: <input id="s_debug" type="text" name="s_debug" value="' + setup_table.debug + '" required="required">'
    else:
        cfg += 'debug: <input id="s_debug" type="text" name="s_debug" value="true" required="required">'
    if setup_table.logs_dir:
        cfg += 'logs_dir: <input id="s_logs_dir" type="text" name="s_logs_dir" value="' + setup_table.logs_dir + '" required="required">'
    else:
        cfg += 'logs_dir: <input id="s_logs_dir" type="text" name="s_logs_dir" value="/home/bitergia/logs" required="required">'
    cfg += '<br><br>[projects]<br>'
    if setup_table.projects_file:
        cfg += 'projects_file: <input id="s_projects_file" type="text" name="s_projects_file" value="' + setup_table.projects_file + '" required="required">'
    else:
        cfg += 'projects_file: <input id="s_projects_file" type="text" name="s_projects_file" value="/home/bitergia/conf/sources/projects.json" required="required">'
    cfg += '<br>[es_collection]<br>'
    if setup_table.es_collection:
        cfg += 'url: <input id="s_co_url" type="text" name="s_co_url" value="' + setup_table.es_collection + '" required="required">'
    else:
        cfg += 'url: <input id="s_co_url" type="text" name="s_co_url" value="http://elasticsearch:9200" required="required">'
    cfg += '<br>[es_enrichment]<br>'
    if setup_table.es_enrichment:
        cfg += 'url: <input id="s_en_url" type="text" name="s_en_url" value="' + setup_table.es_enrichment + '" required="required">'
    else:
        cfg += 'url: <input id="s_en_url" type="text" name="s_en_url" value="http://elasticsearch:9200" required="required">'
    if setup_table.autorefresh:
        cfg += 'autorefresh: <input id="s_autorefresh" type="text" name="s_autorefresh" value="' + setup_table.autorefresh + '" required="required">'
    else:
        cfg += 'autorefresh: <input id="s_autorefresh" type="text" name="s_autorefresh" value="true" required="required">'
    cfg += '<br><br>[sortinghat]<br>'
    if setup_table.host:
        cfg += 'host: <input id="s_host" type="text" name="s_host" value="' + setup_table.host + '" required="required">'
    else:
        cfg += 'host: <input id="s_host" type="text" name="s_host" value="mariadb" required="required">'
    if setup_table.user:
        cfg += 'user: <input id="s_user" type="text" name="s_user" value="' + setup_table.user + '" required="required">'
    else:
        cfg += 'user: <input id="s_user" type="text" name="s_user" value="root" required="required">'
    if setup_table.password:
        cfg += 'password: <input id="s_password" type="text" name="s_password" value="' + setup_table.password + '">'
    else:
        cfg += 'password: <input id="s_password" type="text" name="s_password">'
    if setup_table.database:
        cfg += 'database: <input id="s_database" type="text" name="s_database" value="' + setup_table.database + '" required="required">'
    else:
        cfg += 'database: <input id="s_database" type="text" name="s_database" required="required">'
    if setup_table.load_orgs:
        cfg += 'load_orgs: <input id="s_load_orgs" type="text" name="s_load_orgs" value="' + setup_table.load_orgs + '" required="required">'
    else:
        cfg += 'load_orgs: <input id="s_load_orgs" type="text" name="s_load_orgs" required="required">'
    if setup_table.orgs_file:
        cfg += 'orgs_file: <input id="s_orgs_file" type="text" name="s_orgs_file" value="' + setup_table.orgs_file + '" required="required">'
    else:
        cfg += 'orgs_file: <input id="s_orgs_file" type="text" name="s_orgs_file" value="/home/bitergia/conf/orgs_file" required="required">'
    if setup_table.autoprofile:
        cfg += 'autoprofile: <input id="s_autoprofile" type="text" name="s_autoprofile" value="' + setup_table.autoprofile + '" required="required">'
    else:
        cfg += 'autoprofile: <input id="s_autoprofile" type="text" name="s_autoprofile" value="[]" required="required">'
    if setup_table.matching:
        cfg += 'matching: <input id="s_matching" type="text" name="s_matching" value="' + setup_table.matching + '" required="required">'
    else:
        cfg += 'matching: <input id="s_matching" type="text" name="s_matching" value="[email]" required="required">'
    if setup_table.sleep_for:
        cfg += 'sleep_for: <input id="s_sleep_for" type="text" name="s_sleep_for" value="' + setup_table.sleep_for + '" required="required">'
    else:
        cfg += 'sleep_for: <input id="s_sleep_for" type="text" name="s_sleep_for" required="required">'
    if setup_table.bots_names:
        cfg += 'bots_names: <input id="s_bots_names" type="text" name="s_bots_names" value="' + setup_table.bots_names + '" required="required">'
    else:
        cfg += 'bots_names: <input id="s_bots_names" type="text" name="s_bots_names" value="[]" required="required">'
    if setup_table.unaffiliated_group:
        cfg += 'unaffiliated_group: <input id="s_unaffiliated_group" type="text" name="s_unaffiliated_group" value="' + setup_table.unaffiliated_group + '" required="required">'
    else:
        cfg += 'unaffiliated_group: <input id="s_unaffiliated_group" type="text" name="s_unaffiliated_group" value="Unknown" required="required">'
    if setup_table.affiliate:
        cfg += 'affiliate: <input id="s_affiliate" type="text" name="s_affiliate" value="' + setup_table.affiliate + '" required="required">'
    else:
        cfg += 'affiliate: <input id="s_affiliate" type="text" name="s_affiliate" required="required">'
    cfg += '<br><br>[phases]<br>'
    if setup_table.collection:
        cfg += 'collection: <input id="s_collection" type="text" name="s_collection" value="' + setup_table.collection + '" required="required">'
    else:
        cfg += 'collection: <input id="s_collection" type="text" name="s_collection" value="true" required="required">'
    if setup_table.identities:
        cfg += 'identities: <input id="s_identities" type="text" name="s_identities" value="' + setup_table.identities + '" required="required">'
    else:
        cfg += 'identities: <input id="s_identities" type="text" name="s_identities" value="true" required="required">'
    if setup_table.enrichment:
        cfg += 'enrichment: <input id="s_enrichment" type="text" name="s_enrichment" value="' + setup_table.enrichment + '" required="required">'
    else:
        cfg += 'enrichment: <input id="s_enrichment" type="text" name="s_enrichment" value="true" required="required">'
    if setup_table.panels:
        cfg += 'panels: <input id="s_panels" type="text" name="s_panels" value="' + setup_table.panels + '" required="required">'
    else:
        cfg += 'panels: <input id="s_panels" type="text" name="s_panels" value="true" required="required">'

    return cfg


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

    return HttpResponseRedirect('http://127.0.0.1:8000/')


def rm_backend(request):
    if request.method == 'POST':
        name = str(request.POST.get("rm_ds"))
        try:
            ds = Backends.objects.get(name=name)
            ds.delete()
            ds.save()
        except Backends.DoesNotExist:
            print("Data source does not exist: "+name)

    return HttpResponseRedirect('http://127.0.0.1:8000/')


def write_json(filename, data):
    with open(filename, 'w+') as f:
        json.dump(data, f, sort_keys=True, indent=4)


def write_cfg(filename, data):
    config = configparser.ConfigParser()
    config.read_string(data)

    with open(filename, 'w') as configfile:
        config.write(configfile)


def execute_cmd(cmd):
    try:
        subprocess.check_output(cmd, stderr=subprocess.DEVNULL)
        print("\t[OK] "+str(cmd))
    except subprocess.CalledProcessError as e:
        print("\t[ERROR] docker-compose up -d: "+str(e))


def dash_stop(request):
    cwd = os.getcwd()
    if request.method == 'POST':
        path = request.POST.get("path_stop")
        os.chdir(path)
        cmd = ['docker-compose', 'down']
        execute_cmd(cmd)

    os.chdir(cwd)
    return HttpResponseRedirect('http://127.0.0.1:8000/')


def generate_dashboard(request):
    cwd = os.getcwd()
    if request.method == 'POST':
        path = request.POST.get("path")
        projects = compose_projects()
        write_json(path+'/sources/projects.json', projects)
        setup = compose_setup()
        write_cfg(path+'/setup.cfg', setup)

        os.chdir(path)
        cmd = ['docker-compose', 'up', '-d']
        execute_cmd(cmd)

    os.chdir(cwd)
    return HttpResponseRedirect('http://127.0.0.1:8000/')
