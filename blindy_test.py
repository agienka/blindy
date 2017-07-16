import unittest
import blindy
import re
from unittest.mock import patch, MagicMock

POST = "POST"

PARAMETERS_RAW = ["submit=true ", " admin= 1", "phrase = {}"]
PARAMETERS_AS_LIST_WITH_PLACEHOLDER = [['submit','true'], ['admin','1'], ['phrase','{}']]
PARAMETERS_AS_LIST_WITHOUT_PLACEHOLDER = [['submit','true'], ['admin','1'], ['another-phrase','some another phrase']]
HEADERS_AS_LIST=[['X-Some-Header', 'headervalue']]
HEADERS_AS_DICT={'X-Some-Header': 'headervalue'}
HEADERS_WITH_PLACEHOLDER=[['X-Some-Header', 'sql query goes here: {}']]
PHRASE_WITHOUT_PLACEHOLDER = "some phrase"
PHRASE_WITH_PLACEHOLDER = "some phrase with {} placeholder"
SIMPLE_PAYLOAD = {'submit': 'true', 'admin': '1', 'phrase': 'some+phrase'}
SIMPLE_PAYLOAD2 = {'submit': 'true', 'admin': '1', 'another-phrase': 'some+another+phrase'}
RESPONSE = ("<html>some response</html>",200)
URL = "http://url"
PATTERN = re.compile('.*response.*')


