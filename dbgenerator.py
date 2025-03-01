import argparse
import random
import string
import logging
import pandas as pd

# Logging configuration
logging.basicConfig(filename='db_generation.log', level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

# MySQL data type definitions
db_types = {
    "date": {"has_length": False},
    "datetime": {"has_length": False},
    "timestamp": {"has_length": False},
    "varchar": {"has_length": True},
    "text": {"has_length": False},
    "int": {"has_length": True},
    "tinyint": {"has_length": True},
    "boolean": {"has_length": False},
    "float": {"has_length": True},
    "double": {"has_length": True},
    "char": {"has_length": True},
    "blob": {"has_length": False}
}

def remove_bom(file_path):
    with open(file_path, "rb") as f:
        content = f.read()
    if content.startswith(b'\xef\xbb\xbf'):
        with open(file_path, "wb") as f:
            f.write(content[3:])

def generate_random_name(length=8):
    return random.choice(string.ascii_lowercase) + ''.join(random.choices(string.ascii_lowercase + string.digits, k=length-1))

def process_csv(file_path):
    try:
        remove_bom(file_path)
        with open(file_path, "r", encoding="utf-8") as file:
            first_line = file.readline()
            delimiter = ";" if ";" in first_line else ","
        
        df = pd.read_csv(file_path, delimiter=delimiter, dtype=str).fillna("")
        return df.to_dict(orient='records')
    except Exception as e:
        logging.error(f"Error processing CSV file: {e}")
        exit(1)

def main():
    parser = argparse.ArgumentParser(description="Random Database Structure Generator")
    parser.add_argument("--csv", required=True, help="Path to input CSV file")
    parser.add_argument("--not-random", action="store_true", help="Do not generate random names for database objects")
    args = parser.parse_args()

    csv_data = process_csv(args.csv)
    if not csv_data:
        logging.error("The CSV file contains no valid data.")
        print("Error: The CSV file contains no valid data.")
        exit(1)
    
    name_mapping = {}
    sql_statements = []
    variable_definitions = []
    current_table = None
    table_columns = []
    primary_keys = []
    unique_columns = []
    
    for column in csv_data:
        column_type = column.get('type', '').strip().lower()
        if column_type == "database":
            column_type = "db"
        
        name = column.get('name', '').strip()
        depends = column.get('depends', '').strip()
        
        if not name:
            continue

        random_name = name if args.not_random else generate_random_name()
        
        if column_type == "db":
            name_mapping[name] = random_name
            sql_statements.append(f"CREATE DATABASE IF NOT EXISTS `{random_name}` DEFAULT CHARACTER SET utf8 COLLATE utf8_bin;")
            sql_statements.append(f"USE `{random_name}`;")
            variable_definitions.append(f"DB_{name.upper()}={random_name}")
            logging.info(f"Database created: {random_name}")
        
        elif column_type == "table":
            if current_table and table_columns:
                if primary_keys:
                    table_columns.append(f"  PRIMARY KEY ({', '.join(primary_keys)})")
                if unique_columns:
                    table_columns.append(f"  UNIQUE INDEX ({', '.join(unique_columns)})")
                sql_statements.append(",\n".join(table_columns) + "\n) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE utf8_bin;")
                logging.info(f"Table completed: {current_table}")
                table_columns = []
                primary_keys = []
                unique_columns = []
            
            if depends in name_mapping:
                db_name = name_mapping[depends]
                name_mapping[name] = random_name
                current_table = random_name
                table_columns = []
                sql_statements.append(f"CREATE TABLE IF NOT EXISTS `{db_name}`.`{random_name}` (")
                variable_definitions.append(f"TB_{name.upper()}={random_name}")
                logging.info(f"Table created: {random_name} in {db_name}")
        
        elif column_type == "column":
            if current_table:
                column_type = column.get('valtype', 'varchar').strip().lower()
                column_type = column_type if column_type in db_types else "varchar"
                length = f"({column.get('length', '').strip()})" if db_types[column_type]["has_length"] and column.get('length', '').strip() else ""
                not_null = " NOT NULL" if column.get('nn', '').strip().lower() in ["1", "true", "x"] else " NULL"
                auto_increment = " AUTO_INCREMENT" if column.get('ai', '').strip().lower() in ["1", "true", "x"] else ""
                default = f" DEFAULT {column.get('default', '').strip()}" if column.get('default', '').strip() else ""
                comment = f" COMMENT '{column.get('comment', '').strip()}'" if column.get('comment', '').strip() else ""
                
                column_definition = f"  `{random_name}` {column_type.upper()}{length}{not_null}{auto_increment}{default}{comment}"
                table_columns.append(column_definition)
                if column.get('pk', '').strip().lower() in ["1", "true", "x"]:
                    primary_keys.append(random_name)
                if column.get('uq', '').strip().lower() in ["1", "true", "x"]:
                    unique_columns.append(random_name)
    
    if current_table and table_columns:
        if primary_keys:
            table_columns.append(f"  PRIMARY KEY ({', '.join(primary_keys)})")
        if unique_columns:
            table_columns.append(f"  UNIQUE INDEX ({', '.join(unique_columns)})")
        sql_statements.append(",\n".join(table_columns) + "\n) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE utf8_bin;")
    
    if sql_statements:
        with open("database_structure.sql", "w", encoding="utf-8") as sql_file:
            sql_file.write("\n".join(sql_statements))
            print("File 'database_structure.sql' successfully created.")
    
    if variable_definitions:
        with open("variable_mapping.txt", "w", encoding="utf-8") as var_file:
            var_file.write("\n".join(variable_definitions))
            print("File 'variable_mapping.txt' successfully created.")
    
    logging.info("Process completed.")

if __name__ == "__main__":
    main()

