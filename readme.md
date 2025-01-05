# Commands for Setting Up and Using a Python Virtual Environment

# 1. Create a Virtual Environment
python3 -m venv myenv

# 2. Activate the Virtual Environment (macOS/Linux)
source myenv/bin/activate

# 3. Install MySQL Connector
pip install mysql-connector-python

# 4. For command help 
python3 main.py -h

# 5. Run Your Python Script
python3 main.py -u database_username -H database_host -d database_name -P database_port -c compound_id -p database_password

 