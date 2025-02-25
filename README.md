# ❄️ Snowflake Project

## 📌 Project Overview
The **Snowflake Project** is an automated data pipeline designed to:

1. **Download ZIP files** (The URL must be configured in `config.py`).
2. **Extract `.accdb` (Access database files)**.
3. **Read all tables from the Access database**.
4. **Upload the extracted data to Snowflake**.

---


📌 1️⃣ Clone the GitHub Repository. Run the following command in your terminal (PowerShell / Command Line / Terminal):
**git clone https://github.com/ycwang15/Snowflake-Project.git**

📌 2️⃣ Navigate to the Project Directory
**cd "Snowflake Project"**

📌 3️⃣ Install Dependencies
Ensure you have Python 3.8+ installed, then run:
**pip install -r requirements.txt**

📌 4️⃣ Configure .env File
⚠ Manually update the .env file and replace with actual credentials.

📌 5️⃣ Modify config.py
Open config.py and update the ZIP download URL.

📌 6️⃣ Run the Main Script
Execute the following command in your terminal to start the process:
**python access_to_snowflake.py**
