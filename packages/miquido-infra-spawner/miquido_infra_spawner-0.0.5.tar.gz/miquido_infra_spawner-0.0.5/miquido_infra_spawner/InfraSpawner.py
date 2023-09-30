import os
import shutil
import subprocess

from miquido_infra_spawner.GitlabService import GitlabService


class InfraSpawner:
    def __init__(self, service: GitlabService, gitlab_token: str):
        self.service = service
        self.gitlab_token = gitlab_token
        self.parent_group_id = os.getenv('PARENT_GROUP_ID', '15196715')

    def spawn(self, name, env, domain_prefix, alb_priority, gitlab_repo):
        gr_access_token = self.service.create_project_gitlab_registry_access_token(gitlab_repo)
        api_access_token = self.service.create_project_api_access_token(gitlab_repo)
        project_id, path = self.service.create_project(name, self.parent_group_id)
        self.service.create_gitlab_token_environment_variable(project_id, api_access_token)
        self.service.create_secrets_file(project_id, gr_access_token)
        source_dir = f'{os.path.dirname(__file__)}/template'
        destination_dir = name
        shutil.copytree(source_dir, destination_dir)
        os.chdir(destination_dir)
        os.rename('env', env)
        self.write_values_tf(alb_priority, destination_dir, domain_prefix, env, gitlab_repo, name)
        self.write_state_file(env, project_id)
        self.write_gitlab_ci(domain_prefix, env)
        self.push_repo(path)

    def push_repo(self, path):
        subprocess.call(["git", "init"])
        subprocess.call(
            ["git", "remote", "add", "origin", f"https://xd:{self.gitlab_token}@gitlab.com/{path}.git"])
        subprocess.call(["git", "add", "."])
        subprocess.call(["git", "commit", "-m", '"Initial commit"'])
        subprocess.call(["git", "push", "--set-upstream", 'origin', 'main'])

    def write_gitlab_ci(self, domain_prefix, env):
        with open('.gitlab-ci.yml', 'r') as file:
            filedata = file.read()
        filedata = filedata.replace('<ENVIRONMENT>', env)
        filedata = filedata.replace('<DOMAIN_PREF>', domain_prefix)
        with open('.gitlab-ci.yml', 'w') as file:
            file.write(filedata)

    def write_state_file(self, env, project_id):
        with open(f'{env}/state.tf', 'r') as file:
            filedata = file.read()
        filedata = filedata.replace('<PROJECT_ID>', str(project_id))
        with open(f'{env}/state.tf', 'w') as file:
            file.write(filedata)

    def write_values_tf(self, alb_priority, destination_dir, domain_prefix, env, gitlab_repo, project):
        values = f'''
            project="{project}"
            domain_prefix="{domain_prefix}"
            alb_priority="{alb_priority}"
            gitlab_repo="{gitlab_repo}"
            environment="{env}"
            '''
        with open(f'{env}/variables.auto.tfvars', 'w') as f:
            f.write(values)
