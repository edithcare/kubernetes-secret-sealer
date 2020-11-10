import pytest
from click.testing import CliRunner
from sealer import cli


@pytest.fixture
def runner():
    return CliRunner()


# def test_cli(runner):
#     result = runner.invoke(cli.main)
#     assert result.exit_code == 0
#     assert not result.exception
#     assert result.output.strip() == 'Hello, world.'


def test_cli_with_option(runner):
    result = runner.invoke(cli.main, ['--help'])
    assert not result.exception
    assert result.exit_code == 0
    assert result.output.split("\n")[0] == 'Usage: main [OPTIONS]'


# def test_cli_with_arg(runner):
#     result = runner.invoke(cli.main, ['Michael'])
#     assert result.exit_code == 0
#     assert not result.exception
#     assert result.output.strip() == 'Hello, Michael.'
