import io
import textwrap
from unittest import TestCase

from keyvaluestore.cli import KeyValueStoreCLI
from keyvaluestore.system import KeyValueStoreSystem


class CliTests(TestCase):
    def test_show_help_at_the_begginng(self):
        cli_input = io.StringIO()
        cli_input.seek(0)

        cli_output = io.StringIO()

        cli = KeyValueStoreCLI(KeyValueStoreSystem(), cli_input, cli_output)
        cli.run()

        actual = cli_output.getvalue()
        expected = KeyValueStoreCLI.HELP

        self.assertEqual(actual, expected)

    def test_set_and_get_values(self):
        commands = """
        BEGIN
        SET hello world
        COMMIT
        BEGIN
        GET hello
        COMMIT
        END
        """

        expected = textwrap.dedent(
            """
            OK
            hello=world
            OK
            OK
            world
            OK
            Good bye
            """
        ).strip()
        cli_input = io.StringIO()
        cli_input.write(commands)
        cli_input.seek(0)

        cli_output = io.StringIO()

        cli = KeyValueStoreCLI(KeyValueStoreSystem(), cli_input, cli_output)
        cli.run()

        actual = cli_output.getvalue()[len(KeyValueStoreCLI.HELP) :].strip()

        self.assertEqual(actual, expected)

    def test_count_keys_with_the_same_value(self):
        commands = """
        BEGIN
        SET lucky-number 42
        SET answer-to-all-things 42
        NUMEQUALTO 42
        COMMIT
        END
        """

        expected = textwrap.dedent(
            """
            OK
            lucky-number=42
            answer-to-all-things=42
            2
            OK
            Good bye
            """
        ).strip()
        cli_input = io.StringIO()
        cli_input.write(commands)
        cli_input.seek(0)

        cli_output = io.StringIO()

        cli = KeyValueStoreCLI(KeyValueStoreSystem(), cli_input, cli_output)
        cli.run()

        actual = cli_output.getvalue()[len(KeyValueStoreCLI.HELP) :].strip()

        self.assertEqual(actual, expected)

    def test_unset_values(self):
        commands = """
        BEGIN
        SET hello world
        UNSET hello
        COMMIT
        end
        """

        expected = textwrap.dedent(
            """
            OK
            hello=world
            OK
            OK
            Good bye
            """
        ).strip()
        cli_input = io.StringIO()
        cli_input.write(commands)
        cli_input.seek(0)

        cli_output = io.StringIO()

        cli = KeyValueStoreCLI(KeyValueStoreSystem(), cli_input, cli_output)
        cli.run()

        actual = cli_output.getvalue()[len(KeyValueStoreCLI.HELP) :].strip()

        self.assertEqual(actual, expected)

    def test_display_an_error_is_transaction_is_missing(self):
        commands = """
        SET hello world
        GET hello
        UNSET hello
        NUMEQUALTO world
        COMMIT
        """

        expected = textwrap.dedent(
            """
            ERROR: Enter BEGIN command to start
            ERROR: Enter BEGIN command to start
            ERROR: Enter BEGIN command to start
            ERROR: Enter BEGIN command to start
            ERROR: Enter BEGIN command to start
            """
        ).strip()
        cli_input = io.StringIO()
        cli_input.write(commands)
        cli_input.seek(0)

        cli_output = io.StringIO()

        cli = KeyValueStoreCLI(KeyValueStoreSystem(), cli_input, cli_output)
        cli.run()

        actual = cli_output.getvalue()[len(KeyValueStoreCLI.HELP) :].strip()

        self.assertEqual(actual, expected)

    def test_unknown_command(self):
        commands = """
        beggint
        """

        expected = textwrap.dedent(
            """
            ERROR: Unknown command 'BEGGINT'
            """
        ).strip()
        cli_input = io.StringIO()
        cli_input.write(commands)
        cli_input.seek(0)

        cli_output = io.StringIO()

        cli = KeyValueStoreCLI(KeyValueStoreSystem(), cli_input, cli_output)
        cli.run()

        actual = cli_output.getvalue()[len(KeyValueStoreCLI.HELP) :].strip()

        self.assertEqual(actual, expected)

    def test_validate_parameters(self):
        commands = """
        SET hello
        SET hello word world
        GET
        GET hello world
        UNSET
        UNSET hello world
        NUMEQUALTO
        COMMIT a
        BEGIN a
        END a
        """

        expected = textwrap.dedent(
            """
            ERROR: Expected 2 arguments but got 1
            ERROR: Expected 2 arguments but got 3
            ERROR: Expected 1 arguments but got 0
            ERROR: Expected 1 arguments but got 2
            ERROR: Expected 1 arguments but got 0
            ERROR: Expected 1 arguments but got 2
            ERROR: Expected 1 arguments but got 0
            ERROR: Expected 0 arguments but got 1
            ERROR: Expected 0 arguments but got 1
            ERROR: Expected 0 arguments but got 1
            """
        ).strip()
        cli_input = io.StringIO()
        cli_input.write(commands)
        cli_input.seek(0)

        cli_output = io.StringIO()

        cli = KeyValueStoreCLI(KeyValueStoreSystem(), cli_input, cli_output)
        cli.run()

        actual = cli_output.getvalue()[len(KeyValueStoreCLI.HELP) :].strip()

        self.assertEqual(actual, expected)

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
