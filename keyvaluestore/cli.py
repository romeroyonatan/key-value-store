import sys

from keyvaluestore.system import KeyValueStoreSystem


class TransactionIsMissing(RuntimeError):
    """Raised when the user does not start with BEGIN command"""


class KeyValueStoreCLI:
    HELP = """
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
    Enter the command:  (HELP):
            """

    ERROR_TRANSACTION_IS_MISSING = "ERROR: Enter BEGIN command to start"

    def __init__(self, system, cli_input=sys.stdin, cli_output=sys.stdout):
        self._input = cli_input
        self._output = cli_output
        self._system = system
        self._transaction = NoTransaction()
        self._is_running = True

    def run(self):
        self._output.write(KeyValueStoreCLI.HELP)
        line = self._input.readline()
        while self._is_running and line:
            line = line.strip()
            if line:
                self._process_line(line)
            if self._is_running:
                line = self._input.readline()

    def _process_line(self, line):
        command = line.split()[0].upper()
        try:
            if command == "BEGIN":
                self._begin()
            elif command == "SET":
                self._set(line)
            elif command == "GET":
                self._get(line)
            elif command == "UNSET":
                self._unset(line)
            elif command == "NUMEQUALTO":
                self._numequalto(line)
            elif command == "COMMIT":
                self._commit()
            elif command == "END":
                self._end()
            else:
                self._output.write(f"ERROR: Unknown command '{command}'\n")
        except TransactionIsMissing:
            self._output.write(f"{KeyValueStoreCLI.ERROR_TRANSACTION_IS_MISSING}\n")

    def _begin(self):
        self._transaction = self._system.begin()
        self._output.write("OK\n")

    def _commit(self):
        self._transaction.commit()
        self._transaction = NoTransaction()
        self._output.write("OK\n")

    def _set(self, line):
        _, key, value = line.split()
        self._transaction.set(key, value)
        self._output.write(f"{key}={value}\n")

    def _get(self, line):
        _, key = line.split()
        value = self._transaction.get(key)
        self._output.write(f"{value}\n")

    def _unset(self, line):
        _, key = line.split()
        self._transaction.unset(key)
        self._output.write("OK\n")

    def _numequalto(self, line):
        _, value = line.split()
        number = self._transaction.number_of_keys_with_value(value)
        self._output.write(f"{number}\n")

    def _end(self):
        self._is_running = False
        self._output.write("Good bye\n")


class NoTransaction:
    def set(self, key, value):
        raise TransactionIsMissing

    def get(self, value):
        raise TransactionIsMissing

    def number_of_keys_with_value(self, value):
        raise TransactionIsMissing

    def unset(self, key):
        raise TransactionIsMissing

    def commit(self):
        raise TransactionIsMissing


if __name__ == "__main__":
    cli = KeyValueStoreCLI(KeyValueStoreSystem())
    cli.run()
