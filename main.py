"""
Start module
"""
import json
from github import Github
from jira import JIRA
from core.nova_component import NovaComponent
from core.nova_release import NovaRelease
from release_manager import ReleaseManager


def choose_component_from_release(r: NovaRelease) -> NovaComponent:
    """Choose component from release"""
    print('\n')
    component_name = input(
        'Please, select component to release or press \'q\': ')
    if (component_name == 'q'):
        return None
    c = r.get_component_by_name(component_name)
    if c is None:
        print('Component not found')
        return choose_component_from_release(r)
    return c


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
#         print('* {}: {}'.format(issue.key, removeComponentName(issue.fields.summary.strip())))
#         instructions = issue.raw['fields']['customfield_10646']
#         if instructions is not None:
#             print('DEPLOYMENT INSTRUCTIONS:' + str(instructions))
#         if showPullRequest:
#             print('Pull request: ' + str(issue.raw['fields']['customfield_10659']))
#         if separateTasks:
#             print('-------------------------------------------')

with open('config.json', encoding='utf-8') as f:
    config = json.load(f)

# issues = jira.search_issues('project=LT and fixVersion="Nova 2. Delivery 26" order by Component asc', maxResults=100)
# printIssues(issues, False, False)
# #changeStatusDone(issues)
# print('Total issues count: ' + str(len(issues)))

VERSION = '2'
DELIVERY = '27'
manager = ReleaseManager(
    JIRA(
        config['jira']['host'],
        basic_auth=(config['jira']['username'], config['jira']['password'])),
    Github(config['github']['accessToken']))
release = manager.compose_release(config['jira']['project'], VERSION, DELIVERY)
print(release.describe_status())
component = choose_component_from_release(release)
if component is not None:
    manager.release_component(release, component)
    print(f'Component {component.name} released')
