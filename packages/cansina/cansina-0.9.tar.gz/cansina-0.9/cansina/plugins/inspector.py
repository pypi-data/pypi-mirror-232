import sys
import random
import requests
import hashlib


USER_AGENT = "Mozilla/5.0 (Windows; U; MSIE 10.0; Windows NT 9.0; es-ES)"
user_agent = {"user-agent": USER_AGENT}


class Inspector:
    """This class mission is to examine the behaviour of the application when on
        purpose an inexistent page is requested"""
    TEST404_OK = 0
    TEST404_MD5 = 1
    TEST404_STRING = 2
    TEST404_URL = 3
    TEST404_NONE = 4

    def __init__(self, target):
        self.target = target

    def _give_it_a_try(self):
        """Every time this method is called it will request a random resource
            the target domain. Return value is a dictionary with values as
            HTTP response code, resquest size, md5 of the content and the content
            itself. If there were a redirection it will record the new url"""
        s = []
        for n in range(0, 42):
            random.seed()
            s.append(chr(random.randrange(97, 122)))
        s = "".join(s)
        target = self.target + s

        print("Checking with %s" % target)

        page = requests.get(target, headers=user_agent, verify=False)
        content = page.content

        result = {'code': str(page.status_code),
                  'size': len(content),
                  'md5': hashlib.md5("".join(content)).hexdigest(),
                  'content': content,
                  'location': None}

        if len(page.history) >= 1:
            result['location'] = page.url

        return result

    def check_this(self):
        """Get the a request and decide what to do"""
        first_result = self._give_it_a_try()

        if first_result['code'] == '404':
            print("Got a nice 404, problems not expected")
            # Ok, resquest gave a 404 so we should not find problems
            return '', Inspector.TEST404_OK

        elif first_result['code'] == '302' or first_result['location']:
            location = first_result['location']
            return location, Inspector.TEST404_URL

        #elif first_result['code'] == '200':
        else:
            return first_result['md5'], Inspector.TEST404_MD5

        # We give up here :(
        return '', Inspector.TEST404_NONE

if __name__ == '__main__':
    i = Inspector(sys.argv[1])
    print(i.check_this())
