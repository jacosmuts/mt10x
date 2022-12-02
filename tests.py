import unittest

from datetime import date
from unittest import mock

from mt10x import MT103, Text, UserHeader


MESSAGE1 = (
    "{1:F01ASDFJK20AXXX0987654321}"
    "{2:I103ASDFJK22XXXXN}"
    "{4: :20:20180101-ABCDEF :23B:GHIJ :32A:180117CAD5432,1 :33B:EUR9999,0 :50K:/123456-75901 SOMEWHERE New York 999999 GR :53B:/20100213012345 :57C://SC200123 :59:/201001020 First Name Last Name a12345bc6d789ef01a23 Nowhere NL :70:test reference test reason payment group: 1234567-ABCDEF :71A:SHA :77B:Test this -}"  # NOQA: E501
)
MESSAGE2 = (
    "{1:F01QWERTY22AXXX1234567890}"
    "{2:I103QWERTY33XXXXA7}"
    "{3:{108:MT103}}"
    "{4:\n:20:1234567-8901\n:23B:ABCD\n:32A:000625EUR1000,00\n:33B:EUR1000,00\n:50K:COMPANY NAME\nNAPLES\n:52A:ABCDEFGH123\n:53A:ABCDEF12\n:54A:ABCDEF1G\n:57A:ABCDEFGHIJK\n:59:/20061120050500001A01234\nBENEFICIARY NAME\n:70:/REMITTANCE INFO\n:71A:SHA\n-}"  # NOQA: E501
)
MESSAGE3 = (
    "{1:F01QWERTY22AXXX1234567890}"
    "{2:I103QWERTY33XXXXA7}"
    "{3:{113:SEPA}{111:001}{121:d2d62e74-4f7d-45dc-a230-85fa259e1694}}"
    "{4: :20:123456-ABCDEF001 :23B:GHIJ :32A:123456GBP10000,00 :33B:GBP10000,00 :50K:/This is arbitrary text :52D:/123456-78900 More arbitrary text :53B:/12345678901234 :57C://AB123456 :59:/12345678 Even more arbitrary text :70:abc - 12.34 more txt 20190115-ABCDEF :71A:SHA :72:/INS/ABCDEF01 -}"  # NOQA: E501
)
MESSAGE4 = (
    "{1:F01AAAAGRA0AXXX0057000289}"
    "{2:O1030919010321BBBBGRA0AXXX00570001710103210920N}"
    "{3:{108:MT103 003 OF 045}{121:c8b66b47-2bd9-48fe-be90-93c2096f27d2}}"
    "{4:\n:20:5387354\n:23B:CRED\n:23E:PHOB/20.527.19.60\n:32A:000526USD1101,50\n:33B:USD1121,50\n:50K:FRANZ HOLZAPFEL GMBH\nVIENNA\n:52A:BKAUATWW\n:59:723491524\nC. KLEIN\nBLOEMENGRACHT 15\nAMSTERDAM\n:71A:SHA\n:71F:USD10,\n:71F:USD10,\n:72:/INS/CHASUS33\n-}"
    "{5:{MAC:75D138E4}{CHK:DE1B0D71FA96}}"
)


