from __future__ import annotations
import json

import os
import subprocess

import pkg_resources
import toml
from pydantic import BaseModel
from termcolor import colored


class SnowHelperConfig(BaseModel):
    udf: str = None
    sproc: str = None
    streamlit: str = None
    task: str = None


class SnowHelper:
    SNOWFLAKE_ANACONDA_URL = "https://repo.anaconda.com/pkgs/snowflake/"

    BASE_PATHS = {
        "udf": "src/udf",
        "sproc": "src/sproc",
        "streamlit": "src/streamlit",
        "task": "src/task",
    }

    @staticmethod
    def get_template_path(relative_path):
        return pkg_resources.resource_filename("snowdev", relative_path)

    TEMPLATES = {
        "udf": {
            "py": "fillers/udf/fill.py",
            "toml": "fillers/udf/fill.toml",
        },
        "sproc": {
            "py": "fillers/sproc/fill.py",
            "toml": "fillers/sproc/fill.toml",
        },
        "streamlit": {
            "py": "fillers/streamlit/fill.py",
            "yml": "fillers/streamlit/fill.yml",
        },
        "task": {
            "sql": "fillers/task/fill.sql",
        },
    }

    @classmethod
    def read_file_lines(cls, path, filename):
        with open(os.path.join(path, filename), "r") as file:
            return file.read().splitlines()

    @classmethod
    def get_packages_from_requirements(cls, path):
        return cls.read_file_lines(path, "requirements.txt")

    @classmethod
    def get_imports(cls, path):
        return cls.read_file_lines(path, "imports.txt")

    @classmethod
    def get_packages_from_toml(cls, path):
        data = toml.load(os.path.join(path, "app.toml"))
        dependencies = data["tool"]["poetry"]["dependencies"]
        dependencies.pop("python", None)
        return [f"{pkg}=={version}" for pkg, version in dependencies.items()]

    @classmethod
    def search_package_in_snowflake_channel(cls, package_name):
        if len(package_name) <= 1:
            print(f"Invalid package name: {package_name}")
            return None
        cmd = [
            "conda",
            "search",
            "-c",
            cls.SNOWFLAKE_ANACONDA_URL,
            "--override-channels",
            "--json",
            package_name,
        ]

        try:
            process = subprocess.Popen(
                cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )
            stdout, stderr = process.communicate()
        except Exception as e:
            print(f"Failed to execute command {cmd}: {e}")
            return None

        if process.returncode != 0:
            print(
                f"Command {cmd} failed with return code {process.returncode}: {stderr.decode()}"
            )
            return None

        try:
            results = json.loads(stdout.decode())
            if package_name not in results:
                print(f"Package {package_name} not found")
                return None
            versions = [
                package_info["version"] for package_info in results[package_name]
            ]
            latest_version = max(
                versions, key=lambda version: tuple(map(int, version.split(".")))
            )
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            print(
                f"Failed to parse package versions for {package_name}. Output: {stdout.decode()}"
            )
            return None
        # Return the latest version
        return latest_version

    @classmethod
    def is_package_available_in_snowflake_channel(cls, package_name):
        versions = cls.search_package_in_snowflake_channel(package_name)
        return bool(versions)

    @classmethod
    def get_available_versions_from_snowflake_channel(cls, package_name):
        return cls.search_package_in_snowflake_channel(package_name)

    @classmethod
    def get_dependencies_of_package(cls, package_name):
        try:
            distribution = pkg_resources.get_distribution(package_name)
            return [requirement.name for requirement in distribution.requires()]
        except pkg_resources.DistributionNotFound:
            return []

    @classmethod
    def are_dependencies_available_in_snowflake_channel(cls, package_name):
        dependencies = cls.get_dependencies_of_package(package_name)
        return all(
            cls.is_package_available_in_snowflake_channel(dep) for dep in dependencies
        )

    @classmethod
    def is_specific_version_available_in_snowflake_channel(cls, package_name, version):
        available_versions = cls.get_available_versions_from_snowflake_channel(
            package_name
        )
        return version in available_versions

    @classmethod
    def create_new_component(cls, args_dict):
        config = SnowHelperConfig(**args_dict)
        item_type, item_name = next(
            ((key, value) for key, value in config.dict().items() if value),
            (None, None),
        )

        if not item_type:
            print(
                colored(
                    "Error: Please provide either --udf, --sproc, --streamlit, or --task when using the 'new' command.",
                    "red",
                )
            )
            return

        base_path = cls.BASE_PATHS.get(item_type)
        if not base_path:
            print(colored(f"Unknown item type: {item_type}", "red"))
            return

        new_item_path = os.path.join(base_path, item_name)

        if os.path.exists(new_item_path):
            print(colored(f"{item_type} {item_name} already exists!", "yellow"))
            return

        os.makedirs(new_item_path, exist_ok=True)
        creation_successful = True

        # Handle creation for Streamlit
        if item_type == "streamlit":
            for ext, template_name in cls.TEMPLATES[item_type].items():
                output_name = "streamlit_app.py" if ext == "py" else "environment.yml"
                cls._create_file_from_template(
                    new_item_path, output_name, template_name, item_type, ext, item_name
                )

        # Handle creation for UDF, SPROC, and Task
        else:
            for ext, template_name in cls.TEMPLATES[item_type].items():
                filename = "app.py" if ext == "py" else "app.toml"
                if item_type == "task" and ext == "sql":
                    filename = "app.sql"
                cls._create_file_from_template(
                    new_item_path, filename, template_name, item_type, ext, item_name
                )

        if creation_successful:
            print(
                colored(
                    f"{item_type} {item_name} has been successfully created!", "green"
                )
            )

    @staticmethod
    def _create_file_from_template(
        new_item_path, filename, template_name, item_type, ext, item_name=None
    ):
        try:
            template_content = pkg_resources.resource_string(
                "snowdev", template_name
            ).decode("utf-8")
            if item_type == "streamlit" and ext == "yml":
                template_content = template_content.replace("snowflake-test", item_name)
            elif item_type == "task" and ext == "sql":
                template_content = template_content.replace("sample_task", item_name)
            with open(os.path.join(new_item_path, filename), "w") as f:
                f.write(template_content)
        except FileNotFoundError:
            print(
                colored(
                    f"No template found for {item_type} with extension {ext}. Creating an empty {filename}...",
                    "yellow",
                )
            )
            with open(os.path.join(new_item_path, filename), "w") as f:
                pass
