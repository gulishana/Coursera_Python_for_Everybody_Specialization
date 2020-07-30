import urllib.request, urllib.parse, urllib.error
import oauth # This is built into Python as well
import hidden

# https://apps.twitter.com/
# Create App and get the four strings, put them in 'hidden.py'

# This 'augment' funtion was wrotten by Dr.Chuck to make it easier
# to add all the 4 OAuth parameters
def augment(url, parameters):
    secrets = hidden.oauth()
    consumer = oauth.OAuthConsumer(secrets['consumer_key'],
                                   secrets['consumer_secret'])
    token = oauth.OAuthToken(secrets['token_key'], secrets['token_secret'])

    oauth_request = oauth.OAuthRequest.from_consumer_and_token(consumer,
                    token=token, http_method='GET', http_url=url,
                    parameters=parameters)
    oauth_request.sign_request(oauth.OAuthSignatureMethod_HMAC_SHA1(),
                               consumer, token) # a signature of URL
    return oauth_request.to_url()
# 'augment' takes the values and signs in to makes a big long URL

def test_me():
    print('* Calling Twitter...')
    url = augment('https://api.twitter.com/1.1/statuses/user_timeline.json',
                  {'screen_name': 'drchuck', 'count': '2'})
    print(url)
    connection = urllib.request.urlopen(url)
    data = connection.read()
    print(data)
    headers = dict(connection.getheaders())
    print(headers)
