import os
import argparse

from miquido_infra_spawner.GitlabService import GitlabService
from miquido_infra_spawner.InfraSpawner import InfraSpawner

if __name__ == '__main__':
    token = os.getenv('GITLAB_TOKEN')
    s = GitlabService(token)
    spawner = InfraSpawner(s, token)

    parser = argparse.ArgumentParser()
    parser.add_argument('--name', '-n', action='store', required=True)
    parser.add_argument('--environment', '-e', action='store', required=True)
    parser.add_argument('--domain_prefix', '-d', action='store', required=True)
    parser.add_argument('--alb_priority', '-a', action='store', required=True)
    parser.add_argument('--gitlab_project_id', '-g', action='store', required=True)
    args = parser.parse_args()

    print(f'name = {args.name}')
    spawner.spawn(
        name=args.name,
        env=args.environment,
        domain_prefix=args.domain_prefix,
        alb_priority=args.alb_priority,
        gitlab_repo=args.gitlab_project_id)

