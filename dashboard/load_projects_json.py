from dashboard.models import DataSource, Project, Repository

def load_project(data):
    for project in data:
        try:
            project_form = Project.objects.get(name=project)
        except Project.DoesNotExist:
            project_form = Project(name=project)
            project_form.save()

        for ds in data[project]:
            if ds != "meta":
                try:
                    ds_form = DataSource.objects.get(parent=project, name=ds)
                except DataSource.DoesNotExist:
                    ds_form = DataSource(parent=project, name=ds)
                    ds_form.save()
                try:
                    meta_title = data[project]["meta"]["title"]
                    project_form.meta_title = meta_title
                    project_form.save()
                except KeyError:
                    pass
                
                for repo in data[project][ds]:
                    try:
                        repo_form = Repository.objects.get(parent=project, name=repo)
                    except Repository.DoesNotExist:
                        repo_form = Repository(parent=project, name=repo)
                        repo_form.save()
                    ds_form.repository.add(repo_form)
                ds_form.save()

                project_form.data_source.add(ds_form)
        project_form.save()