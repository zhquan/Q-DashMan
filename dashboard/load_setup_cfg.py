import configparser

from dashboard.models import Setup, Backends, Studies


STUDIES = ["enrcih_demography", "enrich_onion", "enrich_areas_of_code"]


def __add_general(config, setup_table, section):
    setup_table.short_name = config[section]['short_name']
    setup_table.update = config[section]['update']
    setup_table.min_update_delay = config[section]['min_update_delay']
    setup_table.debug = config[section]['debug']
    setup_table.logs_dir = config[section]['logs_dir']
    setup_table.bulk_size = config[section]['bulk_size']
    setup_table.scroll_size = config[section]['scroll_size']
    setup_table.aliases_file = config[section]['aliases_file']
        

def __add_projects(config, setup_table, section):
    setup_table.projects_file = config[section]['projects_file']


def __add_sortinghat(config, setup_table, section):
    setup_table.host = config[section]['host']
    setup_table.user = config[section]['user']
    setup_table.password = config[section]['password']
    setup_table.database = config[section]['database']
    setup_table.load_orgs = config[section]['load_orgs']
    setup_table.orgs_file = config[section]['orgs_file']
    setup_table.autoprofile = config[section]['autoprofile']
    setup_table.matching = config[section]['matching']
    setup_table.sleep_for = config[section]['sleep_for']
    setup_table.bots_names = config[section]['bots_names']
    setup_table.unaffiliated_group = config[section]['unaffiliated_group']
    setup_table.affiliate = config[section]['affiliate']


def __add_backend(config, setup_table, section):
    try:
        backend_table = Backends.objects.get(name=section)
    except Backends.DoesNotExist:
        backend_table = Backends(name=section)

    for key in config[section]:
        val = config[section][key]
        if key == 'raw_index':
            backend_table.raw_index = val
        if key == 'enriched_index':
            backend_table.enriched_index = val
        if key == 'no-archive':
            backend_table.no_archive = val
        if key == 'api-token':
            backend_table.api_token = val
        if key == 'sleep_time':
            backend_table.sleep_time = val
        if key == 'latest-items':
            backend_table.latest_items = val
        if key == 'studies':
            backend_table.studies = val
        if key == 'sleep-for-rate':
            backend_table.sleep_for_rate = val

    backend_table.save()
    setup_table.backends.add(backend_table)


def __add_study(config, setup_table, section):
    try:
        study_table = Studies.objects.get(name=section)
    except Studies.DoesNotExist:
        study_table = Studies(name=section)

    for key in config[section]:
        val = config[section][key]
        if key == 'in_index':
            study_table.in_index = val
        if key == 'out_index':
            study_table.out_index = val
        if key == 'data_source_s':
            study_table.data_source = val
        if key == 'contribs_field':
            study_table.contribs_field = val
        if key == 'timeframe_field':
            study_table.timeframe_field = val
        if key == 'sort_on_field':
            study_table.sort_on_field = val
        if key == 'no_incremental':
            study_table.no_incremental = val
        if key == 'seconds':
            study_table.seconds = val

    study_table.save()
    setup_table.backends.add(study_table)


def __add_phases(config, setup_table, section):
    setup_table.collection = config[section]['collection']
    setup_table.enrichment = config[section]['enrichment']
    setup_table.identities = config[section]['identities']
    setup_table.panels = config[section]['panels']


def __add_panels(config, setup_table, section):
    setup_table.kibiter_time_from = config[section]['kibiter_time_from']
    setup_table.kibiter_default_index = config[section]['kibiter_default_index']
    setup_table.kibiter_url = config[section]['kibiter_url']
    setup_table.kibiter_version = config[section]['kibiter_version']
    setup_table.community = config[section]['community']
    setup_table.gitlab_issues = config[section]['gitlab-issues']
    setup_table.gitlab_merges = config[section]['gitlab-merges']


def __add_es_collection(config, setup_table, section):
    setup_table.es_collection = config[section]['url']


def __add_es_enrichment(config, setup_table, section):
    setup_table.es_enrichment = config[section]['url']
    setup_table.autorefresh = config[section]['autorefresh']


def load_setup(data):
    config = configparser.ConfigParser()
    config.read_string(data)
    try:
        setup_table = Setup.objects.get(name='setup')
    except Setup.DoesNotExist:
        setup_table = Setup(name='setup')
        setup_table.save()

    for section in config.sections():
        if section == "general":
            __add_general(config, setup_table, section)
        elif section == "projects":
            __add_projects(config, setup_table, section)
        elif section == "es_collection":
            __add_es_collection(config, setup_table, section)
        elif section == "es_enrichment":
            __add_es_enrichment(config, setup_table, section)
        elif section == "sortinghat":
            __add_sortinghat(config, setup_table, section)
        elif section == "phases":
            __add_phases(config, setup_table, section)
        elif section == "panels":
            __add_panels(config, setup_table, section)
        elif any(section in s for s in STUDIES):
            __add_study(config, setup_table, section)
        else:
            __add_backend(config, setup_table, section)

        setup_table.save()