import re

from datetime import date


class MT10x:
    """
    Parses an MT10x standard banking format string into a string-like Python
    object so you can do things like `mt103.basic_header` or `print(mt10x)`.

    Usage:

    mt10x = MT10x("some-mt-10x-string")                   #103 and 101 i hope
    print("basic header: {}, bank op code: {}, complete message: {}".format(
        mt103.basic_header,
        mt103.text.bank_operation_code
        mt103
    ))

    With considerable help from:
    http://www.sepaforcorporates.com/swift-for-corporates/read-swift-message-structure/
    https://www.sepaforcorporates.com/swift-for-corporates/explained-swift-gpi-uetr-unique-end-to-end-transaction-reference/



    also this (mt10x comment): Some people, when confronted with a problem, think "I know, I'll use regular expressions."
    Now they have two problems.  (Jamie Zawinski)
    """

    # fmt: off
    MESSAGE_REGEX = re.compile(
        r"^"
        r"({1:(?P<basic_header>[^}]+)})?"
        r"({2:(?P<application_header>(I|O)[^}]+)})?"
        r"({3:"
            r"(?P<user_header>"
                r"({113:[A-Z]{4}})?"
                r"({108:[A-Z 0-9]{0,16}})?"
                r"({111:[0-9]{3}})?"
                r"({121:[a-zA-Z0-9]{8}-[a-zA-Z0-9]{4}-4[a-zA-Z0-9]{3}-[89ab][a-zA-Z0-9]{3}-[a-zA-Z0-9]{12}})?"  # NOQA: E501
            r")"
        r"})?"
        r"({4:\s*(?P<text>.+?)\s*-})?"
        r"({5:(?P<trailer>.+)})?"
        r"$",
        re.DOTALL,
    )
    # fmt: on

    def __init__(self, message):

        if message is None:
            message = ""

        self.raw = message.strip()
        self.basic_header = None
        self.application_header = None
        self.user_header = None
        self.text = None
        self.trailer = None

        self._boolean = False

        self._populate_by_parsing()

    def __str__(self):
        return self.raw

    def __repr__(self):
        return str(self)

    def __bool__(self):
        return self._boolean

    __nonzero__ = __bool__  # Python 2

    def _populate_by_parsing(self):

        if not self.raw:
            return

        m = self.MESSAGE_REGEX.match(self.raw)

        self._boolean = bool(m)

        if not m:
            return None

        self.basic_header = BasicHeader(m.group("basic_header") or "")
        self.application_header = ApplicationHeader(m.group("application_header"))
        self.trailer = m.group("trailer")

        self.user_header = UserHeader(m.group("user_header") or "")
        self.text = Text(m.group("text") or "")


class BasicHeader:
    """
    Actually just need application header for this module, but might as well do basic header while at it.

     """

    def __init__(self, raw):

        self.raw = raw

        self._application_id = None
        self._service_id = None
        self._logical_terminal_address = None
        self._session_number = None
        self._sequence_number = None

        self._boolean = False

        self._populate_by_parsing()

    def __str__(self):
        return self.raw

    def __repr__(self):
        return str(self)

    def __bool__(self):
        return self._boolean

    @property
    def application_id(self):
        return self._application_id

    @property
    def service_id(self):
        return self._service_id

    @property
    def logical_terminal_address(self):
        return self._logical_terminal_address

    @property
    def session_number(self):
        return self._session_number

    @property
    def sequence_number(self):
        return self._sequence_number

    def _populate_by_parsing(self):
        """
        Using python string indexes, since I suck at regex.

        #Todo: I have not checked rules around optional fields, below is sufficient for
               my purpose, but might break for more sophisticated use cases.
        """

        if not self.raw:
            return

        self._boolean = bool(self.raw)  # True

        self._application_id = self.raw[0:1]
        self._service_id = self.raw[1:3]
        self._logical_terminal_address = self.raw[3:15]
        self._session_number = self.raw[15:19]
        self._sequence_number = self.raw[19:25]


class ApplicationHeader:
    """
   Simple string indexes.
    """

    def __init__(self, raw):

        self.raw = raw

        self._input_output = None
        self._swift_message_type = None
        self._destination_address = None
        self._priority = None
        self._delivery_monitoring = None
        self._obsolescence_period = None

        self._boolean = False

        self._populate_by_parsing()

    def __str__(self):
        return self.raw

    def __repr__(self):
        return str(self)

    def __bool__(self):
        return self._boolean

    @property
    def input_output(self):
        return self._input_output

    @property
    def swift_message_type(self):
        return self._swift_message_type

    @property
    def destination_address(self):
        return self._destination_address

    @property
    def priority(self):
        return self._priority

    @property
    def delivery_monitoring(self):
        return self._delivery_monitoring

    @property
    def obsolescence_period(self):
        return self._obsolescence_period



    def _populate_by_parsing(self):
        """
        Using python string indexes, since I suck at regex.
        """

        if not self.raw:
            return

        self._boolean = bool(self.raw)  # True

        self._input_output = self.raw[0:1]
        self._swift_message_type = self.raw[1:4]
        self._destination_address = self.raw[4:16]
        self._priority = self.raw[16:17]
        self._delivery_monitoring = self.raw[17:18]
        self._obsolescence_period = self.raw[18:21]




