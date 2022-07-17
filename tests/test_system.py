from unittest import TestCase

from keyvaluestore.system import KeyValueStoreSystem

A_KEY = "key"
A_VALUE = "value"
A_NON_EXISTENT_KEY = "do not exists"
ANOTHER_VALUE = "another value"
ANOTHER_KEY = "another key"


class TestSystem(TestCase):
    def setUp(self):
        self.system = KeyValueStoreSystem()
        self.system.begin()

    def tearDown(self):
        self.system.end()

    def test_can_set_and_get_a_value_in_a_transaction(self):
        transaction = self.system.begin()

        transaction.set(A_KEY, A_VALUE)

        actual = transaction.get(A_KEY)
        expected = A_VALUE
        self.assertEqual(actual, expected)

    def test_raise_keyerror_if_the_key_does_not_exist(self):
        transaction = self.system.begin()

        with self.assertRaises(KeyError):
            transaction.get(A_NON_EXISTENT_KEY)

    def test_the_value_setted_by_one_transaction_is_not_visible_to_other_transactions_until_commit(self):
        transaction1 = self.system.begin()
        transaction2 = self.system.begin()

        transaction1.set(A_KEY, A_VALUE)

        with self.assertRaises(KeyError):
            transaction2.get(A_KEY)

    def test_a_transaction_can_read_a_value_created_by_another_transaction(self):
        transaction1 = self.system.begin()
        transaction2 = self.system.begin()

        transaction1.set(A_KEY, A_VALUE)
        transaction1.commit()

        actual = transaction2.get(A_KEY)
        expected = A_VALUE
        self.assertEqual(actual, expected)

    def test_when_we_rollback_a_transaction_the_system_should_ignore_the_changes(self):
        transaction1 = self.system.begin()
        transaction2 = self.system.begin()

        transaction1.set(A_KEY, A_VALUE)
        transaction1.rollback()
        transaction1.commit()

        with self.assertRaises(KeyError):
            transaction2.get(A_KEY)

    def test_when_a_transaction_try_to_modify_old_data_the_system_should_reject_the_commit(self):
        transaction1 = self.system.begin()
        transaction2 = self.system.begin()
        transaction3 = self.system.begin()

        transaction1.set(A_KEY, A_VALUE)
        transaction2.set(A_KEY, ANOTHER_VALUE)

        transaction1.commit()
        with self.assertRaises(KeyValueStoreSystem.TransactionConflict):
            transaction2.commit()

        actual = transaction3.get(A_KEY)
        expected = A_VALUE
        self.assertEqual(actual, expected)

    def test_unset_a_key_in_a_transaction(self):
        transaction = self.system.begin()
        transaction.set(A_KEY, A_VALUE)

        transaction.unset(A_KEY)

        with self.assertRaises(KeyError):
            transaction.get(A_KEY)

    def test_a_transaction_can_unset_keys_created_by_other_transactions(self):
        transaction1 = self.system.begin()
        transaction2 = self.system.begin()
        transaction3 = self.system.begin()

        transaction1.set(A_KEY, A_VALUE)
        transaction1.commit()

        transaction2.unset(A_KEY)
        transaction2.commit()

        with self.assertRaises(KeyError):
            transaction3.get(A_KEY)

    def test_get_number_of_keys_with_the_same_value_in_a_transaction(self):
        transaction1 = self.system.begin()
        transaction1.set(A_KEY, A_VALUE)
        transaction1.set(ANOTHER_KEY, A_VALUE)

        actual = transaction1.number_of_keys_with_value(A_VALUE)
        expected = 2
        self.assertEqual(actual, expected)

    def test_take_account_of_keys_created_by_other_transactions_with_the_same_value(self):
        transaction1 = self.system.begin()
        transaction2 = self.system.begin()

        transaction1.set(A_KEY, A_VALUE)
        transaction1.commit()

        transaction2.set(ANOTHER_KEY, A_VALUE)

        actual = transaction2.number_of_keys_with_value(A_VALUE)
        expected = 2
        self.assertEqual(actual, expected)
