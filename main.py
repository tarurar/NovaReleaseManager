"""
Start module
"""

import sys
import json
from typing import Optional
from github import Github
from core.nova_component import NovaComponent
from core.nova_release import NovaRelease
from release_manager import ReleaseManager
from nova_release_repository import NovaReleaseRepository
from integration.jira import JiraIntegration
from integration.git import GitIntegration
from ui.console import preview_component_release


def choose_component_from_release(rel: NovaRelease) -> Optional[NovaComponent]:
    """Choose component from release"""
    print("\n")
    print(
        "Please note, by default 'contains' rule will be used for component selection"
    )
    print(
        "If you want to use strict equality rule, please, add '!' sign to the end of component name"
    )
    component_name = input(
        "Please, select component to release or press 'q' (you can specify name partially): "
    )
    if component_name == "q":
        return None
    cmp = rel.get_component_by_name(component_name)
    if cmp is None:
        print("Component not found")
        return choose_component_from_release(rel)
    return cmp


# def removeComponentName(source):
#     i1 = source.find('[')
#     i2 = source.find(']')
#     if i1 >= 0 and i2 > 0:
#         componentPart = source[i1:i2 + 1]
#         result = source.replace(componentPart, '').strip()
#         return removeComponentName(result)
#     else:
#         return source
# def printIssues(issues, showPullRequest, separateTasks):
#     componentName = None
#     for issue in issues:
#         if len(issue.fields.components) > 0:
#             if componentName != issue.fields.components[0].name:
#                 componentName = issue.fields.components[0].name
#                 print('\n' + componentName)
#                 print('===========================================')
#         print('* {}: {}'.format(issue.key,
#               removeComponentName(issue.fields.summary.strip())))
#         instructions = issue.raw['fields']['customfield_10646']
#         if instructions is not None:
#             print('DEPLOYMENT INSTRUCTIONS:' + str(instructions))
#         if showPullRequest:
#             print('Pull request: ' +
#                str(issue.raw['fields']['customfield_10659']))
#         if separateTasks:
#             print('-------------------------------------------')


print("Nova Release Manager, version 1.0")
version = input("Please, enter version (or 'q' for quit): ")
if version == "q":
    sys.exit()
delivery = input("Please, enter delivery (or 'q' for quit): ")
if delivery == "q":
    sys.exit()

with open("config.json", encoding="utf-8") as f:
    config = json.load(f)

ji = JiraIntegration(
    config["jira"]["host"],
    config["jira"]["username"],
    config["jira"]["password"],
)
manager = ReleaseManager(
    ji,
    Github(config["github"]["accessToken"]),
    GitIntegration(),
    config["textEditor"],
)
release_repository = NovaReleaseRepository(ji)
release = release_repository.get(config["jira"]["project"], version, delivery)
print(release.describe_status())


while True:
    component = choose_component_from_release(release)
    if component is None:
        break
    preview_component_release(release, component)
    release_component_decision = input(
        "Do you want to release this component [Y/n/q]?"
    )
    if release_component_decision == "q":
        break
    if release_component_decision == "n":
        continue
    tag, url = manager.release_component(release, component)
    print(f"Component [{component.name}] released, tag: [{tag}], url: [{url}]")

    if release.can_release_version():
        release_version_decision = input(
            "Looks like all components are released."
            + "Do you want to release version [Y/n]?"
        )
        if release_version_decision == "Y":
            job_done = release_repository.set_released(release)
            if job_done:
                print(
                    f"Version [{release.title}] has been successfully released"
                )
                break
            print(f"Version [{release.title}] has not been released")
