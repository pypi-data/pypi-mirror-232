#import all dependencies needed for the tools functions
try:
    import cx_Oracle
    import pandas
    import logging
    import datetime
    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText
    from email.mime.base import MIMEBase
    from email.header import decode_header
    from email import encoders
    import email
    import smtplib
    import imaplib
    import pysftp
    from sqlalchemy import create_engine

except Exception as error:
    print("import fastsetup - could not import library dependencies.")
    raise Exception(str(error))



def check_type(_argument, _type, _function_name):
    if not isinstance(_argument, _type):
        raise TypeError("fastsetup "+ _function_name +" - wrong data type passed in: " + str(_type))

#---------------------------------------------------------------------------------------------------------------------#
def main_log(_log_folder_path:str):
    
    try:
        #create a log file with today's date and define its format and set the level to DEBUG
        logging.basicConfig(filename=_log_folder_path + datetime.datetime.now().strftime( '%d-%m-%Y.log' ),
                            filemode='a',
                            format='Line: %(lineno)d - Time: %(asctime)s - Position: %(name)s - Status: %(levelname)s - Message: %(message)s',
                            datefmt='%H:%M:%S',
                            level=logging.DEBUG)
    except Exception as error:
        print("fastsetup main_log - could not create a log.")
        raise Exception("error: " + str(error))
   
    
    # create the main log names 
    loggerMain = logging.getLogger( '__main__' )
    loggerInit = logging.getLogger( '__init__' )
    loggerProcess = logging.getLogger( '__process__' )


    
    return loggerMain, loggerInit, loggerProcess
#---------------------------------------------------------------------------------------------------------------------#
def custom_log(_log_folder:str, _log_name:str, _log_format:str = None):
    
    # if the log_foramt string empty the format will be set to default 
    if _log_format == None:
       _log_format = 'Line: %(lineno)d - Time: %(asctime)s - Position: %(name)s - Status: %(levelname)s - Message: %(message)s' 
       print("no special format picked, "+str(_log_name)+" will have the main_log format")
    
    try:  
        # create a log file with today's date and name of your log and define its format as specified and set the level to DEBUG
        logging.basicConfig(filename=_log_folder + '__'+_log_name+'__' +datetime.datetime.now().strftime( '%d-%m-%Y.log' ),
                        filemode='a',
                        format=_log_format,
                        datefmt='%H:%M:%S',
                        level=logging.DEBUG)
    except Exception as error:
        print("fastsetup custom_log - could not create a log.")
        raise Exception("error: " + str(error))
    
    
    #create the main log name
    customLog = logging.getLogger('__'+_log_name+'__')
    
    return customLog
#---------------------------------------------------------------------------------------------------------------------#
def get_config(_config_path:str):
    # gets data from config excel sheet file
    dfs = []
    try:
        xls = pandas.ExcelFile(_config_path)
    except Exception as error:
        print("fastsetup get_config - could not read excel file path")
        raise Exception("error: " + str(error))
    
    for sheet_name in xls.sheet_names:
        df = xls.parse(sheet_name)
        dfs.append(df)

    try:
        combined_df = pandas.concat(dfs, ignore_index=True)
        combined_df['key'] = combined_df['key'].astype(str)
        combined_df['value'] = combined_df['value'].astype(str)
    except Exception as error:
        print("fastsetup get_config - could not find key or value columns")
        raise Exception("error: " + str(error))
    
    for index,row in df.iterrows():
        config = combined_df.set_index('key')['value'].to_dict()

    return config
