import argparse
import dew.args
from dew.dependencyprocessor import DependencyProcessor
from dew.dewfile import Dependency
from dew.impl import CommandData


class ArgumentData(object):
    def __init__(self) -> None:
        self.name = ''


def get_argparser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument('name')
    return parser


def execute(args: ArgumentData, data: CommandData) -> int:
    dewfile_path = 'dewfile.json'
    if data.args.dewfile:
        dewfile_path = data.args.dewfile

    dewfile = dew.dewfile.parse_dewfile(dewfile_path)

    target_dep: Dependency = None
    for dep in dewfile.dependencies:
        if dep.name == args.name:
            target_dep = dep

    if target_dep is None:
        data.view.error(f'Unknown dependency "{args.name}"')
        return 1

    previous_ref = target_dep.ref

    processor = DependencyProcessor(data.storage, data.view, target_dep, dewfile, data.properties)
    target_dep.ref = processor.get_remote().get_latest_ref()
    dew.dewfile.save_refs(dewfile, dewfile_path)

    if previous_ref != target_dep.ref:
        data.view.info(f'Dependency {args.name} upgraded from {previous_ref} to {target_dep.ref}.')
    else:
        data.view.info(f'Dependency {args.name} is already at latest ref {previous_ref} for head {target_dep.head}')

    return 0