class UserHeader:
    """
    The user header is sufficiently complicated that we might want to break it
    up a bit too.
    """

    REGEX = re.compile(
        r"^"
        r"({113:(?P<bpc>[A-Z]{4})})?"
        r"({108:(?P<mur>[A-Z0-9]{0,16})})?"
        r"({111:(?P<sti>[0-9]{3})})?"
        r"({121:(?P<uetr>[a-zA-Z0-9]{8}-[a-zA-Z0-9]{4}-4[a-zA-Z0-9]{3}-[89ab][a-zA-Z0-9]{3}-[a-zA-Z0-9]{12})})?"  # NOQA: E501
        r"$"
    )

    def __init__(self, raw):

        self.raw = raw

        self.bank_priority_code = None
        self.message_user_reference = None
        self.service_type_identifier = None
        self.unique_end_to_end_transaction_reference = None

        self._boolean = False

        self._populate_by_parsing()

    def __str__(self):
        return self.raw

    def __repr__(self):
        return str(self)

    def __bool__(self):
        return self._boolean

    __nonzero__ = __bool__  # Python 2

    @property
    def bpc(self):
        return self.bank_priority_code

    @property
    def mur(self):
        return self.message_user_reference

    @property
    def sti(self):
        return self.service_type_identifier

    @property
    def uetr(self):
        return self.unique_end_to_end_transaction_reference

    def _populate_by_parsing(self):

        if not self.raw:
            return

        m = self.REGEX.match(self.raw)

        self._boolean = bool(m)

        if not m:
            return

        self.bank_priority_code = m.group("bpc")
        self.message_user_reference = m.group("mur")
        self.service_type_identifier = m.group("sti")
        self.unique_end_to_end_transaction_reference = m.group("uetr")





class Text:
    """
    With considerable help from:
      https://gist.github.com/dmcruz/9940a6b217ff701b8f3e
    """

    # fmt: off
    REGEX = re.compile(
        r"^"
        r"(:20:(?P<senders_reference>[^\s:]+)\s*)?"
        r"(:13C:/"
          r"(?P<time_indication_class>(CLSTIME|RNCTIME|SNDTIME))/"
          r"(?P<time_indication_time>[\d]{4})"
          r"(?P<time_indication_sign>[+-])"
          r"(?P<time_indication_offset>\d{4})[^:]*"
        r")*?"
        r"(:23B:(?P<bank_operation_code>[^\s:]+)\s*)?"
        r"(:23E:(?P<instruction_code>[^:]*))?"
        r"(:26T:(?P<transaction_type_code>[^:]*))?"
        r"(:32A:"
            r"(?P<date_year>\d\d)"
            r"(?P<date_month>\d\d)"
            r"(?P<date_day>\d\d)"
            r"(?P<interbank_settled_currency>[A-Z]{3})"
            r"(?P<interbank_settled_amount>[\d,]+)"
        r"\s*)?"
        r"(:33B:"
            r"(?P<original_ordered_currency>[A-Z]{3})"
            r"(?P<original_ordered_amount>[\d,]+)"
        r"\s*)?"
        r"(:36:(?P<exchange_rate>[^:]*))?"
        r"(:50[AFK]:(?P<ordering_customer>.*?)\s*(?=(:\d\d)?))?"
        r"(:51A:(?P<sending_institution>[^:]*))?"
        r"(:52[AD]:(?P<ordering_institution>.*?)\s*(?=(:\d\d)?))?"
        r"(:53[ABD]:(?P<sender_correspondent>[^\s:]*)\s*)?"
        r"(:54[ABD]:(?P<receiver_correspondent>.*?)\s*(?=(:\d\d)?))?"
        r"(:56[ACD]:(?P<intermediary>.*?)\s*(?=(:\d\d)?))?"
        r"(:57[ABCD]:(?P<account_with_institution>.*?)\s*(?=(:\d\d)?))?"
        r"(:59A?:(?P<beneficiary>.*?)\s*(?=(:\d\d)?))?"
        r"(:70:(?P<remittance_information>.*?)\s*(?=(:\d\d)?))?"
        r"(:71A:(?P<details_of_charges>.*?)\s*(?=(:\d\d)?))?"
        r"(:71F:(?P<sender_charges>[^:]*))*"
        r"(:71G:(?P<receiver_charges>[^:]*))?"
        r"(:72:(?P<sender_to_receiver_information>.*?)\s*(?=(:\d\d)?))?"
        r"(:77B:(?P<regulatory_reporting>.*?)\s*(?=(:\d\d)?))?"
        r"$",
        re.DOTALL,
    )
    # fmt: on

    def __init__(self, raw):

        self.raw = raw

        self.senders_reference = None
        self.bank_operation_code = None
        self.instruction_code = None
        self.transaction_type_code = None
        self.interbank_settled_currency = None
        self.interbank_settled_amount = None
        self.original_ordered_currency = None
        self.original_ordered_amount = None
        self.exchange_rate = None
        self.ordering_customer = None
        self.sending_institution = None
        self.ordering_institution = None
        self.sender_correspondent = None
        self.receiver_correspondent = None
        self.intermediary = None
        self.account_with_institution = None
        self.beneficiary = None
        self.remittance_information = None
        self.details_of_charges = None
        self.sender_charges = None
        self.receiver_charges = None
        self.sender_to_receiver_information = None
        self.regulatory_reporting = None

        self.date = None

        self._boolean = False

        self._populate_by_parsing()

    def __str__(self):
        return self.raw

    def __repr__(self):
        return str(self)

    def __bool__(self):
        return self._boolean

    __nonzero__ = __bool__  # Python 2

    def _populate_by_parsing(self):

        if not self.raw:
            return

        m = self.REGEX.match(self.raw)

        self._boolean = bool(m)

        if not m:
            return

        for k, v in m.groupdict().items():
            if v is None:
                continue
            if k.startswith("date_"):
                continue
            if not hasattr(self, k):
                continue
            setattr(self, k, v)

        try:
            self.date = date(
                2000 + int(m.group("date_year")),
                int(m.group("date_month")),
                int(m.group("date_day")),
            )
        except (ValueError, TypeError):
            pass  # Defaults to None
