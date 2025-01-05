import argparse
import mysql.connector
import sys
import uuid
import json  

parser = argparse.ArgumentParser(description="Connect to MySQL and fetch a compound by ID.")
parser.add_argument("-u", "--user", required=True, help="MySQL username")
# parser.add_argument("-p", "--password", required=True, help="MySQL password")
parser.add_argument("-H", "--host", required=True, help="MySQL host")  # Changed from -h to -H
parser.add_argument("-d", "--database", required=True, help="Database name")
parser.add_argument("-P", "--port", required=True, type=int, help="MySQL port")
parser.add_argument("-c", "--compound_id", required=True, help="Compound ID to fetch")

args = parser.parse_args()

try:
    connection = mysql.connector.connect(
        host=args.host,
        port=args.port,
        user=args.user,
        # password=args.password,
        database=args.database
    )

    cursor = connection.cursor(dictionary=True)

    query = "SELECT * FROM compounds WHERE id = %s"
    cursor.execute(query, (args.compound_id,))

    compound = cursor.fetchone()
    if not compound:
        print(f"Compound with ID {args.compound_id} not found.")
        sys.exit(1)

    # Insert the units
    with open('units.json', 'r') as f:
        data = f.read()
        json_data = json.loads(data)  # Corrected json.dump to json.loads

        for zone in json_data:
            zone_id = str(uuid.uuid4())

            name = zone['name']
            insert_query = """
            INSERT INTO zones (id, name, compound_id, created_at, updated_at)
            VALUES (%s, %s, %s, NOW(), NOW())
            """
            result = cursor.execute(insert_query, (zone_id, name, compound['id']))
            unit_blocks = zone['blocks']
            for block in unit_blocks:
                unit_block_id = str(uuid.uuid4())
                unit_block_name = block['block']
                insert_query = """
                INSERT INTO unit_blocks (id, name, compound_id, zone_id, created_at, updated_at)
                VALUES (%s, %s, %s, %s, NOW(), NOW())
                """
                cursor.execute(insert_query, (
                    unit_block_id,
                    unit_block_name,
                    compound['id'],
                    zone_id
                ))
                units = block['units']
                for unit in units:
                    unit_id = str(uuid.uuid4())  # Added to match variable used
                    insert_query = """
                    INSERT INTO units (id, number, notes, unit_block_id, compound_id, created_at, updated_at)
                    VALUES (%s, %s, %s, %s, %s, NOW(), NOW())
                    """
                    cursor.execute(insert_query, (
                        unit_id,
                        unit['unit_name'],
                        unit.get('notes', None),
                        unit_block_id,
                        compound['id']
                    ))

    category_name = 'Maintenance'
    category_description = 'description'

    check_query = "SELECT id FROM categories WHERE name = %s"
    cursor.execute(check_query, (category_name,))
    existing_category = cursor.fetchone()

    if existing_category:
        category_id = existing_category['id']
    else:
        category_id = str(uuid.uuid4())
        insert_query = """INSERT INTO categories (id, name, description, updated_at, created_at) 
                        VALUES (%s, %s, %s, NOW(), NOW())"""
        cursor.execute(insert_query, (category_id, category_name, category_description))
        print(f"New category '{category_name}' created with ID: {category_id}")

    # Insert the services
    with open('services.json', 'r') as f:
        data = f.read()
        json_data = json.loads(data)  # Corrected json.dump to json.loads

        for parent in json_data:
            parent_id = str(uuid.uuid4())
            name = parent['name']
            cost = 0  # Assuming cost is always 0 (can be adjusted)
            description = parent['name']
            insert_query = """
            INSERT INTO services (id, name, cost, description, compound_id, category_id, created_at, updated_at)
            VALUES (%s, %s, %s, %s, %s, %s, NOW(), NOW())
            """
            cursor.execute(insert_query, (
                parent_id,
                name,
                cost,
                description,
                compound['id'],
                category_id
            ))
            children = parent['children']
            for child in children:
                child_id = str(uuid.uuid4())  # Added to match variable used
                insert_query = """
                INSERT INTO services (id, name, cost, description, compound_id, category_id, created_at, updated_at, parent_id)
                VALUES (%s, %s, %s, %s, %s, %s, NOW(), NOW(), %s)
                """
                cursor.execute(insert_query, (
                    child_id,
                    child,
                    cost,
                    child,
                    compound['id'],
                    category_id,
                    parent_id
                ))
    try:
        connection.commit()  
        print("Data saved successfully.")
    except mysql.connector.Error as err:
        print(f"Commit error: {err}")

except mysql.connector.Error as err:
    print(f"Error: {err}")
finally:
    if 'connection' in locals() and connection.is_connected():
        cursor.close()
        connection.close()
        print("MySQL connection closed.")