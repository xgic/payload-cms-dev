# XG AIS (Xoren Games Automation Intelligence System)

## Aiming to make the most of your time, every time.

XG AIS is a project designed to automate and streamline various processes within Xoren Games, enhancing efficiency and productivity.

Welcome to the XG AIS project repository! This repository contains the source code and documentation for the Xoren Games Automation Intelligence System. Please note that this repository is private and intended for internal use within Xoren Games only.

## Getting Started

### Prerequisites

Before setting up the development environment, ensure you have the following installed:

- [Docker](https://www.docker.com/get-started)
- [Visual Studio Code (VS Code)](https://code.visualstudio.com/)
- [Git](https://git-scm.com/downloads)

### Development Environment Setup

To ensure a consistent and efficient development experience, XG AIS utilizes VS Code development containers. These containers provide a pre-configured environment with all the necessary tools and dependencies. The following steps will guide you through setting up the development environment for the first time or when the base Docker images need to be recreated.

1. **Login with a Standard Developer Account**
   - Use your assigned developer credentials. If you do not have an account, please contact the IT department.

2. **Open or Clone the Project**
   - If the project already exists in the `~/source/xg-ais` directory, open it with VS Code locally or using SSH.
   - If the project is not located at `~/source/xg-ais`, clone the repository to the standard path on a Debian-based development system:
     ```bash
     git clone <repository-url> ~/source/xg-ais
     cd ~/source/xg-ais
     ```
   - Ensure your local repository is up to date by pulling the latest changes:
     ```bash
     git pull origin main
     ```

3. **Build Initial Docker Images**
   - Run the following command to build the initial Docker images required for the development environment:
     ```bash
     ./initial_build
     ```
   - This script sets up the base images needed for the development containers.

4. **Install the XG GitOps Console Application**
   - Install the application in editable mode to facilitate development and testing:
     ```bash
     pip install --user -e .
     ```

5. **Test the XG GitOps Console Application**
   - Use the following commands to manage the Docker Compose services for the development environment:
     ```bash
     # Start or restart all XG AIS services
     xg ais dev -r

     # Stop all XG AIS services
     xg ais dev -s
     ```
   - Verify that the services start correctly. If you encounter issues, check the logs or consult the troubleshooting guide.

6. **Rebuild and Open in Development Container**
   - Use the VS Code command palette to select `Dev Containers: Rebuild and Reopen in Container`. This ensures the development containers are up to date and configured correctly for the XG AIS project.

## Contributing

We welcome contributions to the XG AIS project! Please follow these guidelines:

- **Coding Standards:** Adhere to the project's coding standards and best practices.
- **Testing:** Ensure all code changes are thoroughly tested. Include unit tests where applicable.
- **Pull Requests:** Submit pull requests for review. Provide a clear description of the changes and reference any related issues.

For more detailed information, please refer to the [Contributing Guide](CONTRIBUTING.md).

## Documentation

Additional documentation is available to help you understand and work with the XG AIS project:

- [API Reference](docs/api.md)
- [Architecture Overview](docs/architecture.md)
- [User Guide](docs/user-guide.md)

## Support

If you need assistance or encounter any issues, please reach out to the development team:

- **Email:** [support@xorengames.com](mailto:support@xorengames.com)
- **Issue Tracker:** [GitLab Issues](https://gitlab.xorengames.com/xg/xg-ais/-/issues)

## Licensing

This project is private and for use only at Xoren Games [Private License](LICENSE).