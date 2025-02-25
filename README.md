# Snowflake-Project
## 🚀 Project Overview
The **Snowflake Project** is an automated data pipeline designed to:
1. **Download ZIP files** (The URL must be configured in `config.py`).
2. **Extract `.accdb` (Access database files)**.
3. **Read all tables from the Access database**.
4. **Upload the extracted data to Snowflake**.

---

## 📥 **How to Clone the Repository**
### **1️⃣ Clone the GitHub Repository**
Run the following command in your **terminal (PowerShell / Command Line / Terminal)**:
```bash
git clone https://github.com/ycwang15/Snowflake-Project.git

### **2️⃣Then navigate to the project directory:**
cd "Snowflake Project"

### **3️⃣Make sure you have Python 3.8+ installed. Then, install the required dependencies:**
pip install -r requirements.txt


### **4️⃣Manually update your .env file**
⚠️ Make sure to replace your_username and your_password with actual credentials!

### **5️⃣Modify config.py**
Open the config.py file and update the ZIP download URL.

### **6️⃣Execute the Main Script**
Run the following command in the terminal:
python access_to_snowflake.py
