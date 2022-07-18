from keyvaluestore.cli import KeyValueStoreCLI
from keyvaluestore.system import KeyValueStoreSystem

cli = KeyValueStoreCLI(KeyValueStoreSystem())
cli.run()