class TestStringMethods(unittest.TestCase):


    def testsubstitute_placeholders(self):
        # when
        res = blindy.substitute_placeholders(PHRASE_WITH_PLACEHOLDER, 'placeholder', ['at', 'the', 'end'])

        # then
        self.assertEqual(res, "some phrase with {} 'at','the','end'")


    def testprepare_payloadWithPlaceholder(self):
        # when
        res = blindy.prepare_payload(PARAMETERS_AS_LIST_WITH_PLACEHOLDER, PHRASE_WITHOUT_PLACEHOLDER, True)

        # then
        self.assertEqual(res, SIMPLE_PAYLOAD)


    def testprepare_payloadWithoutPlaceholder(self):
        # when
        res = blindy.prepare_payload(PARAMETERS_AS_LIST_WITHOUT_PLACEHOLDER, PHRASE_WITHOUT_PLACEHOLDER, True)

        # then
        self.assertEqual(res, SIMPLE_PAYLOAD2)


    def testParseParameters(self):
        # when
        res = blindy.parse_parameters(PARAMETERS_RAW, '=')

        # then
        self.assertEqual(res, PARAMETERS_AS_LIST_WITH_PLACEHOLDER)


    @patch('requests.post')
    def testin_POST_request(self, reguests_post):
        # given
        reguests_post.return_value = MagicMock(status_code=200)

        #when
        blindy.in_POST_request(SIMPLE_PAYLOAD, URL, HEADERS_AS_LIST)

        # then
        reguests_post.assert_called_with(URL, data=SIMPLE_PAYLOAD, headers=HEADERS_AS_LIST)


    @patch('requests.get')
    def testin_GET_request(self, reguests_get):
        # given
        reguests_get.return_value = MagicMock(status_code=200, text='it\'s ok')

        #when
        blindy.in_GET_request(SIMPLE_PAYLOAD, URL, HEADERS_AS_LIST)

        # then
        reguests_get.assert_called_with(URL, params=SIMPLE_PAYLOAD, headers=HEADERS_AS_LIST)


    @patch('blindy.in_POST_request')
    def testnot_bruteforce(self, ipr):
        # given
        ipr.return_value = RESPONSE

        # when
        blindy.not_bruteforce(PARAMETERS_AS_LIST_WITH_PLACEHOLDER, HEADERS_AS_LIST, PHRASE_WITHOUT_PLACEHOLDER, URL, ipr, PATTERN, True, True)

        # then
        ipr.assert_called_with(SIMPLE_PAYLOAD, URL, HEADERS_AS_DICT)


    @patch('blindy.in_GET_request')
    def testPositivePatternFound(self, igr):
        # given
        igr.side_effect = [RESPONSE if (i==20 or i==39 or i==44 or i==62) else ('Not a pattern', 500) for i in range(0,len(blindy.chars)+20+38+44+62)]

        # when
        result = blindy.bruteforce(PARAMETERS_AS_LIST_WITH_PLACEHOLDER, HEADERS_AS_LIST, PHRASE_WITH_PLACEHOLDER, URL, igr, PATTERN, True, True)

        # then
        self.assertEqual(result, 'user')


    @patch('blindy.in_GET_request')
    def testNegativePatternFound(self, igr):
        # given
        igr.side_effect = [('Not a pattern', 500) if (i==20 or i==39 or i==44 or i==62) else RESPONSE for i in range(0,len(blindy.chars)+20+38+44+62)]

        # when
        result = blindy.bruteforce(PARAMETERS_AS_LIST_WITH_PLACEHOLDER, HEADERS_AS_LIST, PHRASE_WITH_PLACEHOLDER, URL, igr, PATTERN, False, True)

        # then
        self.assertEqual(result, 'user')

    @patch('blindy.run_with_callback')
    def testRun_injectionQuerySetAsList(self, run_with_callback):

        # when
        blindy.run_injection("POST", PARAMETERS_AS_LIST_WITH_PLACEHOLDER, HEADERS_AS_LIST,
                             [PHRASE_WITH_PLACEHOLDER, PHRASE_WITH_PLACEHOLDER], URL, PATTERN, False, True)

        # then
        self.assertEqual(run_with_callback.call_count, 2)

    @patch('blindy.run_with_callback')
    def testRun_injectionQuerySetAsList(self, run_with_callback):

        # when
        blindy.run_injection(POST, PARAMETERS_AS_LIST_WITH_PLACEHOLDER, HEADERS_AS_LIST,
                             PHRASE_WITH_PLACEHOLDER, URL, PATTERN, False, True)

        # then
        run_with_callback.assert_called_once_with(POST, PARAMETERS_AS_LIST_WITH_PLACEHOLDER, HEADERS_AS_LIST,
                             PHRASE_WITH_PLACEHOLDER, URL, PATTERN, False, True)

    @patch('blindy.bruteforce')
    def test_assign_POST_verb(self, bf):
        # given
        bf.return_value = RESPONSE

        # when
        blindy.run_with_callback("POST", PARAMETERS_AS_LIST_WITH_PLACEHOLDER, HEADERS_AS_LIST, PHRASE_WITH_PLACEHOLDER, URL, PATTERN, False, True)

        # then
        bf.assert_called_with(PARAMETERS_AS_LIST_WITH_PLACEHOLDER, HEADERS_AS_LIST, PHRASE_WITH_PLACEHOLDER, URL, blindy.in_POST_request, PATTERN, False, True)


    @patch('blindy.bruteforce')
    def test_assign_GET_verb(self, bf):
        # when
        blindy.run_with_callback("GET", PARAMETERS_AS_LIST_WITH_PLACEHOLDER, HEADERS_AS_LIST, PHRASE_WITH_PLACEHOLDER, URL, PATTERN, False, True)

        # then
        bf.assert_called_with(PARAMETERS_AS_LIST_WITH_PLACEHOLDER, HEADERS_AS_LIST, PHRASE_WITH_PLACEHOLDER, URL, blindy.in_GET_request, PATTERN, False, True)

    @patch('blindy.bruteforce')
    def test_injection_in_header(self, bf):
        # when
        blindy.run_with_callback("GET", PARAMETERS_AS_LIST_WITHOUT_PLACEHOLDER, HEADERS_WITH_PLACEHOLDER,
                             PHRASE_WITH_PLACEHOLDER, URL,
                             PATTERN, False, True)
        # then
        bf.assert_called_with(PARAMETERS_AS_LIST_WITHOUT_PLACEHOLDER, HEADERS_WITH_PLACEHOLDER, PHRASE_WITH_PLACEHOLDER,
                              URL,
                              blindy.in_GET_request, PATTERN, False, True)

    @patch('blindy.not_bruteforce')
    def testrun_injectionNoBruteforceIfNoPlaceholderInQuery(self, not_bruteforce):
        # when
        blindy.run_with_callback("GET", PARAMETERS_AS_LIST_WITH_PLACEHOLDER, HEADERS_AS_LIST, PHRASE_WITHOUT_PLACEHOLDER, URL, PATTERN, False, True)

        # then
        not_bruteforce.assert_called_once_with(PARAMETERS_AS_LIST_WITH_PLACEHOLDER, HEADERS_AS_LIST, PHRASE_WITHOUT_PLACEHOLDER, URL, blindy.in_GET_request, PATTERN, False, True)


if __name__ == '__main__':
    unittest.main()