class SwiftMT103TestCase(unittest.TestCase):
    def test___init__(self):

        keys = (
            "basic_header",
            "application_header",
            "user_header",
            "text",
            "trailer",
        )

        with mock.patch.object(MT103, "_populate_by_parsing") as m:
            mt103 = MT103("test")
            self.assertFalse(mt103)
            self.assertEqual(m.call_count, 1)

        for key in keys:
            self.assertIsNone(getattr(mt103, key))
            self.assertEqual(mt103.raw, "test")

    def test__populate_by_parsing_message1(self):

        mt103 = MT103(MESSAGE1)

        self.assertTrue(mt103)
        self.assertEqual(mt103.basic_header, "F01ASDFJK20AXXX0987654321")
        self.assertEqual(mt103.application_header, "I103ASDFJK22XXXXN")
        self.assertFalse(mt103.user_header)
        self.assertEqual(mt103.trailer, None)

        self.assertEqual(str(mt103.text), MESSAGE1[54:-3])

    def test__populate_by_parsing_message2(self):

        mt103 = MT103(MESSAGE2)
        self.assertTrue(mt103)
        self.assertEqual(mt103.basic_header, "F01QWERTY22AXXX1234567890")
        self.assertEqual(mt103.application_header, "I103QWERTY33XXXXA7")
        self.assertEqual(str(mt103.user_header), "{108:MT103}")
        self.assertEqual(mt103.text.raw, MESSAGE2[70:-3])
        self.assertEqual(mt103.trailer, None)

    def test__populate_by_parsing_message3(self):

        mt103 = MT103(MESSAGE3)
        self.assertTrue(mt103)
        self.assertEqual(mt103.basic_header, "F01QWERTY22AXXX1234567890")
        self.assertEqual(mt103.application_header, "I103QWERTY33XXXXA7")
        self.assertEqual(
            str(mt103.user_header),
            "{113:SEPA}{111:001}{121:d2d62e74-4f7d-45dc-a230-85fa259e1694}",
        )
        self.assertEqual(mt103.text.raw, MESSAGE3[120:-3])
        self.assertEqual(mt103.trailer, None)

    def test__populate_by_parsing_message4(self):

        mt103 = MT103(MESSAGE4)
        self.assertTrue(mt103)
        self.assertEqual(mt103.basic_header, "F01AAAAGRA0AXXX0057000289")
        self.assertEqual(
            mt103.application_header,
            "O1030919010321BBBBGRA0AXXX00570001710103210920N",
        )
        self.assertEqual(
            str(mt103.user_header),
            "{108:MT103 003 OF 045}{121:c8b66b47-2bd9-48fe-be90-93c2096f27d2}",
        )
        self.assertEqual(mt103.text.raw, MESSAGE4[152:-39])
        self.assertEqual(mt103.trailer, "{MAC:75D138E4}{CHK:DE1B0D71FA96}")

    def test_truthyness(self):
        self.assertFalse(MT103(""))
        self.assertFalse(MT103("test"))

    def test___str__(self):
        self.assertEqual(str(MT103(MESSAGE1)), MESSAGE1)
        self.assertEqual(str(MT103(MESSAGE2)), MESSAGE2)
        self.assertEqual(str(MT103(MESSAGE3)), MESSAGE3)
        self.assertEqual(str(MT103(MESSAGE4)), MESSAGE4)


class UserHeaderTestCase(unittest.TestCase):
    def test___init__(self):

        keys = (
            "bank_priority_code",
            "message_user_reference",
            "service_type_identifier",
            "unique_end_to_end_transaction_reference",
        )

        with mock.patch.object(Text, "_populate_by_parsing"):
            user_header = UserHeader("test")

        self.assertFalse(user_header)

        for key in keys:
            self.assertIsNone(getattr(user_header, key))
            self.assertEqual(user_header.raw, "test")

    def test__populate_by_parsing(self):

        mt103 = MT103(MESSAGE1)
        self.assertTrue(mt103)
        self.assertFalse(mt103.user_header)

        mt103 = MT103(MESSAGE2)
        self.assertTrue(mt103)
        self.assertTrue(mt103.user_header)
        self.assertIsNone(mt103.user_header.bank_priority_code)
        self.assertIsNone(mt103.user_header.bpc)
        self.assertEqual(mt103.user_header.message_user_reference, "MT103")
        self.assertEqual(mt103.user_header.mur, "MT103")
        self.assertIsNone(mt103.user_header.service_type_identifier)
        self.assertIsNone(mt103.user_header.sti)
        self.assertIsNone(
            mt103.user_header.unique_end_to_end_transaction_reference
        )  # NOQA: E501
        self.assertIsNone(mt103.user_header.uetr)

        mt103 = MT103(MESSAGE3)
        self.assertTrue(mt103)
        self.assertTrue(mt103.user_header)
        self.assertEqual(mt103.user_header.bank_priority_code, "SEPA")
        self.assertEqual(mt103.user_header.bpc, "SEPA")
        self.assertIsNone(mt103.user_header.message_user_reference)
        self.assertIsNone(mt103.user_header.mur)
        self.assertEqual(mt103.user_header.service_type_identifier, "001")
        self.assertEqual(mt103.user_header.sti, "001")
        self.assertEqual(
            "d2d62e74-4f7d-45dc-a230-85fa259e1694",
            mt103.user_header.unique_end_to_end_transaction_reference,
        )
        self.assertEqual(
            "d2d62e74-4f7d-45dc-a230-85fa259e1694", mt103.user_header.uetr
        )


