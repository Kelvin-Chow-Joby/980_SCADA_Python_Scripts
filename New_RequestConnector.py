from contextlib import nullcontext
from genericpath import exists
import requests
import json
import yaml
import psycopg2
import schedule
import time
import urllib
#from jira import JIRA


# Read the configuration file
with open('./RestConnector.yaml') as f:
    config = yaml.load(f, Loader=yaml.FullLoader)

# Jira REST Endpoint
baseUrl = "https://jira.na.joby.aero/"

# Pointing to different endpoints for get/post
searchSuffix = "rest/api/2/search/?jql="
createSuffix = "rest/api/2/issue/"
searchUrl= baseUrl + searchSuffix
createUrl = baseUrl + createSuffix

token = config['jira']['token']
creds =  'Bearer ' + token
headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": creds
            }


#-------------------------------------------------------------------------------
# Retrieves All PEP Inventory Tickets
#-------------------------------------------------------------------------------
def getPEPInventoryTickets():
    # Let's start with reading from Jira
    # Define a JQL, in this case, let's retrieve all PEP inventory tickets.
    invjql = 'project=PEP+AND+status+NOT+IN+(%22In+Progress%22,Done)+AND+%22Problem+Type%22=Inventory+ORDER+BY+created+DESC'

    #url = "https://jira.na.joby.aero/rest/api/2/search/?jql="
    #jql = 'project=ME+AND+issuetype=Part+AND+status+in(Open,%22In+Review%22,%22Waiting+for+support%22,Machining,QC,%22Eng+Review%22,%22FINAL+QC%22,%22On+Hold%22,%22Trim%20%26%20Drill%22,Kit,Cure,Laminate,Demold,%22In+Verification%22,%22Approved+for+Release%22,Tooling,Outsourced,%22Ready+to+Laminate%22,%22Ready+to+Cure%22,%22Dimensional+Inspection%22,NDI)+AND+component=%22Composite+Part%22+ORDER+BY+priority+DESC,due+ASC&startAt='
#   jqlkit = 'project=ME+AND+issuetype=Part+AND+status=Kit+AND+component=%22Composite+Part%22+ORDER+BY+priority+DESC,due+ASC&startAt='


    # Prepare the headers and authentication. This is my personal token. it should be replaced with a machine token or oauth2 and moved to a secrets file
    payload={}
    files={}
    headers = {
    'Authorization': 'Bearer '+ config['jira']['token']}

    # We can onlu retrieve 50 results at a time when querying the API
    startAt=0

    # Assemble our URL by concatenating the endpoint and the actual JQL
    fullurl = searchUrl + invjql
    response = requests.request("GET", fullurl, headers=headers, data=payload, files=files)
    res_json = json.loads(response.text)
        
    # Get the total number of issues
    total = res_json['total']
    print(str(total) + " Isssues retrieved")

    issuelist=[]
    # For Each issue, extract id and part number (Add more to you liking)
    for item in res_json['issues']:
        id = item['id']
        partNumber = item['fields']['customfield_11502']
        #quantity = item['fields']['customfield_XXXXX']
        
        # Now build all the retrieved items into a json dictionnary
        result = {"id": id}
        result.update({"partNumber": partNumber})

        # And append to a list of elements
        issuelist.append(result)

    # Prepare insert query
    itemstoprocess = len(issuelist)
    if itemstoprocess > 0:
        values = ""
        for item in issuelist:
            values = values + "('"+str(json.dumps(item)) + "'),"
            print(values)
        values = values[:-1]
        insertquery = 'INSERT INTO public."PEPIssues"(vals) VALUES '+values+';'
        print(insertquery)

    # Connect to our postgres database
    psqlcon = psycopg2.connect(
        user=config['psql']['user'],
        password=config['psql']['pass'],
        host=config['psql']['host'],
        port=config['psql']['port'],
        database=config['psql']['database'])
    psqlcon.autocommit = True

    deletequery = 'DELETE FROM public."PEPIssues"'
    # And execute query
    psqlcur = psqlcon.cursor()
    # TO-DO: Switch to upsert...
    psqlcur.execute(deletequery)
    psqlcur.execute(insertquery)


# OLD METHOD USING JIRA MODULE
# #-------------------------------------------------------------------------------
# # Search for existing issue
# #-------------------------------------------------------------------------------
# def searchForIssue(partNumber: str):
#     # This is where we create the connection object
#     jiraConnection = JIRA(token_auth=config['jira']['token'],server=url)
#     jqlString = 'project = "PEP" AND "cf[11502]" ~ "%s" AND status NOT IN ("In Progress","Done") ORDER BY created DESC' % partNumber
#     print('Running check for issue with part number ' + partNumber)
#     #print('JQL query: ' + jqlString)
#     getIssues = jiraConnection.search_issues(jqlString)
#     return getIssues

