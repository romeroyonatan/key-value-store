import sys
import textwrap
from typing import Union

from keyvaluestore.system import KeyValueStoreSystem, Transaction


class TransactionIsMissing(RuntimeError):
    """Raised when the user does not start with BEGIN command"""


class KeyValueStoreCLI:
    HELP = textwrap.dedent(
        """
        🐍Welcome to the Simple Storage System!🐍

        You can use the following commands:

                BEGIN           🔸 start a new transaction
                        SET             Set a key-value pair.
                        UNSET           Unset a key
                        GET             Get the value associated with a key.
                        NUMEQUALTO      Returns the number of keys that are
                                        associated with the given value.
                COMMIT          🔸 commit the current transaction.
                ROLLBACK        🔸 rollback the current
                                   transaction.
                HELP            🔸 show this help message
                END             🔸 end the program
        """
    )

    ERROR_TRANSACTION_IS_MISSING = "ERROR: Enter BEGIN command to start"
    PROMPT = "Enter the command:  (HELP): "

    _transaction: Union[Transaction, "NoTransaction"]

    def __init__(self, system: KeyValueStoreSystem, cli_input=sys.stdin, cli_output=sys.stdout):
        self._input = cli_input
        self._output = cli_output
        self._system = system
        self._transaction = NoTransaction()
        self._is_still_running = True
        self._register_commands()

    def _register_commands(self):
        self._commands = {
            "BEGIN": self._begin,
            "SET": self._set,
            "GET": self._get,
            "UNSET": self._unset,
            "NUMEQUALTO": self._numequalto,
            "COMMIT": self._commit,
            "ROLLBACK": self._rollback,
            "HELP": self._help,
            "END": self._end,
        }

    def run(self):
        self._help()
        self._prompt()
        line = self._input.readline()
        while self._is_still_running and line:
            line = line.strip()
            if line:
                self._process_line(line)
            if self._is_still_running:
                self._prompt()
                line = self._input.readline()

    def _prompt(self):
        self._output.write(KeyValueStoreCLI.PROMPT)
        self._output.flush()

    def _process_line(self, line):
        command = line.split()[0].upper()
        if command in self._commands:
            self._execute_command(command, line)
        else:
            self._output.write(f"ERROR: Unknown command '{command}'\n")

    def _execute_command(self, command, line):
        try:
            self._commands[command](line)
        except TransactionIsMissing:
            self._output.write(f"{KeyValueStoreCLI.ERROR_TRANSACTION_IS_MISSING}\n")
        except ValueError as error:
            self._output.write(f"ERROR: {error}\n")

    def _help(self, _=""):
        self._output.write(f"{KeyValueStoreCLI.HELP}")

    def _begin(self, line):
        self._assert_number_of_arguments_equal_to(0, line)
        self._transaction = self._system.begin()
        self._output.write("OK\n")

    def _commit(self, line):
        self._assert_number_of_arguments_equal_to(0, line)
        self._transaction.commit()
        self._transaction = NoTransaction()
        self._output.write("OK\n")

    def _rollback(self, line):
        self._assert_number_of_arguments_equal_to(0, line)
        self._transaction.rollback()
        self._output.write("OK\n")

    def _set(self, line):
        self._assert_number_of_arguments_equal_to(2, line)
        _, key, value = line.split()
        self._transaction.set(key, value)
        self._output.write(f"{key}={value}\n")

    def _get(self, line):
        self._assert_number_of_arguments_equal_to(1, line)
        _, key = line.split()
        try:
            value = self._transaction.get(key)
            self._output.write(f"{value}\n")
        except KeyError:
            self._output.write("(NULL)\n")

    def _unset(self, line):
        self._assert_number_of_arguments_equal_to(1, line)
        _, key = line.split()
        self._transaction.unset(key)
        self._output.write("OK\n")

    def _numequalto(self, line):
        self._assert_number_of_arguments_equal_to(1, line)
        _, value = line.split()
        number = self._transaction.number_of_keys_with_value(value)
        self._output.write(f"{number}\n")

    def _end(self, line):
        self._assert_number_of_arguments_equal_to(0, line)
        self._is_still_running = False
        self._output.write("Good bye\n")

    def _assert_number_of_arguments_equal_to(self, expected, line):
        actual = len(line.split()) - 1
        if actual != expected:
            raise ValueError(f"Expected {expected} arguments but got {actual}")


class NoTransaction:
    def __getattr__(self, item):
        raise TransactionIsMissing
