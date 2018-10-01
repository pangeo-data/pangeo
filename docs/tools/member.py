#!/usr/bin/env python3
import os
import argparse
import yaml

from github import Github


def main(access_token, people_yml):
    '''update the Pangeo organization with any new members'''
    # authentication with GitHub
    g = Github(access_token)
    org = g.get_organization('pangeo-data')

    # people.yml is in the pangeo docs
    with open(people_yml) as f:
        people = yaml.safe_load(f)

    github_ids = [p['github'] for p in people]

    # pangeo-members = 2180253
    team = org.get_team(2180253)

    # get existing GitHub members
    existing_org_logins = list(member.login for member in org.get_members())
    existing_team_logins = list(member.login for member in team.get_members())

    # add those members not yet in the GitHub org
    for member in github_ids:
        user = g.get_user(member)
        print(user)
        if member not in existing_org_logins:
            print(f'--> adding {member} to org')
            org.add_to_members(user, role='member')

        if member not in existing_team_logins:
            print(f'--> adding {member} to team')
            team.add_membership(user, role='member')


if __name__ == "__main__":

    print(list(os.environ.keys()), flush=True)

    parser = argparse.ArgumentParser(description='Add users to GitHub Org/Team')
    parser.add_argument('--access_token', required=True, type=str,
                        help='GitHub Access Token')
    parser.add_argument('--people', required=True, type=str,
                        help='Path to people.yml')
    args = parser.parse_args()
    
    main(args.access_token, args.people)