# OLD METHOD USING JIRA MODULE
# #-------------------------------------------------------------------------------
# # Create single issue
# #-------------------------------------------------------------------------------
# def createSingleIssue(partNumber: str, quantity: int):
#     # This is where we create the connection object
#     jiraConnection = JIRA(token_auth=config['jira']['token'],server=url)

#     issueDict = {
#                     'project': {'key': 'PEP'},
#                     'summary': partNumber + ' - Inventory Depleted',
#                     'description': 'Inventory is depleted on p/n ' + partNumber + ', please order ' + str(quantity) + ' more',
#                     'issuetype': {'name': 'Problem'},
#                     "customfield_11502": partNumber, #Custom field for 'part number'
#                     "customfield_16400": { "value": "Inventory" } #Custom field for 'problem type' dropdown
#                     }
                    
#     issueCheck = searchForIssue(partNumber=partNumber)

#     if len(issueCheck) == 0:
#         print('No existing issue found, creating new issue')
#         postSingleIssue = jiraConnection.create_issue(fields=issueDict) #Actual method call
#         print('New issue created: ' + str(postSingleIssue))
#         return postSingleIssue
#     else:
#         issueKey = issueCheck[0].key
#         print('Open ticket already exists with a matching part number: ' + str(issueKey))
#         return


# NEW METHOD USING HTTP REQUESTS
#-------------------------------------------------------------------------------
# Search for existing issue
#-------------------------------------------------------------------------------
def searchForIssue(partNumber: str):

    jqlString = 'project = "PEP" AND "cf[11502]" ~ "%s" AND status NOT IN ("In Progress","Done") ORDER BY created DESC' % partNumber
    encodedJql = urllib.parse.quote(jqlString) #Encode JQL string into a valid URL
    fullUrl = searchUrl + encodedJql
    print('Running check for issue with part number ' + partNumber)
    r = requests.get(fullUrl,headers=headers).text

    return r


# NEW METHOD USING HTTP REQUESTS
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


#-------------------------------------------------------------------------------
# Looks for Queries to be processes in Postgres
#-------------------------------------------------------------------------------
def processQueries():
    # Connect to our postgres database
    psqlcon = psycopg2.connect(
        user=config['psql']['user'],
        password=config['psql']['pass'],
        host=config['psql']['host'],
        port=config['psql']['port'],
        database=config['psql']['database'])
    psqlcon.autocommit = True

    # Read Entry in the query table
    psqlcur = psqlcon.cursor()   
    query = 'SELECT id, target, function, args FROM public."QUERYTABLE" LIMIT 1'
    psqlcur.execute(query)
    res = psqlcur.fetchall()
    psqlcur.close()
    
    if len(res) > 0:
        print("Processing "+str(res))
        print(res)
        
        targetsystem= res[0][1]
        id =res[0][0]
        function = res[0][2]
        args = res[0][3]


        # Evaluate the target system
        if targetsystem == "ion":
            print("Ion Commands Not implemented yet, come back later.")
            # Pass the query to ion  
        elif targetsystem =="jira":
            # Pass the query to jira
            # 3 Options At the time (RefreshPEPTable, getPEPIssue, CreatePEPIssue)
            if function == "refreshPEPTable":
                queryresults = getPEPInventoryTickets()
            elif function == "getPEPIssue":
                queryresults =searchForIssue(args[0])
            elif function == "createPEPIssue":
                queryresults =createSingleIssue(args[0],args[1])
            else:
                print("Unknown Query "+function+". Please pass a valid keyword (ex. refreshPEPTable, createPEPIssue).")
                psqlcur = psqlcon.cursor()   
                query = 'DELETE from public."QUERYTABLE" WHERE id = \'' + id + '\';'
                psqlcur.execute(query)

        else:
                print("Unknown Target System "+targetsystem+". Please pass a valid keyword (ex. ion, Jira).")
        # Write Results in the Results Table
        #print ("Inserting into RESULTTABLE")
        #psqlcur = psqlcon.cursor()   
        #print (queryresults)
        query = 'INSERT INTO public."RESULTTABLE"(id, json) VALUES (\''+str(id)+'\',\''+str(res[0][3])+'\');'
        
        #psqlcur.execute(query)
        psqlcur.close()

        # Clear entry in the query table
        print ("Clearing QUERYTABLE")
        psqlcur = psqlcon.cursor()   
        query = 'DELETE from public."QUERYTABLE" WHERE id = \'' + id + '\';'
        
        psqlcur.execute(query)
        psqlcur.close()
    else: 
        print("Nothing to process.")


#-------------------------------------------------------------------------------
# Main Request
#-------------------------------------------------------------------------------
def main():
    schedule.every().minute.at(":00").do(getPEPInventoryTickets)
    schedule.every().second.do(processQueries)
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    main()
