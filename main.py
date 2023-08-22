"""
Start module
"""

import sys
import json
from typing import Optional
import argparse
from github import Github
from core.nova_component import NovaComponent
from core.nova_release import NovaRelease
from csv_utils import export_packages_to_csv
from mappers import map_to_tag_info
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


if __name__ == "__main__":
    print("Nova Release Manager, version 1.0")

    parser = argparse.ArgumentParser(description="Nova Release Manager")
    parser.add_argument(
        "--command",
        type=str,
        required=True,
        help="The mode release manager will operate in",
        choices=["list-packages", "release"],
        default="release",
    )

    parser.add_argument(
        "--since",
        type=str,
        required=False,
        help="The date to start listing packages from. Format: YYYY-MM-DD. Applicable only for 'list-packages' command",
    )

    parser.add_argument(
        "--csv-output",
        type=str,
        required=False,
        help="The path to CSV file to output the result. Applicable only for 'list-packages' command",
    )

    args = parser.parse_args()

    with open("config.json", encoding="utf-8") as f:
        config = json.load(f)

    ji = JiraIntegration(
        config["jira"]["host"],
        config["jira"]["username"],
        config["jira"]["password"],
    )
    release_repository = NovaReleaseRepository(ji)

    if args.command == "release":
        version = input("Please, enter version (or 'q' for quit): ")
        if version == "q":
            sys.exit()
        delivery = input("Please, enter delivery (or 'q' for quit): ")
        if delivery == "q":
            sys.exit()

        manager = ReleaseManager(
            ji,
            Github(config["github"]["accessToken"]),
            GitIntegration(),
            config["textEditor"],
        )
        release = release_repository.get(
            config["jira"]["project"], version, delivery
        )
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
            print(
                f"Component [{component.name}] released, tag: [{tag}], url: [{url}]"
            )

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

    if args.command == "list-packages":
        packages = release_repository.get_packages(config["jira"]["project"])
        gi = GitIntegration()
        all_tags_info = []
        for package in packages:
            package_tags = gi.list_tags(package.repo.url, args.since)
            package_tags_info = list(
                map(
                    lambda tag, pkg=package: map_to_tag_info(pkg, tag),
                    package_tags,
                )
            )
            package_tags_info_sorted = sorted(
                package_tags_info,
                key=lambda tag_info: tag_info["date"],
                reverse=True,
            )
            all_tags_info.extend(package_tags_info_sorted)

        if all_tags_info:
            export_packages_to_csv(all_tags_info, args.csv_output)
