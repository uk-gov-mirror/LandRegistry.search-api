from unittest import TestCase
from unittest.mock import patch

from search_api.constants.charge_id import ChargeId
from search_api.exceptions import ApplicationError
from search_api.utilities.charge_id import (add_prefix, decode_base_31,
                                            decode_charge_id, encode_base_31,
                                            encode_charge_id,
                                            is_valid_charge_id, remove_prefix)

EXPECTED_ENCODED_MAX_LENGTH = 6
DECODED_INTEGER = 56745
ENCODED_INTEGER = '1X1H'

CHARGE_ID = '123'
PREFIXED_CHARGE_ID = '{}{}'.format(ChargeId.PREFIX, CHARGE_ID)
CHARGE_ID_NO_HYPHEN = '{}{}'.format(ChargeId.PREFIX_NO_SEPARATOR, CHARGE_ID)
INVALID_CHARGE_ID = 'some invalid charge id'


class TestChargeIdService(TestCase):

    def test_is_valid_charge_id_with_valid_charge_id(self):
        """Should return True for a valid charge id"""
        result = is_valid_charge_id(PREFIXED_CHARGE_ID)
        self.assertTrue(result)

    def test_is_valid_charge_id_with_no_hyphen_charge_id(self):
        """Should return True for a valid charge id with no hyphen"""
        result = is_valid_charge_id(CHARGE_ID_NO_HYPHEN)
        self.assertTrue(result)

    def test_is_valid_charge_id_with_invalid_charge_id(self):
        """Should return False for an invalid charge id"""
        result = is_valid_charge_id(INVALID_CHARGE_ID)
        self.assertFalse(result)

    @patch('search_api.utilities.charge_id.encode_base_31')
    @patch('search_api.utilities.charge_id.add_prefix')
    def test_encode_charge_id(self, add_prefix_mock, encode_base_31_mock):
        """Should call add_prefix and encode_base_31"""

        expected_charge_id = '{}{}'.format(ChargeId.PREFIX, ENCODED_INTEGER)

        add_prefix_mock.return_value = expected_charge_id
        actual_charge_id = encode_charge_id(DECODED_INTEGER)

        add_prefix_mock.assert_called()
        encode_base_31_mock.assert_called()
        self.assertEqual(expected_charge_id, actual_charge_id)

    @patch('search_api.utilities.charge_id.decode_base_31')
    @patch('search_api.utilities.charge_id.remove_prefix')
    def test_decode_charge_id(self, remove_prefix_mock, decode_base_31_mock):
        """Should call remove_prefix and encode_base_31"""

        decode_base_31_mock.return_value = DECODED_INTEGER
        actual_charge_id = decode_charge_id(ENCODED_INTEGER)

        remove_prefix_mock.assert_called()
        decode_base_31_mock.assert_called()
        self.assertEqual(DECODED_INTEGER, actual_charge_id)

    def test_add_prefix(self):
        """Should append the expected prefix to the given charge id"""
        actual_charge_id = add_prefix(DECODED_INTEGER)
        expected_charge_id = '{}{}'.format(ChargeId.PREFIX, DECODED_INTEGER)

        self.assertEqual(expected_charge_id, actual_charge_id)

    def test_remove_prefix(self):
        """Should append the expected prefix to the given charge id"""
        actual_charge_id = remove_prefix(PREFIXED_CHARGE_ID)
        expected_charge_id = CHARGE_ID

        self.assertEqual(expected_charge_id, actual_charge_id)

    def test_encode_base_31_expected_output(self):
        """A known input should produce an expected output"""
        charge_id = encode_base_31(DECODED_INTEGER)
        self.assertEqual(ENCODED_INTEGER, charge_id)

    def test_encode_base_31_same_input_same_output(self):
        """The same input should produce the same output"""
        charge_id_one = encode_base_31(DECODED_INTEGER)
        charge_id_two = encode_base_31(DECODED_INTEGER)
        self.assertEqual(charge_id_one, charge_id_two)

    def test_encode_base_31_max_length(self):
        """Output should be ENCODED_MAX with largest input"""
        charge_id = encode_base_31(ChargeId.CEILING)
        self.assertLessEqual(len(charge_id), EXPECTED_ENCODED_MAX_LENGTH)

    def test_encode_base_31_less_than_floor(self):
        """Should throw ApplicationError if the input is less than ChargeId.FLOOR"""
        self.assertRaises(ApplicationError, encode_base_31, ChargeId.FLOOR - 1)

    def test_encode_base_31_more_than_ceiling(self):
        """Should throw ApplicationError if the input is greater than ChargeId.CEILING"""
        self.assertRaises(ApplicationError, encode_base_31, ChargeId.CEILING + 1)

    def test_decode_base_31_expected_output(self):
        """A known input should produce an expected output"""
        charge_id = decode_base_31(ENCODED_INTEGER)
        self.assertEqual(DECODED_INTEGER, charge_id)