#---------------------------------------------------------------------------------------------------------------------#
def SMTP(_config:dict):
    # sents an email with or without an attachment
    # getting all the email components
    file_name = _config['file_name']
    sender_email = _config['sender_email']
    to_email = _config['to_email'].split(';')
    email_subject = _config['email_subject']
    sender_email = _config['sender_email']
    body_type = _config['body_type']
    try: 
        body = _config['body']
    except Exception as error:
        print("fastsetup SMTP - ATTENTION: Email has no body or the implementation in the config is wrong.")
    try:
        cc = _config['cc'].split(';')
    except Exception as error:
        print("fastsetup SMTP - ATTENTION: Email has no CC recipient/s or the implementation in the config is wrong.")
    try:
        attachments = _config['attachments'].split(';')
    except Exception as error:
        print("fastsetup SMTP - ATTENTION: Email has no attachment/s or the implementation in the config is wrong.")


    ###################################################################################################################
    # Build the body of the Email
    message = MIMEMultipart('alternative')
    message["From"] = sender_email
    message['To'] = ', '.join(to_email)
    message["Subject"] = email_subject
    try:    
        message["CC"] = ', '.join(cc)
        recipients = to_email + cc
    except:
        recipients = to_email
    message.attach(MIMEText(body, body_type))

    print("fastsetup SMTP - email setup successfully")
    ###################################################################################################################
    # iterate through all the files and attache them with the email
    try:
        for attachment_path in attachments:
            # attach the files
            with open(attachment_path, "rb") as attachment:
                file = MIMEBase("application", "octet-stream")
                file.set_payload(attachment.read())
        
            # Encode file in ASCII characters to send by email
            encoders.encode_base64(file)
            # add name for the file
            file.add_header("Content-Disposition",f"attachment; filename= {file_name}",)
            # Add attachment to message and convert message to string
            message.attach(file)
            text = message.as_string()
    except Exception as error:
        print("fastsetup SMTP_send - could not add attachments")
        raise Exception("error: " + str(error))

    print("fastsetup SMTP - added attachments successfully")
    ################################################################################################################### 
    # connect to the server and send the email
    try:
        with smtplib.SMTP(_config['server'], _config['port']) as server:
             server.sendmail(sender_email, recipients, text)
    except Exception as error:
        print("fastsetup SMTP - could not send the email")
        raise Exception("error: " + str(error))

    print("fastsetup SMTP - email Sent \n")
#---------------------------------------------------------------------------------------------------------------------#
def IMAP(_config:dict):
    # Connect to the IMAP server (for Gmail, use 'imap.gmail.com')
    imap_server = imaplib.IMAP4_SSL('imap.gmail.com')

    # Log in to your email account
    imap_server.login(_config['username'], _config['password'])

    mailbox = 'inbox'
    imap_server.select(mailbox)

    search_subject = _config['search_subject']
    search_criteria = f'(SUBJECT "{search_subject}")'
    status, email_ids = imap_server.search(None, search_criteria)
    email_id_list = email_ids[0].split()
    # Sort the email IDs by date in descending order (most recent first)
    email_id_list.sort(reverse=True)

    # Fetch the most recent email
    if email_id_list:
        most_recent_email_id = email_id_list[0]
    
        # Fetch the email content based on the email ID
        status, email_data = imap_server.fetch(most_recent_email_id, '(RFC822)')

        # Parse the email content
        raw_email = email_data[0][1]
        email_message = email.message_from_bytes(raw_email)

        # Extract email details (subject, sender, date, etc.)
        subject, encoding = decode_header(email_message['Subject'])[0]
        from_, encoding = decode_header(email_message['From'])[0]
        date, encoding = decode_header(email_message['Date'])[0]

        # Process the email body (text or HTML content)
        if email_message.is_multipart():
            for part in email_message.walk():
                content_type = part.get_content_type()
                content_disposition = str(part.get("Content-Disposition"))

            if "attachment" not in content_disposition:
                body = part.get_payload(decode=True).decode()
                print(f"Content Type: {content_type}")
                print(f"Body:\n{body}")
            else:
                print("No emails found with the specified subject.")

    # Logout and close the connection
    imap_server.logout()
#---------------------------------------------------------------------------------------------------------------------#
def SFTP_download(_config:dict):

    # to get the hostkeys for the sftp
    cnopts = pysftp.CnOpts()
    cnopts.hostkeys = None
    try:
        # SFTP connection
        with pysftp.Connection(host = _config['host'], username = _config['user_name'], password= _config['password'] , port = int(_config['SFTP_port']) , cnopts = cnopts) as sftp:        
            try:
                # this to enter the file location before iteration  
                sftp.cwd(_config['server_folder_name'])
            except Exception as error:
                print("fastsetup SFTP_download - could not find server_folder_name")
                raise Exception("error: " + str(error))
            #######################################################
            # this for loop iterate through all ziped files until it fineds the required file
            directory_structure = sftp.listdir_attr()
            for attr in directory_structure:
                attr_file_name = str(attr.filename)
                if attr_file_name == _config['server_file_name']:
                   remoteFilePath = attr_file_name
            #######################################################
            # gets the required ziped file
            try:        
                file =  sftp.get(remoteFilePath, _config['local_file_path'])
                print("SFTP download - downloaded file successfully")
            except Exception as error:
                print("fastsetup SFTP_download - could not get file from the server")
                raise Exception("error: " + str(error))
            # close the connection
            sftp.close()
    except Exception as error:
        print("fastsetup SFTP_download - could not connect to the server")
        raise Exception("error: " + str(error))    
    return file
