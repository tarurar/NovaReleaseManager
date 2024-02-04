"""
Start module
"""

import argparse
import sys
from typing import Optional

from config import Config
from core.nova_component import NovaComponent
from core.nova_release import NovaRelease
from csv_utils import export_packages_to_csv
from integration.git import GitIntegration
from integration.jira import JiraIntegration
from mappers import is_package_tag, map_to_tag_info
from notes_generator import NotesGenerator
from nova_release_repository import NovaReleaseRepository
from release_manager import ReleaseManager
from ui.console import preview_component_release


def choose_component_from_release(rel: NovaRelease) -> Optional[NovaComponent]:
    """Choose component from release"""
    print("\n")
    print("Please note, 'contains' rule will be used for component selection")
    print("To use strict equality, please add '!' sign to the end of name")
    component_name = input(
        "Please, select component or press 'q' (partial name supported): "
    )
    if component_name == "q":
        return None
    cmp = rel.get_component_by_name(component_name)
    if cmp is None:
        print("Component not found")
        return choose_component_from_release(rel)
    return cmp


if __name__ == "__main__":
    print("Nova Release Manager, version 1.3")

    parser = argparse.ArgumentParser(description="Nova Release Manager")
    parser.add_argument(
        "--command",
        type=str,
        required=True,
        help="The mode release manager will operate in",
        choices=["list-packages", "release", "generate-notes"],
        default="release",
    )

    parser.add_argument(
        "--version",
        type=str,
        required=False,
        help="""
        NOVA version number. Default is 2.
        Applicable only for 'release' and 'generate-notes' commands.
        """,
        default=2,
    )

    parser.add_argument(
        "--delivery",
        type=str,
        required=True,
        help="""
        NOVA delivery number.
        Applicable only for 'release' and 'generate-notes' commands.
        """,
    )

    parser.add_argument(
        "--since",
        type=str,
        required=False,
        help="""
        The date to start listing packages from. Format: YYYY-MM-DD. 
        Applicable only for 'list-packages' command.
        """,
    )

    parser.add_argument(
        "--csv-output",
        type=str,
        required=False,
        help="""
        The path to CSV file to output the result. 
        Applicable only for 'list-packages' command.
        """,
    )

    parser.add_argument(
        "--config-path",
        type=str,
        required=False,
        help="""
        The path to configuration file, optional.
        If not specified, the config.json file in the current directory will be used.
        """,
    )

    args = parser.parse_args()

    config = Config(args.config_path)

    ji = JiraIntegration(
        config.data["jira"]["host"],
        config.data["jira"]["username"],
        config.data["jira"]["password"],
    )
    release_repository = NovaReleaseRepository(ji)

    if args.command == "release":
        version = args.version
        delivery = args.delivery
        manager = ReleaseManager()
        release = release_repository.get(
            config.data["jira"]["project"], version, delivery
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
            try:
                component_release = manager.release_component(
                    release, component
                )
            except Exception as e:
                print(f"Error occurred: {e}")
                continue
            print(
                f"[{component.name}] released, tag: [{component_release.tag_name}], url: [{component_release.url}]"
            )

            if release.can_release_version():
                release_version_decision = input(
                    "Looks like all components are released."
                    + "Do you want to release version [Y/n]?"
                )
                if release_version_decision == "Y":
                    if release_repository.set_released(release):
                        print(
                            f"[{release.title}] has been successfully released"
                        )
                        break
                    print(f"[{release.title}] has not been released")

    if args.command == "list-packages":
        packages = release_repository.get_packages(
            config.data["jira"]["project"]
        )
        gi = GitIntegration()
        all_tags_info: list[dict[str, str]] = []
        counter = 0
        for package in packages:
            counter += 1

            if package.repo is None:
                continue

            repo_all_tags = gi.list_tags(package.repo.url, args.since)

            # filter out tags which are not related to packages, common rules
            package_tags = list(
                filter(
                    lambda tag, pkg=package: is_package_tag(pkg, tag),
                    repo_all_tags,
                )
            )

            # if exception is specified for package, filter out tags which
            # do not match the exception
            tag_exception = config.get_package_tag_exception(package.name)
            if tag_exception:
                package_tags = list(
                    filter(
                        lambda tag, e=tag_exception: e.tag_template
                        in tag.name.lower(),
                        package_tags,
                    )
                )

            # skip packages with no tags
            if len(package_tags) == 0:
                continue

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

            percents_done = round(counter / len(packages) * 100)
            print(
                f"{package.name:<50} processed, {len(package_tags):<3} tags discovered {'with exceptions' if tag_exception else ''}, ({percents_done:<3}% done)"
            )

        if all_tags_info:
            path = export_packages_to_csv(all_tags_info, args.csv_output)
            print(f"CSV file has been created: {path}")
        else:
            print("No tags found")

    if args.command == "generate-notes":
        version = args.version
        delivery = args.delivery
        manager = ReleaseManager()
        release = release_repository.get(
            config.data["jira"]["project"], version, delivery
        )
        print(release.describe_status())
        notes_generator = NotesGenerator(release, GitIntegration())
        if not notes_generator.can_generate():
            print(
                "Release is not ready to generate notes. Please, check the status of the release."
            )
            sys.exit()
        notes = notes_generator.generate()
        print("Release notes generated: ")
        for component_name, result in notes.items():
            if result.path:
                print(f"    [{component_name}]: [{result.path}]")
        print("Release notes were not generated for the following components:")
        for component_name, result in notes.items():
            if result.error:
                print(f"    [{component_name}]: [{result.error}]")
