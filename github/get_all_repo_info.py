#!/usr/bin/python3
# -*- coding:utf-8 -*-

from github import Github

g = Github("2567729201@qq.com", "Qw060101.github")

org = g.get_organization("PharbersDeveloper")
org.login

repo = g.get_repo("PharbersDeveloper/BP-Server-Deploy")
commit_head_sha = repo.get_commits()[0].sha
last_commit_date = repo.get_commit(sha=commit_head_sha).commit.author.date

for repo in g.get_user().get_repos():
    print(repo.name)
    # repo.edit(has_wiki=False)
    # # to see all the available attributes and methods
    # print(dir(repo))
