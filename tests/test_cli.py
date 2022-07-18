import io
import textwrap
from unittest import TestCase

from keyvaluestore.cli import KeyValueStoreCLI
from keyvaluestore.system import KeyValueStoreSystem


class CliTests(TestCase):
    def test_set_and_get_values(self):
        (
            given_a_CLI()
            .type("BEGIN")
            .type("SET hello world")
            .expect("hello=world")
            .type("COMMIT")
            .type("BEGIN")
            .type("GET hello")
            .expect("world")
            .type("COMMIT")
            .type("END")
            .do_it()
        )

    def test_count_keys_with_the_same_value(self):
        (
            given_a_CLI()
            .type("BEGIN")
            .type("SET lucky-number 42")
            .type("SET answer-to-all-things 42")
            .type("NUMEQUALTO 42")
            .expect("2")
            .type("END")
            .do_it()
        )

    def test_unset_values(self):
        (
            given_a_CLI()
            .type("BEGIN")
            .type("SET hello world")
            .type("UNSET hello")
            .type("get hello")
            .expect("(NULL)")
            .type("END")
            .do_it()
        )


    def test_display_an_error_is_transaction_is_missing(self):
        (
            given_a_CLI()
            .type("SET hello world")
            .expect("ERROR: Enter BEGIN command to start")
            .type("get hello")
            .expect("ERROR: Enter BEGIN command to start")
            .type("UNSET hello")
            .expect("ERROR: Enter BEGIN command to start")
            .type("NUMEQUALTO world")
            .expect("ERROR: Enter BEGIN command to start")
            .type("COMMIT")
            .expect("ERROR: Enter BEGIN command to start")
            .type("ROLLBACK")
            .expect("ERROR: Enter BEGIN command to start")
            .do_it()
        )

    def test_unknown_command(self):
        (
            given_a_CLI()
            .type("banana")
            .expect("ERROR: Unknown command 'BANANA'")
            .do_it()
        )

    def test_validate_parameters(self):
        (
            given_a_CLI()
            .type("SET hello")
            .expect("ERROR: Expected 2 arguments but got 1")
            .type("SET hello world world")
            .expect("ERROR: Expected 2 arguments but got 3")
            .type("GET")
            .expect("ERROR: Expected 1 arguments but got 0")
            .type("UNSET")
            .expect("ERROR: Expected 1 arguments but got 0")
            .type("UNSET hello world")
            .expect("ERROR: Expected 1 arguments but got 2")
            .type("NUMEQUALTO")
            .expect("ERROR: Expected 1 arguments but got 0")
            .type("COMMIT a")
            .expect("ERROR: Expected 0 arguments but got 1")
            .type("BEGIN a")
            .expect("ERROR: Expected 0 arguments but got 1")
            .type("END a")
            .expect("ERROR: Expected 0 arguments but got 1")
            .do_it()
        )

    def test_help(self):
        commands = """
        HELP
        """

        expected = KeyValueStoreCLI.HELP.strip()
        cli_input = io.StringIO()
        cli_input.write(commands)
        cli_input.seek(0)

        cli_output = io.StringIO()

        cli = KeyValueStoreCLI(KeyValueStoreSystem(), cli_input, cli_output)
        cli.run()

        actual = cli_output.getvalue()[len(KeyValueStoreCLI.HELP) :].strip()

        self.assertEqual(actual, expected)

    def test_rollback(self):
        (
            given_a_CLI()
            .type("BEGIN")
            .type("SET hello world")
            .type("COMMIT")
            .type("BEGIN")
            .type("SET hello you")
            .type("ROLLBACK")
            .expect("OK")
            .type("GET hello")
            .expect("world")
            .type("END")
            .do_it()
        )

    def test_unset_in_a_transaction(self):
        (
            given_a_CLI()
            .type("BEGIN")
            .type("SET hello world")
            .type("COMMIT")
            .type("BEGIN")
            .type("UNSET hello")
            .type("GET hello")
            .expect("(NULL)")
            .type("END")
            .do_it()
        )

    def test_rollback_unset(self):
        (
            given_a_CLI()
            .type("BEGIN")
            .type("SET hello world")
            .type("COMMIT")
            .type("BEGIN")
            .type("UNSET hello")
            .type("ROLLBACK")
            .type("GET hello")
            .expect("world")
            .type("END")
            .do_it()
        )


class CLITestRunner:
    def __init__(self):
        self._commands = []
        self._expected = {}
        self._do_it_not_called = True

    def type(self, command) -> "CLITestRunner":
        self._commands.append(command)
        return self

    def expect(self, expected_output) -> "CLITestRunner":
        command_index = len(self._commands)
        self._expected[command_index] = expected_output
        return self

    def do_it(self):
        self._do_it_not_called = False
        cli_input = io.StringIO(initial_value="\n".join(self._commands))
        cli_output = io.StringIO()
        cli = KeyValueStoreCLI(KeyValueStoreSystem(), cli_input, cli_output)
        cli.run()
        output = cli_output.getvalue()[len(KeyValueStoreCLI.HELP) :]
        command_index = 1
        for line in output.split("\n"):
            if command_index in self._expected and self._expected[command_index] != line:
                command = self._commands[command_index - 1]
                raise AssertionError(f"{command}: Expected {self._expected[command_index]!r}, but got {line!r}")
            command_index += 1

    def __del__(self):
        if self._do_it_not_called:
            raise AssertionError("You forgot to call do_it()")


def given_a_CLI() -> CLITestRunner:
    return CLITestRunner()
