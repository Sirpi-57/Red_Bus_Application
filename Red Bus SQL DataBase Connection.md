# **RED BUS SQL CONNECTION \- CODE EXPLANATION**

# 1.Importing Necessary Libraries:

import pandas as pd  
import mysql.connector  
import numpy as np

# 2\. Concatenating All Data:

\# csv to dataframe  
df\_bus\_1\=pd.read\_csv("APSRTC.csv")  
df\_bus\_2\=pd.read\_csv("ASTC.csv")  
df\_bus\_3\=pd.read\_csv("CTU.csv")  
df\_bus\_4\=pd.read\_csv("HRTC.csv")  
df\_bus\_5\=pd.read\_csv("KERALA\_RTC.csv")  
df\_bus\_6\=pd.read\_csv("KTCL.csv")  
df\_bus\_7\=pd.read\_csv("RSRTC.csv")  
df\_bus\_8\=pd.read\_csv("SBSTC.csv")  
df\_bus\_9\=pd.read\_csv("UPSRTC.csv")  
df\_bus\_10\=pd.read\_csv("WBTC.csv")

Final\_df\=pd.concat(\[df\_bus\_1,df\_bus\_2,df\_bus\_3,df\_bus\_4,df\_bus\_5,df\_bus\_6,  
                    df\_bus\_7,df\_bus\_8,df\_bus\_9,df\_bus\_10\],ignore\_index\=True)  
Final\_df

# 3.Final Re-Ordering & Re-Naming:

\# New Columns Order:  
new\_column\_order \= \['Route Link','Route Name', 'Start Location', 'End Location', 'Bus Name',  
    'Bus Type', 'standardized\_ac\_type', 'standardized\_seat\_type',  
    'Departure Time', 'Duration', 'Reaching Time', 'Bus Rating',  
    'Price', 'Seat Availability'\]

\# Reindexing the DataFrame to the new column order  
Final\_df \= Final\_df.reindex(columns\=new\_column\_order)  
Final\_df

\# Renaming columns  
Final\_df.rename(columns\={  
    'Route Link': 'route\_link',  
    'Route Name': 'route\_name',  
    'Start Location': 'start\_location',  
    'End Location': 'end\_location',  
    'Bus Name': 'bus\_name',  
    'Bus Type': 'bus\_type',  
    'Departure Time': 'departure\_time',  
    'Duration': 'duration',  
    'Reaching Time': 'reaching\_time',  
    'Bus Rating': 'bus\_rating',  
    'Price': 'price',  
    'Seat Availability': 'seat\_availability',  
    'Start Time': 'start\_time',  
    'End Time': 'end\_time'  
}, inplace\=True)

\# Verifying the changes  
print(Final\_df.columns)

\# Saving Dataframe as CSV:  
Final\_df.to\_csv('FINAL\_BUSES.csv', index\=False)  
Final\_df.columns

# 4.Connecting To MySQL DataBase:

\# Connecting to MySQL server  
conn \= mysql.connector.connect(  
    host\="localhost",  
    user\="root",  
    password\="\#\#\#\#\#\#\#\#\#\#",  
    database \="RED\_BUS\_DETAILS"  
)  
my\_cursor \= conn.cursor()

# 5.Create A DataBase and Table:

\# Creating database if not exists  
my\_cursor.execute("CREATE DATABASE IF NOT EXISTS RED\_BUS\_DETAILS")

\# Table Creation  
\# Creating table query:

\# Selecting the database  
my\_cursor.execute("USE RED\_BUS\_DETAILS")

\# Table Creation  
create\_table\_query \= """  
CREATE TABLE IF NOT EXISTS BusDetails (  
    id INT AUTO\_INCREMENT PRIMARY KEY,  
    route\_link VARCHAR(255),  
    route\_name VARCHAR(255),  
    start\_location VARCHAR(255),  
    end\_location VARCHAR(255),  
    bus\_name VARCHAR(255),  
    bus\_type VARCHAR(255),  
    standardized\_ac\_type VARCHAR(255),  
    standardized\_seat\_type VARCHAR(255),  
    departure\_time TIME,  
    duration TIME,  
    reaching\_time TIME,  
    bus\_rating FLOAT,  
    price FLOAT,  
    seat\_availability INT    
)  
"""

\# Executing the query  
my\_cursor.execute(create\_table\_query)

print("Table Created successfully")

# 6.SQL Query to Insert Data:

\# Preparing the SQL INSERT query  
insert\_query \= """  
INSERT INTO BusDetails (  
    route\_link,  
    route\_name,  
    start\_location,  
    end\_location,  
    bus\_name,  
    bus\_type,  
    standardized\_ac\_type,  
    standardized\_seat\_type,  
    departure\_time,  
    duration,  
    reaching\_time,  
    bus\_rating,  
    price,  
    seat\_availability  
) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)  
"""

\# Converting DataFrame to list of tuples  
data \= Final\_df\[\['route\_link', 'route\_name', 'start\_location', 'end\_location',  
                 'bus\_name', 'bus\_type', 'standardized\_ac\_type', 'standardized\_seat\_type',  
                 'departure\_time', 'duration', 'reaching\_time', 'bus\_rating',  
                 'price', 'seat\_availability'\]\].values.tolist()

\# Inserting data into the table  
my\_cursor.executemany(insert\_query, data)

\# Printing success message  
print("Values inserted successfully")

# 7.Commit and Close:

\# Commiting the changes  
conn.commit()

\# Closing the connection  
conn.close()

