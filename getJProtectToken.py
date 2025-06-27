import requests
import json

'''I don't think I need these, I can just pass in directly in the other file the clientID, Secret, and ServerURL
----Then return the token
clientID = ''
password = ''
protectInstance = ""
url = f"https://{protectInstance}.protect.jamfcloud.com/"
'''
def getAccessToken(serverURL, clientID, clientSecret):
    print(f"The hostname received by the get function is: {serverURL}")
    print(f"The client ID received by the get function is: {clientID}")
    print(f"The clientSecret received by the get function is: {clientSecret}")
    session = requests.Session() #initialize the session
    """Gets a reusable access token to authenticate requests to the Jamf
    Protect API"""
    authDetails = {
        "client_id": clientID,
        "password": clientSecret,
    }
    response = session.post(serverURL + "token", json=authDetails)

    """the raise_for_status is basically a better way to ensure that you didn't get a 404 or something.
    It throws a message if you get anything other than a 200-299 response"""
    response.raise_for_status()
    print(f"printing raise_for_status: {response.raise_for_status()}")
 
    responseData = response.json()
    print(response.json())
    print(
        f"Access token granted, valid for {int(responseData['expires_in'] // 60)} minutes."
    )
    """notice it's called an 'access_token' instead of just 'token' like on the Jamf Pro side"""
    print(responseData["access_token"])
    return responseData["access_token"]

#for testing: