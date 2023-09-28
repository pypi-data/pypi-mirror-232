import os
from typing import Any, Dict, List

import click
import git
from gable.helpers.repo_interactions import get_git_repo_info
from gable.openapi import ContractInput, PostContractRequest, Status
from requests import get


def load_contract_from_file(file: click.File) -> Dict[str, Any]:
    if file.name.endswith(".yaml") or file.name.endswith(".yml"):
        import yaml

        try:
            return yaml.safe_load(file)  # type: ignore
        except yaml.scanner.ScannerError as exc:  # type: ignore
            # This should be a custom exception for user errors
            raise click.ClickException(f"Error parsing YAML file: {file.name}")
    elif file.name.endswith(".toml"):
        raise click.ClickException(
            "We don't currently support defining contracts with TOML, try YAML instead!"
        )
    elif file.name.endswith(".json"):
        raise click.ClickException(
            "We don't currently support defining contracts with JSON, try YAML instead!"
        )
    else:
        raise click.ClickException("Unknown filetype, try YAML instead!")


def contract_files_to_post_contract_request(
    contractFiles: List[click.File],
) -> PostContractRequest:
    contracts = []
    for contractFile in contractFiles:
        contract = load_contract_from_file(contractFile)
        if "id" not in contract:
            raise click.ClickException(f"{contractFile}:\n\tContract must have an id.")
        git_info = get_git_repo_info(contractFile.name)
        relative_path = os.path.relpath(contractFile.name, git_info["localRepoRootDir"])
        if relative_path.startswith(".."):
            raise click.ClickException(
                f"{contractFile.name}:\n\tContract must be located within the git repo where gable is being executed ({git_info['localRepoRootDir']})."
            )
        contractInput = ContractInput(
            id=contract["id"],
            version="0.0.1",  # This should be server calculated
            status=Status("ACTIVE"),
            reviewers=[],  # This should be info accessible from a github PR integration
            filePath=relative_path,
            contractSpec=contract,
            gitHash=git_info["gitHash"],
            gitRepo=git_info["gitRemoteOriginHTTPS"],  # type: ignore
            gitUser=git_info["gitUser"],
            mergedAt=git_info["mergedAt"],
        )
        contracts.append(contractInput)
    return PostContractRequest(
        __root__=contracts,
    )
