from dashboard.models import Project, Setup


DATA_SOURCES = ['git', 'bugzilla', 'jira', 'phabricator', 'gerrit', 'github',
                'jenkins', 'askbot', 'discourse', 'pipermail', 'stackexchange',
                'slack', 'confluence', 'mediawiki', 'meetup', 'gitlab:issues',
                'gitlab:mrs', 'groupsio']

STUDIES = ['enrich_demography', 'enrich_areas_of_code', 'enrich_onion']


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
    cfg += 'bulk_size = '+setup.bulk_size+'\n'
    cfg += 'scroll_size = '+setup.scroll_size+'\n'

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

    cfg += '\n[panels]\n'
    cfg += 'kibiter_time_from = '+setup.kibiter_time_from+'\n'
    cfg += 'kibiter_default_index = '+setup.kibiter_default_index+'\n'
    cfg += 'kibiter_url = '+setup.kibiter_url+'\n'
    cfg += 'kibiter_version = ' + setup.kibiter_version + '\n'
    cfg += 'community = ' + setup.community + '\n'
    cfg += 'gitlab-issues = ' + setup.gitlab_issues + '\n'
    cfg += 'gitlab-merges = ' + setup.gitlab_merges + '\n'

    backends = setup.backends.all()
    for b in backends:
        backend = setup.backends.get(name=b)
        fields = backend._meta.get_fields()
        cfg += compose_data_source(backend, fields, str(b))

    studies = setup.studies.all()
    for s in studies:
        study = setup.backends.get(name=s)
        fields = study._meta.get_fields()
        cfg += compose_study(study, fields, str(s))

    return cfg


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


def compose_backends():
    html = "<option disabled selected value> -- select a data source -- </option>"
    for ds in DATA_SOURCES:
        html += '<option value="'+ds+'">'+ds+'</option>'

    return html


def compose_studies():
    html = ""
    for s in STUDIES:
        html += '<option value="'+s+'">'+s+'</option>'

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


def compose_study(study, fields, name):
    cfg = '\n['+name+']\n'
    for f in fields:
        field = str(f).split(".")[-1]
        if field == 'in_index' and getattr(study, field) != '':
            cfg += 'in_index = '+study.in_index+'\n'
        elif field == 'out_index' and getattr(study, field) != '':
            cfg += 'out_index = '+study.out_index+'\n'
        elif field == 'data_source' and getattr(study, field) != '':
            cfg += 'data_source = '+study.data_source+'\n'
        elif field == 'contribs_field' and getattr(study, field) != '':
            cfg += 'contribs_field = '+study.contribs_field+'\n'
        elif field == 'timeframe_field' and getattr(study, field) != '':
            cfg += 'timeframe_field = '+study.timeframe_field+'\n'
        elif field == 'sort_on_field' and getattr(study, field) != '':
            cfg += 'sort_on_field = '+study.sort_on_field+'\n'
        elif field == 'no_incremental' and getattr(study, field) != '':
            cfg += 'no_incremental = '+study.no_incremental+'\n'
        elif field == 'seconds' and getattr(study, field) != '':
            cfg += 'seconds = '+study.seconds+'\n'

    return cfg


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
    if setup_table.bulk_size:
        cfg += 'bulk_size: <input id="s_bulk_size" type="text" name="s_bulk_size" value="' + setup_table.bulk_size + '">'
    else:
        cfg += 'bulk_size: <input id="s_bulk_size" type="text" name="s_bulk_size">'
    if setup_table.scroll_size:
        cfg += 'scroll_size: <input id="s_scroll_size" type="text" name="s_scroll_size" value="' + setup_table.scroll_size + '">'
    else:
        cfg += 'scroll_size: <input id="s_scroll_size" type="text" name="s_scroll_size">'
    if setup_table.aliases_file:
        cfg += 'aliases_file: <input id="s_aliases_file" type="text" name="s_aliases_file" value="' + setup_table.aliases_file + '" required="required">'
    else:
        cfg += 'aliases_file: <input id="s_aliases_file" type="text" name="s_aliases_file" value="/home/bitergia/conf/aliases.json" required="required">'

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

    cfg += '<br><br>[panels]<br>'
    if setup_table.kibiter_time_from:
        cfg += 'kibiter_time_from <input id="s_kibiter_time_from" type="text" name="s_kibiter_time_from" value="' + setup_table.kibiter_time_from + '" required="required">'
    else:
        cfg += 'kibiter_time_from <input id="s_kibiter_time_from" type="text" name="s_kibiter_time_from" value="now-90d" required="required">'
    if setup_table.kibiter_default_index:
        cfg += 'kibiter_default_index <input id="s_kibiter_default_index" type="text" name="s_kibiter_default_index" value="' + setup_table.kibiter_default_index + '" required="required">'
    else:
        cfg += 'kibiter_default_index <input id="s_kibiter_default_index" type="text" name="s_kibiter_default_index" value="git" required="required">'
    if setup_table.kibiter_url:
        cfg += 'kibiter_url <input id="s_kibiter_url" type="text" name="s_kibiter_url" value="' + setup_table.kibiter_url + '" required="required">'
    else:
        cfg += 'kibiter_url <input id="s_kibiter_url" type="text" name="s_kibiter_url" value="http://kibiter:5601" required="required">'
    if setup_table.kibiter_version:
        cfg += 'kibiter_version <input id="s_kibiter_version" type="text" name="s_kibiter_version" value="' + setup_table.kibiter_version + '" required="required">'
    else:
        cfg += 'kibiter_version <input id="s_kibiter_version" type="text" name="s_kibiter_version" value="6.1.0-1" required="required">'
    if setup_table.community:
        cfg += 'community <input id="s_community" type="text" name="s_community" value="' + setup_table.community + '" required="required">'
    else:
        cfg += 'community <input id="s_community" type="text" name="s_community" value="true" required="required">'
    if setup_table.gitlab_issues:
        cfg += 'gitlab-issues <input id="s_gitlab_issues" type="text" name="s_gitlab_issues" value="' + setup_table.gitlab_issues + '" required="required">'
    else:
        cfg += 'gitlab-issues <input id="s_gitlab_issues" type="text" name="s_gitlab_issues" value="false" required="required">'
    if setup_table.gitlab_merges:
        cfg += 'gitlab-merges <input id="s_gitlab_merges" type="text" name="s_gitlab_merges" value="' + setup_table.gitlab_merges + '" required="required">'
    else:
        cfg += 'gitlab-merges <input id="s_gitlab_merges" type="text" name="s_gitlab_merges" value="false" required="required">'

    return cfg