class TextTestCase(unittest.TestCase):
    def test___init__(self):

        keys = (
            "transaction_reference",
            "bank_operation_code",
            "interbank_settled_currency",
            "interbank_settled_amount",
            "original_ordered_currency",
            "original_ordered_amount",
            "ordering_customer",
            "ordering_institution",
            "sender_correspondent",
            "receiver_correspondent",
            "intermediary",
            "account_with_institution",
            "beneficiary",
            "remittance_information",
            "details_of_charges",
            "sender_to_receiver_information",
            "regulatory_reporting",
            "date",
        )

        with mock.patch.object(Text, "_populate_by_parsing"):
            text = Text("test")

        self.assertFalse(text)

        for key in keys:
            self.assertIsNone(getattr(text, key))
            self.assertEqual(text.raw, "test")

    def test__populate_by_parsing_message1(self):

        mt103 = MT103(MESSAGE1)

        self.assertTrue(mt103)
        self.assertTrue(mt103.text)
        self.assertEqual(mt103.text.transaction_reference, "20180101-ABCDEF")
        self.assertEqual(mt103.text.interbank_settled_currency, "CAD")
        self.assertEqual(mt103.text.original_ordered_currency, "EUR")
        self.assertEqual(mt103.text.bank_operation_code, "GHIJ")
        self.assertEqual(mt103.text.date, date(2018, 1, 17))
        self.assertEqual(
            mt103.text.ordering_customer,
            "/123456-75901 SOMEWHERE New York 999999 GR",
        )
        self.assertEqual(mt103.text.regulatory_reporting, "Test this")
        self.assertEqual(mt103.text.sender_to_receiver_information, None)
        self.assertEqual(mt103.text.original_ordered_amount, "9999,0")
        self.assertEqual(
            mt103.text.beneficiary,
            "/201001020 First Name Last Name a12345bc6d789ef01a23 Nowhere NL",
        )
        self.assertEqual(
            mt103.text.remittance_information,
            "test reference test reason payment group: 1234567-ABCDEF",
        )
        self.assertEqual(mt103.text.details_of_charges, "SHA")
        self.assertEqual(mt103.text.sender_correspondent, "/20100213012345")
        self.assertEqual(mt103.text.intermediary, None)
        self.assertEqual(mt103.text.receiver_correspondent, None)
        self.assertEqual(mt103.text.interbank_settled_amount, "5432,1")
        self.assertEqual(mt103.text.ordering_institution, None)
        self.assertEqual(mt103.text.account_with_institution, "//SC200123")

    def test__populate_by_parsing_message4(self):

        mt103 = MT103(MESSAGE4)

        self.assertTrue(mt103)
        self.assertTrue(mt103.text)
        self.assertEqual(mt103.text.transaction_reference, "5387354")
        self.assertEqual(mt103.text.interbank_settled_currency, "USD")
        self.assertEqual(mt103.text.original_ordered_currency, "USD")
        self.assertEqual(mt103.text.bank_operation_code, "CRED")
        self.assertEqual(mt103.text.date, date(2000, 5, 26))
        self.assertEqual(
            mt103.text.ordering_customer, "FRANZ HOLZAPFEL GMBH\nVIENNA"
        )
        self.assertIsNone(mt103.text.regulatory_reporting)
        self.assertEqual(
            mt103.text.sender_to_receiver_information, "/INS/CHASUS33"
        )
        self.assertEqual(mt103.text.original_ordered_amount, "1121,50")
        self.assertEqual(
            mt103.text.beneficiary,
            "723491524\nC. KLEIN\nBLOEMENGRACHT 15\nAMSTERDAM",
        )
        self.assertIsNone(mt103.text.remittance_information)
        self.assertEqual(mt103.text.details_of_charges, "SHA")
        self.assertIsNone(mt103.text.sender_correspondent)
        self.assertIsNone(mt103.text.intermediary)
        self.assertEqual(mt103.text.receiver_correspondent, None)
        self.assertEqual(mt103.text.interbank_settled_amount, "1101,50")
        self.assertEqual(mt103.text.ordering_institution, "BKAUATWW")
        self.assertIsNone(mt103.text.account_with_institution)

    def test_truthyness(self):
        self.assertFalse(Text(""))
        self.assertFalse(Text("test"))
        self.assertFalse(MT103("").text)
        self.assertFalse(MT103("test").text)
        self.assertTrue(MT103(MESSAGE1).text)


if __name__ == "__main__":
    unittest.main()
