import os
import requests
import zipfile
import io
import pyodbc
import pandas as pd
import tempfile
import snowflake.connector
from snowflake.connector.pandas_tools import write_pandas
from dotenv import load_dotenv
import config 

# load .env file
load_dotenv()

# Step 1: Download the ZIP file from the URL
def download_and_extract_zip_in_memory():
    url = config.ZIP_DOWNLOAD_URL  # read URL from .env file
    print(f"Downloading ZIP file from: {url}")

    response = requests.get(url)
    response.raise_for_status()

    # Load the ZIP file into memory
    zip_data = io.BytesIO(response.content)
    print("The ZIP file is loaded into memory.")

    # Unzip the ZIP file into memory
    with zipfile.ZipFile(zip_data, 'r') as zip_ref:
        file_list = zip_ref.namelist()
        print(f"Files included in the ZIP file: {file_list}")

        # Find `.accdb` files
        accdb_filename = next((f for f in file_list if f.endswith('.accdb')), None)
        if not accdb_filename:
            raise FileNotFoundError("No .accdb file was found in the ZIP file.")

        # Extract the .accdb file into memory
        accdb_data = zip_ref.read(accdb_filename)
        print(f"Extracted .accdb file: {accdb_filename}")
        return io.BytesIO(accdb_data), accdb_filename


# Step 2: Read the table in the Access database
def process_access_database(accdb_file):
    print("Connecting to the Access database...")

    # Use tempfile to create a temporary file
    with tempfile.NamedTemporaryFile(suffix=".accdb", delete=False) as temp_file:
        temp_file.write(accdb_file.getbuffer())  # Write the file in memory to a temporary file
        temp_file_path = temp_file.name  # Get the temporary file path

    print(f"Temporary file created: {temp_file_path}")

    # Connect to the Access database
    connection = pyodbc.connect(
        r"Driver={Microsoft Access Driver (*.mdb, *.accdb)};DBQ=" + temp_file_path + ";"
    )
    cursor = connection.cursor()

    # Get all table names
    table_names = [table.table_name for table in cursor.tables() if table.table_type == 'TABLE']
    print(f"Found {len(table_names)} tables: {table_names}")

    tables_data = {}

    # Read tables one by one
    for table in table_names:
        print(f"Reading table: {table}")
        query = f"SELECT * FROM [{table}]"
        df = pd.read_sql(query, connection)
        tables_data[table] = df

    connection.close()
    print("All tables have been read.")

    return tables_data


# Step 3: Upload to Snowflake
def upload_to_snowflake(tables_data):
    print("Connecting to Snowflake...")

    conn = snowflake.connector.connect(
        user=os.getenv("SNOWFLAKE_USER"),
        password=os.getenv("SNOWFLAKE_PASSWORD"),
        account=os.getenv("SNOWFLAKE_ACCOUNT"),
        authenticator=os.getenv("SNOWFLAKE_AUTH"),
        warehouse=os.getenv("SNOWFLAKE_WAREHOUSE"),
        database=os.getenv("SNOWFLAKE_DATABASE"),
        schema=os.getenv("SNOWFLAKE_SCHEMA"),
        role=os.getenv("SNOWFLAKE_ROLE")
    )

    cursor = conn.cursor()

    def map_dtype(dtype):
        if dtype == "int64":
            return "NUMBER(38,0)" 
        elif dtype == "float64":
            return "FLOAT"  
        else:
            return "VARCHAR(16777216)"  

    for table_name, df in tables_data.items():
        print(f"Uploading table: {table_name} ({len(df)} rows)")

        try:
            table_name_upper = table_name.upper()
            create_table_sql = f"""
            CREATE OR REPLACE TABLE {table_name_upper} (
                {', '.join([f'"{col}" {map_dtype(str(df[col].dtype))}' for col in df.columns])}
            );
            """
            print(f"Executing: {create_table_sql}")
            cursor.execute(create_table_sql)

            success, num_chunks, num_rows, _ = write_pandas(conn, df, table_name_upper)

            if success:
                print(f"✅ Successfully uploaded {num_rows} rows to {table_name_upper}")
            else:
                print(f"⚠️ Upload to {table_name_upper} partially succeeded: {num_rows} rows uploaded")

        except Exception as e:
            print(f"❌ Error uploading {table_name_upper}: {str(e)}")

    cursor.close()
    conn.close()
    print("All tables uploaded successfully!")


# Step 4: Main program execution
if __name__ == "__main__":
    # ✅ download Access database from the URL in config.py file
    accdb_file, accdb_filename = download_and_extract_zip_in_memory()

    # ✅ Data Processing/Transfrom
    tables_data = process_access_database(accdb_file)

    # ✅ Upload data to Snowflake
    upload_to_snowflake(tables_data)
