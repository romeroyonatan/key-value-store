# Key-Value Python Store
The purpose of this app create a simple key-value store in Python.
All data will be stored in memory for simplicity.
## Run app
```
$ python -m venv venv
(venv) $ pip install -r requirements.txt
(venv) $ python script.py

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
[13:31:24] DEBUG    Transactions: None                                                                                    script.py:24
Enter the command:  (HELP):
