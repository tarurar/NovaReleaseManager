"""
Jira utility helper function module.
"""

from typing import Optional
from urllib.parse import urlparse
import validators

from core.cvs import GitCloudService


def parse_jira_cmp_descr(descr: str) -> tuple[
        Optional[GitCloudService],
        Optional[str]]:
    """
    Parse Jira component description and return cloud service and
    repository URL. It is epected that JIRA component description
    will be in the following format:
        Bitbucket: http(s)://bitbucket.org/<repo>
        GitHub: http(s)://github.com/<company>/<repo> or
            just <company>/<repo>
    """
    if descr is None:
        return None, None

    normalized_description = descr.strip().lower()

    if not normalized_description.startswith('http'):
        normalized_description = 'http://' + normalized_description

    if validators.url(normalized_description):
        url_parse_result = urlparse(normalized_description)
        if 'github' in url_parse_result.hostname:
            return GitCloudService.GITHUB, descr
        if 'bitbucket' in url_parse_result.hostname:
            return GitCloudService.BITBUCKET, descr
    return None, None
