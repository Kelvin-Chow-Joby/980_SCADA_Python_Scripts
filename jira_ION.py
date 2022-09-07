#-------------------------------------------------------------------------------
# SECTION: Arguments
#-------------------------------------------------------------------------------
import sys
#This is where we define the issue information
projectKey = sys.argv[1]
partNumber = sys.argv[2]
quantity = sys.argv[3]

#Example issue information:
#projectKey = 'PEP' #This would be the target project key
#issueType = 'Problem' #This can be whatever issue type you want to use
#partNumber = '505123-001' #Put the target part number here - THIS NEEDS TO GET POPULATED BY A QUERY

#-------------------------------------------------------------------------------
# SECTION: Jira
#-------------------------------------------------------------------------------
#Documentation available here: https://developer.atlassian.com/server/jira/platform/jira-rest-api-examples/
from jira import JIRA
#This is where we define the connection information
jiraServer = 'https://jira.na.joby.aero' #Link to the JIRA server
workspaceEmail = 'nicholas.morris@joby.aero' #Authenticated user of choice
apiToken = 'NDI5MzQzOTEwMDY5Otq8cfEGPkJZfTjrSfl8H0Z0s/3G' #Needs to be created by an authenticated user at https://id.atlassian.com/manage-profile/security/api-tokens
# This is where we open the connection object
jira_connection = JIRA(
                        token_auth=apiToken,
                        server=jiraServer
                        )
#The following are the example methods
#Example that creates a single issue
issue_dict = {
                'project': {'key': 'PEP'},
                'summary': partNumber + ' - Inventory Depleted',
                'description': 'Inventory is depleted on p/n ' + partNumber + ', please order ' + quantity + ' more',
                'issuetype': {'name': 'Problem'},
                "customfield_11502": partNumber, #Custom field for 'part number'
                "customfield_16400": { "value": "Inventory" } #Custom field for 'problem type' dropdown
                }
new_issue = jira_connection.create_issue(fields=issue_dict) #Actual method call
#Example that creates multiple issues at once
issue_list = [
    {
        'project': {'key': projectKey},
        'summary': 'Test summary 1',
        'description': 'Test description 1',
        'issuetype': {'name': issueType},
    },
    {
        'project': {'key': projectKey},
        'summary': 'Test summary 2',
        'description': 'Test description 2',
        'issuetype': {'name': issueType},
    },
    {
        'project': {'key': projectKey},
        'summary': 'Test summary 3',
        'description': 'Test description 3',
        'issuetype': {'name': issueType},
    }]
    
#-------------------------------------------------------------------------------
# SECTION: Method Calls
#-------------------------------------------------------------------------------
jira_connection.create_issues(field_list=issue_dict)