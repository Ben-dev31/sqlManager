# sqlManager

**sqlManager** is a simple Python module to manage SQLite databases and tables with ease.  
It provides a high-level API for creating tables, adding, updating, deleting, and querying records, as well as managing table schemas.

## Features

- Create and manage SQLite tables dynamically
- Add, update, delete, and query records easily
- Add, remove, and rename table columns
- Rename tables
- Retrieve table metadata
- Object-oriented interface for database rows

---

## Installation

Copy the `sqlManager` directory into your project, or install via pip if published.

```bash
pip install git+https://github.com/Ben-dev31/sqlManager.git
```
To upgrade

```bash
pip install --upgrade git+https://github.com/Ben-dev31/sqlManager.git

```
**Requirements:**  
- Python 3.8+
- Standard library only (`sqlite3`)

---

## Quick Start

```python
from sqlManager.model import SQLModel

fields = [
    ('id', 'INTEGER PRIMARY KEY'),
    ('name', 'TEXT', 'UNIQUE'),
    ('firstName', 'TEXT', 'UNIQUE'),
    ('age', 'INTEGER', 'NOT NULL')
]

model = SQLModel(fields=fields, name='person', base_name='mydb.sqlite3')
model.create()  # Create the table if it doesn't exist

# Add a record
model.add(name="Doe", firstName="John", age=30)

# Get all records
for person in model.all():
    print(person.nane, person.firstName, person.age)

# Update a record
person = model.get(nom="Doe")[0]
person.age = 31
person.save()

# Delete a record
person.remove()
```

---

## API Reference

### SQLModel

#### Initialization

```python
SQLModel(fields=None, base_name='sql.db', name='tables')
```

- **fields**: List of tuples describing columns.  
  Example: `[('id', 'INTEGER PRIMARY KEY'), ('name', 'TEXT', 'UNIQUE')]`
- **base_name**: SQLite file name.
- **name**: Table name.

#### Methods

- **create()**  
  Create the table with the specified fields.

- **add(data=None, \*\*kwargs)**  
  Add a single record. Accepts a dict or keyword arguments.

- **add_many(data)**  
  Add multiple records.  
  `data`: list of lists (each sublist is a row, without column names).

- **add_fields(fields)**  
  Add one or more columns to the table.  
  `fields`: list of tuples (column_name, column_type, ...)

- **remove_fields(fields)**  
  Remove one or more columns from the table.  
  `fields`: list of tuples (column_name,)

- **rename_field(field_name, new_name)**  
  Rename a column.

- **rename_table(table, new_name)**  
  Rename a table.

- **get_tables_meta(table=None)**  
  Get the list of columns for a table.

- **get_tables()**  
  Get the list of all tables in the database.

- **all(reverse=False, order_col='id')**  
  Get all records as `DataObject` instances.

- **get(reverse=False, order_col='id', data=None, \*\*kwargs)**  
  Get records matching criteria as `DataObject` instances.

- **get_by_column(cols)**  
  Get specific columns.

- **update(col, value, setcond)**  
  Update a column value for records matching a condition.

- **delete_all()**  
  Delete all records from the table.

- **delete_table(table_name)**  
  Delete a table from the database.

- **remove(data=None, \*\*kwargs)**  
  Delete records matching criteria.

---

### DataObject

Represents a single row from the database.  
Attributes correspond to column names.

#### Methods

- **save()**  
  Save changes to the database (update or insert).

- **remove()**  
  Delete this record from the database.

- **newTableToConnect(name)**  
  Connect this object to a different table.

- **isExist()**  
  Check if this record