#---------------------------------------------------------------------------------------------------------------------#
def SFTP_upload(_config:dict):

    # to get the hostkeys for the sftp
    cnopts = pysftp.CnOpts()
    cnopts.hostkeys = None
    try:
        # SFTP connection
        with pysftp.Connection(host = _config['host'], username = _config['user_name'], password= _config['password'] , port = int(_config['SFTP_port']) , cnopts = cnopts) as sftp:
            print("SFTP upload - connection successful")

            try:
                #call sftp.put() method to upload file to server
                sftp.put(_config['local_file'], _config['target_location'])
                print("SFTP upload - upload successful")
            except Exception as error:
                print("fastsetup SFTP_upload - could not upload the file")
                raise Exception("error: " + str(error))

            # close the connection
            sftp.close()      
            print("SFTP upload - connection closed successful \n")
    except Exception as error:
        print('fastsetup SFTP_upload - could not connect to the server')
        raise Exception("error: " + str(error))
#---------------------------------------------------------------------------------------------------------------------#
def oracle_download(_config:dict):
    try:
        dsn = cx_Oracle.makedsn(_config['host'], _config['port'], service_name = _config['data_source'])
    except Exception as error:
        print("fastsetup oracle_download - could not make dsn")
        raise Exception("error: " + str(error))
    
    try:
        connection = cx_Oracle.connect(user=_config['user_ID'], password=_config['password'], dsn=dsn)
        print("fastsetup oracle_download - connected to oracle database")
    except Exception as error:
        print("fastsetup oracle_download - could not connect to oracle")
        raise Exception("error: " + str(error))    
    
    try:
        df = pandas.read_sql(_config['query'], con=connection)
        print("fastsetup oracle_download - query found")
    except Exception as error:
        print("fastsetup oracle_download - could not find the query")
        raise Exception("error: " + str(error))
              
    connection.close()
    print("fastsetup oracle_download - connection closed. \n")
    
    return df
#---------------------------------------------------------------------------------------------------------------------#
def oracle_upload(_config:dict, dataframe:pandas.DataFrame):
    try:
        dsn = cx_Oracle.makedsn(_config['host'], _config['port'], service_name = _config['data_source'])
    except Exception as error:
        print("fastsetup oracle_download - could not make dsn")
        raise Exception("error: " + str(error))
    
    try:
        connection = cx_Oracle.connect(user=_config['user_ID'], password=_config['password'], dsn=dsn)
        print("fastsetup oracle_download - connected to oracle database")
    except Exception as error:
        print("fastsetup oracle_download - could not connect to oracle")
        raise Exception("error: " + str(error))    
    
    try:
        dataframe.to_sql(_config['query'], con=connection)
        print("fastsetup oracle_download - query found")
    except Exception as error:
        print("fastsetup oracle_download - could not find the query")
        raise Exception("error: " + str(error))
              
    connection.close()
    print("fastsetup oracle_download - connection closed. \n")
#---------------------------------------------------------------------------------------------------------------------#
def sql_upload(config:dict, df_to_upload:pandas.DataFrame = None):
    check_type(config, dict, "sql_upload")
    check_type(df_to_upload, pandas.DataFrame, "sql_upload")

    if df_to_upload == None:
        file = config["file_path"]

    try:
        engine = create_engine("mssql+pyodbc://"+config['username']+":"+config['password']+"@"+config['servername']+"/"+config['database']+ "?driver=SQL+Server") 
    except Exception as error:
        print("fastsetup SQL_upload - could not create engine")
        raise Exception("error: " + str(error))
    try:
        file.to_sql(config['table_name'], con=engine, if_exists='append')
        print("sql upload successfully")
    except Exception as error:
        print("fastsetup sql_upload - could not upload file")
        raise Exception("error: " + str(error))
#---------------------------------------------------------------------------------------------------------------------#   
def sql_download(config:dict, dataframe:pandas.DataFrame):
    check_type(config, dict, "sql_upload")
    check_type(dataframe, pandas.DataFrame, "sql_upload")

    if dataframe == None:
        file = config["file_path"]

    try:
        engine = create_engine("mssql+pyodbc://"+config['username']+":"+config['password']+"@"+config['servername']+"/"+config['database']+ "?driver=SQL+Server") 
    except Exception as error:
        print("fastsetup SQL_upload - could not create engine")
        raise Exception("error: " + str(error))
    try:
        dataframe = pandas.to_sql(config['table_name'], con=engine, if_exists='append')
        print("sql upload successfully")
    except Exception as error:
        print("fastsetup sql_upload - could not upload file")
        raise Exception("error: " + str(error))
    return dataframe