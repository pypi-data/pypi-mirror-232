import requests


def Authenticate(config:dict):
    
        payload="{\r\n    \"TenancyName\": \""+config['TenancyName']+"\",\r\n    \"UsernameOrEmailAddress\": \""+config['Username']+"\",\r\n    \"Password\": \""+config['Password']+"\"\r\n}"
        headers = {
            'Content-Type': 'application/json',
            }
        print("sending request")
        response = requests.request("POST", config['Authenticate_url'], headers=headers, data=payload, verify=False)
        print("requist succssefully")
        return response


def AddQueueItem(_config:dict,row):


        payload="{'itemData': {'Priority': 'High','Name': '"+_config['QueueName']+"','SpecificContent': {   'Name': '"+str(row["Name"])+"', 'OST Shop Id': '"+str(row["OST Shop Id"])+"', 'Bank': '"+str(row["Bank"])+"', 'Company': '"+str(row["Company"])+"', 'Payment': '"+str(row["Payment"])+"'}}}"
        headers = {
            'X-UIPATH-TenantName': _config['X-UIPATH-TenantName'],
            'Authorization': _config['Authorization'],
            'Content-Type': _config['Content-Type']
            }
        response = requests.request("POST", _config['AddQueueItem_url'], headers=headers, data=payload, verify=False)
        return response


def BulkAddQueueItem(_config:dict):
   
        payload="{'queueName': '"+_config['QueueName']+"','commitType': 'AllOrNothing','queueItems': "+str(_config['listItem'])+"}"
        print(payload)
        headers = {
            'X-UIPATH-TenantName': 'OrangeProduction',
            'Authorization': 'Bearer '+ _config['Result']+'',
            'Content-Type': 'application/json'
            }
        response = requests.request("POST", _config['bulk_url'], headers=headers, data=payload, verify=False)
        return response