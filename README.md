<a name="readme-top"></a>

<!-- PROJECT SHIELDS -->
<!--
*** I'm using markdown "reference style" links for readability.
*** Reference links are enclosed in brackets [ ] instead of parentheses ( ).
*** See the bottom of this document for the declaration of the reference variables
*** for contributors-url, forks-url, etc. This is an optional, concise syntax you may use.
*** https://www.markdownguide.org/basic-syntax/#reference-style-links
-->
[![Issues][issues-shield]][issues-url]
[![MIT License][license-shield]][license-url]


<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#about-the-project">About The Project</a>
    </li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#configuration">Configuration</a></li>
      </ul>
    </li>
    <li><a href="#usage">Usage</a></li>
    <li><a href="#roadmap">Roadmap</a></li>
    <li><a href="#license">License</a></li>
    <li><a href="#contact">Contact</a></li>
  </ol>
</details>



<!-- ABOUT THE PROJECT -->
## About The Project
This project is devoted to delivery automation for another Lykke-based project called `NOVA`. It manages releases in `JIRA`. It also creates release notes and tags components in `GitHub` and `Bitbucket`.

<p align="right">(<a href="#readme-top">back to top</a>)</p>


<!-- GETTING STARTED -->
## Getting Started

This project is built using Python 3.10. To get started, you need to install Python 3.10 and the required dependencies.
To install Python 3.10, please visit the [Python website](https://www.python.org/downloads/).
To install project dependencies, please run the following command:
```sh
pip install -r requirements.txt
```

### Configuration

The `config.json` file is used to configure various aspects of the application. Here's a breakdown of the different sections and their meanings:

#### jira

This section is used to configure the connection to Jira instance.

- `host`: The URL of your Jira instance.
- `username`: The username used to authenticate with Jira.
- `password`: The password or token used to authenticate with Jira.
- `project`: The key of the Jira project to interact with.

#### github

This section is used to configure the connection to GitHub.

- `username`: The username of the GitHub account.
- `accessToken`: The personal access token of the GitHub account. If there are private repositories in the project, the token must have access to private repositories.

#### bitbucket

This section is used to configure the connection to Bitbucket.

- `username`: The username of the Bitbucket account.
- `password`: The password of the Bitbucket account.

#### release

This section is used to configure the release process.

- `branch`: The branch to release from.
- `artifactsFolderPathTemplate`: The template for the path where release artifacts should be stored. `{nova}` and `{delivery}{hotfix}` are placeholders that will be replaced with actual values during the release process.
- `packageTags`: This section is used to configure the tagging of packages.
  - `exceptions`: An array of exceptions for package tagging. Each exception has:
    - `name`: The name of the package.
    - `tagTemplate`: The template for the tag of the package. The tag will be generated by replacing the "*" in the template with the version of the package.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

#### Example

Here is configuration file example:
```json
{
  "jira": {
    "host": "<JIRA_HOST>",
    "username": "<JIRA_USERNAME>",
    "password": "<JIRA_PASSWORD_OR_TOKEN>",
    "project": "<JIRA_PROJECT>"
  },
  "github": {
    "username": "<GITHUB_USERNAME>",
    "accessToken": "<GITHUB_ACCESS_TOKEN>"
  },
  "bitbucket": {
    "username": "<BITBUCKET_USERNAME>",
    "password": "<BITBUCKET_PASSWORD_OR_TOKEN>"
  },
  "release": {
    "branch": "<RELEASE_BRANCH>",
    "artifactsFolderPathTemplate": "{nova}{delivery}{hotfix}",
    "packageTags": {
      "exceptions": [
        {
          "name": "<PACKAGE_NAME_1>",
          "tagTemplate": "<TAG_TEMPLATE_1>"
        },
        {
          "name": "<PACKAGE_NAME_2>",
          "tagTemplate": "<TAG_TEMPLATE_2>"
        },
        // Add more packages as needed
      ]
    }
  },
  "textEditor": "code"
}
```


<!-- USAGE EXAMPLES -->
## Usage

The application has three modes of operation:
- `release`: This mode is used to create a release for every component. It supposes that there is already release created in JIRA with tasks assigned and ready for release. When running in this mode it first asks for the `NOVA` version, which is 2 as of December 14, 2023 and delivery number. Based on these values it fetches the information from JIRA and suggests to go throw release steps for every component, which includes:
  - Generating new CHANGELOG entry based on JIRA tasks. Before committing the CHANGELOG entry, it opens it in the text editor specified in the `textEditor` configuration option.
  - Optionally updating versions in .csproj files.
  - Tagging the repository.
  - Moving tasks to the next status (`DONE`).
- `list-packages`: This mode is used to list the package versions created since the date specified. Option `--since` is used to specify the date. The date should be in the format `YYYY-MM-DD`. Option is not mandatory. If it is not specified, the application will try to detect the latest release date and list the packages created since that date. If neither the date is specified nor the latest release date is detected, the application will raise an error. The `packages-output.csv` file is created in the folder specified in the `artifactsFolderPathTemplate` configuration option.
- `list-services`: This mode is used to list the services versions created since the date specified. Option `--since` is used to specify the date. The date should be in the format `YYYY-MM-DD`. Option is not mandatory. If it is not specified, the application will try to detect the latest release date and list the services created since that date. If neither the date is specified nor the latest release date is detected, the application will raise an error. The `services-output.csv` file is created in the folder specified in the `artifactsFolderPathTemplate` configuration option.
- `generate-notes`: This mode is used to generate release notes for the specified delivery. It created a .pdf file for every component which has CHANGELOG.md file in the root folder. The .pdf file is created in the folder specified in the `artifactsFolderPathTemplate` configuration option.

Please note, the application heavily depends on the JIRA's `Components` feature. It is assumed that every component has its own `Component` in JIRA and every task is assigned to the corresponding `Component`. The `Component` name is used as the name of the component in the application. It means the registry of components in JIRA is the single source of truth for the application and should be managed with care.

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- ROADMAP -->
## Roadmap

See the [open issues](https://github.com/tarurar/NovaReleaseManager/issues) for a full list of proposed features (and known issues).

<p align="right">(<a href="#readme-top">back to top</a>)</p>


<!-- LICENSE -->
## License

Distributed under the MIT License. See `LICENSE.txt` for more information.

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- CONTACT -->
## Contact

[Andrei Tarutin](https://twitter.com/atarutin) - andrey.tarutin@lykke-business.ch

Project Link: [https://github.com/tarurar/NovaReleaseManager](https://github.com/tarurar/NovaReleaseManager)

<p align="right">(<a href="#readme-top">back to top</a>)</p>


<!-- MARKDOWN LINKS & IMAGES -->
<!-- https://www.markdownguide.org/basic-syntax/#reference-style-links -->
[issues-shield]: https://img.shields.io/github/issues/tarurar/NovaReleaseManager.svg?style=for-the-badge
[issues-url]: https://github.com/tarurar/NovaReleaseManager/issues
[license-shield]: https://img.shields.io/github/license/tarurar/NovaReleaseManager.svg?style=for-the-badge
[license-url]: https://github.com/tarurar/NovaReleaseManager/blob/master/LICENSE.txt