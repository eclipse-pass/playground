import argparse
import json
from base64 import b64encode

try:
    import requests
except:
    print("Please run: pip install requests")
    exit()

try:
    from nacl import encoding, public
except:
    print("Please run: pip install pynacl")
    exit()

parser = argparse.ArgumentParser(prog='github_secrets.py')
parser.add_argument('-u', '--user', required=True, nargs='?', action="store", dest='user', help='Your GitHub username')
parser.add_argument('-t', '--token', required=True, nargs='?', action="store", dest='token', help='A GitHub personal access token with repo access')
parser.add_argument('-r', '--repo', required=True, nargs='?', action="store", dest='repo', help='The name of the GitHub repository containing the secret')
parser.add_argument('-n', '--name', required=True, nargs='?', action="store", dest='name', help='Name of the secret')
parser.add_argument('-v', '--value', required=False, nargs='?', action="store", dest='value', help='The unencoded value to be set for the secret. If not included, the secret metadata will be fetched.')
argresults = parser.parse_args()

repoUrl = "https://api.github.com/repos/eclipse-pass/" + argresults.repo
headers = {"Accept":"application/vnd.github.v3+json"}

if argresults.value:
    # First we fetch the public key to use for encoding
    result = requests.get(repoUrl + "/actions/secrets/public-key", headers=headers, auth=(argresults.user, argresults.token))
    publicKeyData = result.json()

    # Encrypt the secret before sending it
    public_key = publicKeyData["key"]
    public_key = public.PublicKey(public_key.encode("utf-8"), encoding.Base64Encoder())
    sealed_box = public.SealedBox(public_key)
    encrypted = sealed_box.encrypt(argresults.value.encode("utf-8"))
    encodedValue = b64encode(encrypted).decode("utf-8")

    # Send the request to set the secret
    data = '{"encrypted_value":"' + encodedValue + '","key_id":"' + publicKeyData["key_id"] + '"}'
    secretUrl = repoUrl + "/actions/secrets/" + argresults.name
    result = requests.put(secretUrl, data=data, headers=headers, auth=(argresults.user, argresults.token))
    if result.status_code == requests.codes.no_content:
        print("\nYour secret has been updated!")
    else:
        print("\nERROR! Your secret was not updated: " + result.reason + "(" + str(result.status_code) + ")")
else:
    result = requests.get(repoUrl + "/actions/secrets/" + argresults.name, headers=headers, auth=(argresults.user, argresults.token))
    secretMetadata = result.json()
    print(json.dumps(secretMetadata))
