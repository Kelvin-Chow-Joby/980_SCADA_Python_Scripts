#Documentation available here: https://developer.atlassian.com/server/jira/platform/jira-rest-api-examples/
from jira import JIRA

#-------------------------------------------------------------------------------
# SECTION: Arguments
#-------------------------------------------------------------------------------

#Example issue information:
#projectKey = 'PEP' #This would be the target project key
#issueType = 'Problem' #This can be whatever issue type you want to use
#partNumber = '505123-001' #Put the target part number here - THIS NEEDS TO GET POPULATED BY A QUERY

#-------------------------------------------------------------------------------
# Setup JIRA connection
#-------------------------------------------------------------------------------

jiraServer = 'https://jira.na.joby.aero' #Link to the JIRA server
workspaceEmail = 'nicholas.morris@joby.aero' #Authenticated user of choice
apiToken = 'NDI5MzQzOTEwMDY5Otq8cfEGPkJZfTjrSfl8H0Z0s/3G' #Needs to be created by an authenticated user at https://id.atlassian.com/manage-profile/security/api-tokens

# This is where we create the connection object
jiraConnection = JIRA(
                        token_auth=apiToken,
                        server=jiraServer
                        )


#-------------------------------------------------------------------------------
# Search for existing issue
#-------------------------------------------------------------------------------
def searchForIssue(partNumber: str):
    jqlString = 'project = "PEP" AND "cf[11502]" ~ "%s" AND status NOT IN ("In Progress","Done") ORDER BY created DESC' % partNumber
    print('Running check for issue with part number ' + partNumber)
    #print('JQL query: ' + jqlString)
    getIssues = jiraConnection.search_issues(jqlString)
    return getIssues


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
                    
    issueCheck = searchForIssue(partNumber=partNumber)

    if len(issueCheck) == 0:
        print('No existing issue found, creating new issue')
        postSingleIssue = jiraConnection.create_issue(fields=issueDict) #Actual method call
        print('New issue created: ' + str(postSingleIssue))
        return postSingleIssue
    else:
        issueKey = issueCheck[0].key
        print('Open ticket already exists with a matching part number: ' + str(issueKey))
        return


#-------------------------------------------------------------------------------
# Create multiple issues
#-------------------------------------------------------------------------------
# def createMultipleIssues(issueList):
#     issue_list = [
#                     {
#                         'project': {'key': 'PEP'},
#                         'summary': partNumber + ' - Inventory Depleted',
#                         'description': 'Inventory is depleted on p/n ' + partNumber + ', please order ' + str(quantity) + ' more',
#                         'issuetype': {'name': 'Problem'},
#                         "customfield_11502": partNumber, #Custom field for 'part number'
#                         "customfield_16400": { "value": "Inventory" } #Custom field for 'problem type' dropdown
#                     },
#                     {
#                         'project': {'key': 'PEP'},
#                         'summary': partNumber + ' - Inventory Depleted',
#                         'description': 'Inventory is depleted on p/n ' + partNumber + ', please order ' + str(quantity) + ' more',
#                         'issuetype': {'name': 'Problem'},
#                         "customfield_11502": partNumber, #Custom field for 'part number'
#                         "customfield_16400": { "value": "Inventory" } #Custom field for 'problem type' dropdown
#                     },
#                     {
#                         'project': {'key': 'PEP'},
#                         'summary': partNumber + ' - Inventory Depleted',
#                         'description': 'Inventory is depleted on p/n ' + partNumber + ', please order ' + str(quantity) + ' more',
#                         'issuetype': {'name': 'Problem'},
#                         "customfield_11502": partNumber, #Custom field for 'part number'
#                         "customfield_16400": { "value": "Inventory" } #Custom field for 'problem type' dropdown
#                     }
#                     ]
        
#     postMultipleIssues = jiraConnection.create_issues(field_list=issueList)
#     print('postMultipleIssues response: ' + postMultipleIssues)
#     return postMultipleIssues

test = createSingleIssue(partNumber='200644-005_A', quantity=1)