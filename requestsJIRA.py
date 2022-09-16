import requests
import json
import urllib

# Jira REST Endpoint
baseUrl = "https://jira.na.joby.aero/"
searchSuffix = "rest/api/2/search/?jql="
createSuffix = "rest/api/2/issue/"
searchUrl= baseUrl + searchSuffix
createUrl = baseUrl + createSuffix

token = 'NDI5MzQzOTEwMDY5Otq8cfEGPkJZfTjrSfl8H0Z0s/3G'
creds =  'Bearer ' + token
headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": creds
            }

#-------------------------------------------------------------------------------
# Search for existing issue
#-------------------------------------------------------------------------------
def searchForIssue(partNumber: str):
    # This is where we create the connection object
    #jiraConnection = JIRA(token_auth=config['jira']['token'],server=url)
    jqlString = 'project = "PEP" AND "cf[11502]" ~ "%s" AND status NOT IN ("In Progress","Done") ORDER BY created DESC' % partNumber
    encodedJql = urllib.parse.quote(jqlString)
    print('Running check for issue with part number ' + partNumber)
    fullUrl = searchUrl + encodedJql
    r = requests.get(fullUrl,headers=headers).text

    return r

#-------------------------------------------------------------------------------
# Create single issue
#-------------------------------------------------------------------------------
def createSingleIssue(partNumber: str, quantity: int):

    issueDict = {
                    'project': {'key': 'PEP'},
                    'summary': partNumber + ' - Inventory Depleted',
                    'description': 'Inventory is depleted on p/n ' + partNumber + ', please order ' + str(quantity) + ' more',
                    'issuetype': {'name': 'Problem'},
                    "customfield_11502": partNumber, #Custom field for 'part number'
                    "customfield_16400": { "value": "Inventory" } #Custom field for 'problem type' dropdown
                    }

    payload = {"fields" : issueDict}

    issueCheck = searchForIssue(partNumber=partNumber)
    issueCheck = json.loads(issueCheck)
    totalIssues = issueCheck.get('total')

    if totalIssues == 0:
        print('No existing issue found, creating new issue')
        r = requests.post(createUrl, headers=headers, json=payload).text
        r = json.loads(r)
        print('New issue created: ' + r.get('key'))
        return
    else:
        issueString = 'Open ticket(s) already exist with a matching part number: '
        issueList = issueCheck.get('issues')
        for issue in issueList:
            issueKey = issue.get('key')
            issueString = issueString + issueKey + ' '
        print(issueString)
        return
