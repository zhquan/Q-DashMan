from django.db import models
# Create your models here.


class Repository(models.Model):
    name = models.CharField(max_length=200)
    parent = models.CharField(max_length=200)
    params = models.CharField(max_length=200)

    def __str__(self):
        return self.name + " " + self.params


class DataSource(models.Model):
    name = models.CharField(max_length=200)
    parent = models.CharField(max_length=200)
    repository = models.ManyToManyField(Repository)

    def __str__(self):
        return self.name


class Project(models.Model):
    name = models.CharField(max_length=200, unique=True)
    meta_title = models.CharField(max_length=200)
    data_source = models.ManyToManyField(DataSource)

    def __str__(self):
        return self.name


class Backends(models.Model):
    name = models.CharField(max_length=200, unique=True)
    raw_index = models.CharField(max_length=200)
    enriched_index = models.CharField(max_length=200)
    no_archive = models.CharField(max_length=200)
    api_token = models.CharField(max_length=200)
    sleep_time = models.CharField(max_length=200)
    latest_items = models.CharField(max_length=200)
    studies = models.CharField(max_length=200)
    sleep_for_rate = models.CharField(max_length=200)

    def __str__(self):
        return self.name


class Studies(models.Model):
    name = models.CharField(max_length=200)
    in_index = models.CharField(max_length=200)
    out_index = models.CharField(max_length=200)
    data_source = models.CharField(max_length=200)
    contribs_field = models.CharField(max_length=200)
    timeframe_field = models.CharField(max_length=200)
    sort_on_field = models.CharField(max_length=200)
    no_incremental = models.CharField(max_length=200)
    seconds = models.CharField(max_length=200)

    def __str__(self):
        return self.name


class Setup(models.Model):
    name = models.CharField(max_length=200, default='setup')
    short_name = models.CharField(max_length=200, unique=True)
    update = models.CharField(max_length=200)
    min_update_delay = models.CharField(max_length=200)
    debug = models.CharField(max_length=200)
    logs_dir = models.CharField(max_length=200)
    bulk_size = models.CharField(max_length=200)
    scroll_size = models.CharField(max_length=200)
    aliases_file = models.CharField(max_length=200)
    projects_file = models.CharField(max_length=200)
    es_collection = models.CharField(max_length=200)
    es_enrichment = models.CharField(max_length=200)
    autorefresh = models.CharField(max_length=200)
    collection = models.CharField(max_length=200)
    identities = models.CharField(max_length=200)
    enrichment = models.CharField(max_length=200)
    panels = models.CharField(max_length=200)
    host = models.CharField(max_length=200)
    user = models.CharField(max_length=200)
    password = models.CharField(max_length=200)
    database = models.CharField(max_length=200)
    load_orgs = models.CharField(max_length=200)
    orgs_file = models.CharField(max_length=200)
    autoprofile = models.CharField(max_length=200)
    matching = models.CharField(max_length=200)
    sleep_for = models.CharField(max_length=200)
    bots_names = models.CharField(max_length=200)
    unaffiliated_group = models.CharField(max_length=200)
    affiliate = models.CharField(max_length=200)
    kibiter_time_from = models.CharField(max_length=200)
    kibiter_default_index = models.CharField(max_length=200)
    kibiter_url = models.CharField(max_length=200)
    kibiter_version = models.CharField(max_length=200)
    community = models.CharField(max_length=200)
    gitlab_issues = models.CharField(max_length=200)
    gitlab_merges = models.CharField(max_length=200)
    backends = models.ManyToManyField(Backends)
    studies = models.ManyToManyField(Studies)
    