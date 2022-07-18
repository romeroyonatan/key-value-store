import sys

from keyvaluestore.system import KeyValueStoreSystem


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

    def __init__(self, system, cli_input=sys.stdin, cli_output=sys.stdout):
        self._input = cli_input
        self._output = cli_output
        self._system = system

    def run(self):
        self._output.write(KeyValueStoreCLI.HELP)
        line = self._input.readline()
        transaction = None
        while line:
            line = line.strip()
            if line:
                command = line.split()[0]
                if command == "BEGIN":
                    transaction = self._system.begin()
                    self._output.write("OK\n")
                if command == "SET":
                    _, key, value = line.split()
                    transaction.set(key, value)
                    self._output.write(f"{key}={value}\n")
                if command == "GET":
                    _, key = line.split()
                    value = transaction.get(key)
                    self._output.write(f"{value}\n")
                if command == "UNSET":
                    _, key = line.split()
                    transaction.unset(key)
                    self._output.write("OK\n")
                if command == "NUMEQUALTO":
                    _, value = line.split()
                    number = transaction.number_of_keys_with_value(value)
                    self._output.write(f"{number}\n")
                if command == "COMMIT":
                    transaction.commit()
                    transaction = None
                    self._output.write("OK\n")
                if command == "END":
                    self._output.write("Good bye\n")
                    break
            line = self._input.readline()


if __name__ == "__main__":
    cli = KeyValueStoreCLI(KeyValueStoreSystem())
    cli.run()