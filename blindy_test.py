import unittest
import blindy
import re
from unittest.mock import patch, MagicMock

PARAMETERS_RAW = ["submit=true ", " admin= 1", "phrase = {}"]
PARAMETERS_AS_LIST_WITH_PLACEHOLDER = [['submit','true'], ['admin','1'], ['phrase','{}']]
PARAMETERS_AS_LIST_WITHOUT_PLACEHOLDER = [['submit','true'], ['admin','1'], ['another-phrase','some another phrase']]
HEADERS={'X-Some-Header', 'headervalue'}
HEADERS_WITH_PLACEHOLDER={'X-Some-Header', 'sql query goes here: {}'}
PHRASE_WITHOUT_PLACEHOLDER = "some phrase"
PHRASE_WITH_PLACEHOLDER = "some phrase with {} placeholder"
SIMPLE_PAYLOAD = {'submit': 'true', 'admin': '1', 'phrase': 'some+phrase'}
SIMPLE_PAYLOAD2 = {'submit': 'true', 'admin': '1', 'another-phrase': 'some+another+phrase'}
RESPONSE = ("<html>some response</html>",200)
HTTP_URL = "http://url"
PATTERN = re.compile('.*response.*')


class TestStringMethods(unittest.TestCase):

    def testCreateBruteQuery(self):
        # when
        res = blindy.createBruteQuery('one', PHRASE_WITH_PLACEHOLDER)

        # then
        self.assertEqual(res, "some phrase with one placeholder")


    def testCreateWord(self):
        # when
        res = blindy.createWord('strin', 'g')
        # then
        self.assertEqual(res, 'string')


    def testSubstitutePlaceholders(self):
        # when
        res = blindy.substitutePlaceholders(PHRASE_WITH_PLACEHOLDER, 'placeholder', ['at', 'the', 'end'])

        # then
        self.assertEqual(res, "some phrase with {} 'at','the','end'")


    def testPreparePayloadWithPlaceholder(self):
        # when
        res = blindy.preparePayload(PARAMETERS_AS_LIST_WITH_PLACEHOLDER, PHRASE_WITHOUT_PLACEHOLDER, True)

        # then
        self.assertEqual(res, SIMPLE_PAYLOAD)


    def testPreparePayloadWithoutPlaceholder(self):
        # when
        res = blindy.preparePayload(PARAMETERS_AS_LIST_WITHOUT_PLACEHOLDER, PHRASE_WITHOUT_PLACEHOLDER, True)

        # then
        self.assertEqual(res, SIMPLE_PAYLOAD2)


    def testParseParameters(self):
        # when
        res = blindy.parseParameters(PARAMETERS_RAW, '=')

        # then
        self.assertEqual(res, PARAMETERS_AS_LIST_WITH_PLACEHOLDER)


    @patch('requests.post')
    def testInPOSTrequest(self, reguests_post):
        # given
        reguests_post.return_value = MagicMock(status_code=200)

        #when
        blindy.inPOSTrequest(SIMPLE_PAYLOAD, HTTP_URL, HEADERS)

        # then
        reguests_post.assert_called_with(HTTP_URL, data=SIMPLE_PAYLOAD, headers=HEADERS)


    @patch('requests.get')
    def testInGETrequest(self, reguests_get):
        # given
        reguests_get.return_value = MagicMock(status_code=200, text='it\'s ok')

        #when
        blindy.inGETrequest(SIMPLE_PAYLOAD, HTTP_URL, HEADERS)

        # then
        reguests_get.assert_called_with(HTTP_URL, params=SIMPLE_PAYLOAD, headers=HEADERS)


    @patch('blindy.inPOSTrequest')
    def testNotBruteforce(self, ipr):
        # given
        ipr.return_value = RESPONSE

        # when
        blindy.notBruteForce(PARAMETERS_AS_LIST_WITH_PLACEHOLDER, HEADERS, PHRASE_WITHOUT_PLACEHOLDER, HTTP_URL, ipr, PATTERN, True, True)

        # then
        ipr.assert_called_with(SIMPLE_PAYLOAD, HTTP_URL, HEADERS)


    @patch('blindy.bruteforce')
    def testRunInjectionPOST(self, bf):
        # given
        bf.return_value = RESPONSE

        # when
        blindy.runInjection("POST", PARAMETERS_AS_LIST_WITH_PLACEHOLDER, HEADERS,[PHRASE_WITH_PLACEHOLDER, PHRASE_WITH_PLACEHOLDER], HTTP_URL, PATTERN, False, True)

        # then
        bf.assert_called_with(PARAMETERS_AS_LIST_WITH_PLACEHOLDER, HEADERS, PHRASE_WITH_PLACEHOLDER, HTTP_URL, blindy.inPOSTrequest, PATTERN, False, True)


    @patch('blindy.bruteforce')
    def testRunInjectionGET(self, bf):
        # when
        blindy.runInjection("GET", PARAMETERS_AS_LIST_WITH_PLACEHOLDER, HEADERS, [PHRASE_WITH_PLACEHOLDER, PHRASE_WITH_PLACEHOLDER], HTTP_URL, PATTERN, False, True)

        # then
        bf.assert_called_with(PARAMETERS_AS_LIST_WITH_PLACEHOLDER, HEADERS, PHRASE_WITH_PLACEHOLDER, HTTP_URL, blindy.inGETrequest, PATTERN, False, True)

    @patch('blindy.bruteforce')
    def testInjectionInHeader(self, bf):
        # when
        blindy.runInjection("GET", PARAMETERS_AS_LIST_WITHOUT_PLACEHOLDER, HEADERS_WITH_PLACEHOLDER,
                            [PHRASE_WITH_PLACEHOLDER], HTTP_URL,
                            PATTERN, False, True)
        # then
        bf.assert_called_with(PARAMETERS_AS_LIST_WITHOUT_PLACEHOLDER, HEADERS_WITH_PLACEHOLDER, PHRASE_WITH_PLACEHOLDER,
                              HTTP_URL,
                              blindy.inGETrequest, PATTERN, False, True)

    @patch('blindy.notBruteForce')
    def testRunInjectionNoBruteforceIfNoPlaceholderInQuery(self, notBruteForce):
        # when
        blindy.runInjection("GET", PARAMETERS_AS_LIST_WITH_PLACEHOLDER, HEADERS, [PHRASE_WITHOUT_PLACEHOLDER], HTTP_URL, PATTERN, False, True)

        # then
        notBruteForce.assert_called_once_with(PARAMETERS_AS_LIST_WITH_PLACEHOLDER, HEADERS, PHRASE_WITHOUT_PLACEHOLDER, HTTP_URL, blindy.inGETrequest, PATTERN, False, True)


    @patch('blindy.inGETrequest')
    def testPositivePatternFound(self, igr):
        # given
        igr.side_effect = [RESPONSE if (i==20 or i==39 or i==44 or i==62) else ('Not a pattern', 500) for i in range(0,len(blindy.chars)+20+38+44+62)]

        # when
        result = blindy.bruteforce(PARAMETERS_AS_LIST_WITH_PLACEHOLDER, HEADERS, PHRASE_WITH_PLACEHOLDER, HTTP_URL, igr, PATTERN, True, True)

        # then
        self.assertEqual(result, 'user')


    @patch('blindy.inGETrequest')
    def testNegativePatternFound(self, igr):
        # given
        igr.side_effect = [('Not a pattern', 500) if (i==20 or i==39 or i==44 or i==62) else RESPONSE for i in range(0,len(blindy.chars)+20+38+44+62)]

        # when
        result = blindy.bruteforce(PARAMETERS_AS_LIST_WITH_PLACEHOLDER, HEADERS, PHRASE_WITH_PLACEHOLDER, HTTP_URL, igr, PATTERN, False, True)

        # then
        self.assertEqual(result, 'user')


if __name__ == '__main__':
    unittest.main()