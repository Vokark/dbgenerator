# dbgenerator

## Description:

Python program to generate databases from CSV files for people like me who completely forgives the commands all the time!!.
This program can generate random database, table, and column names. To avoid that, use the --not-random modifier in the command line. CSV can be an Excel file or any other CSV file, accepts ; and , as delimiters, and don't change the header because it reads table names.

The first line of CSV file can be "type;depends;name;valtype;length;nn;ai;pk;uq;default;comment" or "type,depends,name,valtype,length,nn,ai,pk,uq,default,comment" if you use ";" in first line, all document **MUST** use ";" as separator, if you use "," all document **MUST** use ",".

## CSV:

CSV file db.csv was created in Excel, so it has BOM bytes at the beginning of the file. If you see it with less, you can see type field has an odd "space" before; this Python program removes those bytes, so don't worry, you can delete them or use commas as well. All that is supported.

type: Field type; it can be "db", "database", "table" or "column".
depends: You need to declare here from what value this depends on, e.g., the database name is testdb, tables depend on testdb, and columns depend on tables, so you need to put the table name. 
name: Field name
valtype: column value type, it can be any declared in db_types dictionary.
length: Field maximum length db_types dictionary declares which column types have length
nn: Not null.
ai: Automatic increment value.
pk: Primary Key.
uq: unique field value.
default: default value when new row is created.

You can see it in the example db.csv file in this repo.

## Use:

```bash
git clone https://github.com/Vokark/dbgenerator
cd dbgenerator
python3 dbgenerator --csv /path/to/database.csv --not-random

sudo mysql -uroot < database_structure.sql
```

If you need a type that is not defined in python program, you can add at db_types dicctionary and put if it has length True or False, that means that value can have length value like varchar ex VARCHAR(20) but put type and lenght in corresponding column in CSV file:

```python
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
```

Username and password are randomly generated. You can see it in database_structure.sql file or in variable_mapping.txt file.

db_generation.log is added for debug purposes.

## Output files:

This program generates 3 files:

1. db_generation.log: Log file, if you have any issue, you can see the problem here (or some of them :D).
1. database_structure.sql: Database file that can be imported into mysql/mariadb server.
1. variable_mappint.txt: if you randomize values, the new names will be here. Or if you use "--not-random" in command line, you can see new database user and password here.

Note that database_structure.sql will only create database, table or user names if they do not exist before.

Enjoy!
