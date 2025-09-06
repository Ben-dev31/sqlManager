import sqlite3

class SQLModel:
    """
    Field representation example:
        fields = [
            ('id', 'INTEGER PRIMARY KEY'),
            ('nom', 'TEXT', 'UNIQUE'),
            ('prenom', 'TEXT', 'UNIQUE'),
            ('age', 'INTEGER', 'NOT NULL')
        ]
    """

    def __init__(self, fields=None, base_name='sql.db', name='tables'):
        if fields is None:
            fields = []
        self.fields = fields
        self.base_name = base_name
        self.name = name

    def __executereq(self, req, param=()):
        """
        Internal method to execute a SQL request.
        """
        self.connexion = sqlite3.connect(self.base_name)
        self.cursor = self.connexion.cursor()
        try:
            self.cursor.execute(req, param)
            if ('SELECT' in req.upper()) or ('PRAGMA' in req.upper()):
                res = self.cursor.fetchall()
                return res
        except Exception as e:
            self.connexion.rollback()
        finally:
            self.connexion.commit()
            self.connexion.close()

    def executerSQL(self, req, param):
        """
        Public method to execute a SQL request.
        """
        return self.__executereq(req, param)

    def create(self) -> None:
        """
        Create the table with the specified fields.
        """
        if self.fields[0][0] != 'id' and self.fields[0][1] != 'INTEGER PRIMARY KEY':
            self.fields.insert(0, ('id', 'INTEGER PRIMARY KEY'))

        req = f"CREATE TABLE IF NOT EXISTS '{self.name}'("
        for champ in self.fields:
            for col in champ:
                if col == champ[0]:
                    req += f"'{col}' "
                else:
                    req += col + ' '
            req += ", "
        req = req[:-2] + ")"
        self.__executereq(req=req)

    def add(self, data=None, **kwargs) -> None:
        """
        Add a single record to the table.
        """
        if data is not None and isinstance(data, dict):
            kwargs = data

        req = f"INSERT INTO '{self.name}' ("
        param = []
        for key in kwargs:
            req += f"'{key}', "
            param.append(kwargs[key])
        req = req[:-2] + ') VALUES ('
        req += ', '.join(['?'] * len(param)) + ')'
        self.__executereq(req, tuple(param))

    def add_many(self, data=None):
        """
        Add multiple records to the table.
        Args:
            data: list[list] | list of records without column names
        """
        req = f"INSERT INTO '{self.name}' ("
        for tp in self.fields:
            if tp[0] != 'id':
                req += f"'{tp[0]}', "
        req = req[:-2] + ') VALUES ('
        req += ', '.join(['?'] * len(data[0])) + ')'

        try:
            self.connexion = sqlite3.connect(self.base_name)
            self.cursor = self.connexion.cursor()
            self.cursor.executemany(req, data)
        except Exception as e:
            self.connexion.rollback()
        finally:
            self.connexion.commit()
            self.connexion.close()

    def add_fields(self, fields=None) -> None:
        """
        Add one or more fields to the table.
        Args:
            fields: list of tuples (field_name, field_type, ...)
        """
        if fields is not None:
            for field in fields:
                req = f"ALTER TABLE '{self.name}' ADD "
                req += f"'{field[0]}' {field[1]}"
                self.__executereq(req)

    def remove_fields(self, fields=None) -> None:
        """
        Remove one or more fields from the table.
        Args:
            fields: list of tuples (field_name,)
        """
        if fields is not None:
            for field in fields:
                req = f"ALTER TABLE '{self.name}' DROP COLUMN "
                req += f"'{field[0]}'"
                self.__executereq(req)

    def rename_field(self, field_name, new_name):
        """
        Rename a field in the table.
        """
        req = f"ALTER TABLE '{self.name}' RENAME column '{field_name}' TO '{new_name}'"
        self.__executereq(req)

    def rename_table(self, table, new_name) -> None:
        """
        Rename a table.
        Args:
            table: str | current table name
            new_name: str | new table name
        """
        req = f"ALTER TABLE '{table}' RENAME TO '{new_name}'"
        self.__executereq(req)

    def get_tables_meta(self, table=None) -> list:
        """
        Get the list of columns for a table.
        Args:
            table: str | table name
        Returns:
            list of column names
        """
        if table is None:
            table = self.name
        req = f"PRAGMA table_info('{table}')"
        meta = self.__executereq(req)
        ls = []
        if meta:
            for champ in meta:
                ls.append(champ[1])
        return ls

    def get_tables(self) -> list[tuple]:
        """
        Get the list of all tables in the database.
        """
        req = "SELECT name FROM sqlite_master WHERE TYPE='table'"
        return self.__executereq(req)

    def all(self, reverse=False, order_col='id') -> list:
        """
        Get all records from the table.
        Args:
            reverse: bool | order descending if True
            order_col: str | column to order by
        Returns:
            list of DataObject
        """
        req = f"SELECT * FROM '{self.name}' "
        req += f"ORDER BY {order_col} {'DESC' if reverse else ''}".strip()
        values = self.__executereq(req)
        data = []
        for tp in values:
            data.append(
                DataObject(
                    fields=self.fields,
                    datas=tp,
                    base_name=self.base_name,
                    table_name=self.name
                )
            )
        return data

    def get(self, reverse=False, order_col='id', data=None, **kwargs) -> list:
        """
        Get records matching specific criteria.
        Args:
            data: dict | filter criteria
        Returns:
            list of DataObject
        """
        if data is not None and isinstance(data, dict):
            kwargs = data

        req = f"SELECT * FROM '{self.name}' WHERE "
        param = []
        for key in kwargs:
            for tp in self.fields:
                if tp[0] == key:
                    req += f"{key} = ? AND "
                    param.append(kwargs[key])
        req = req[:-4]
        req += f" ORDER BY {order_col} {'DESC' if reverse else ''}".strip()
        values = self.__executereq(req, tuple(param))
        data = []
        for tp in values:
            data.append(
                DataObject(
                    fields=self.fields,
                    datas=tp,
                    base_name=self.base_name,
                    table_name=self.name
                )
            )
        return data

    def get_by_column(self, cols: str):
        """
        Get specific columns from the table.
        Args:
            cols: str | column names separated by commas
        Returns:
            list of DataObject
        """
        req = f"SELECT {cols} FROM '{self.name}'"
        values = self.__executereq(req)
        data = []
        for tp in values:
            data.append(
                DataObject(
                    fields=self.fields,
                    datas=tp,
                    base_name=self.base_name,
                    table_name=self.name
                )
            )
        return data

    def update(self, col, value, setcond) -> None:
        """
        Update a column value for records matching a condition.
        Args:
            col: str | column to update
            value: str | new value
            setcond: str | condition (e.g., "age <= 30")
        """
        req = f'UPDATE "{self.name}" SET "{col}" = "{value}" '
        if setcond is not None:
            req += f' WHERE {setcond}'
        self.__executereq(req)

    def delete_all(self) -> None:
        """
        Delete all records from the table.
        """
        req = f"DELETE FROM '{self.name}'"
        self.__executereq(req)

    def delete_table(self, table_name) -> None:
        """
        Delete a table from the database.
        Args:
            table_name: str
        """
        req = f"DROP TABLE '{table_name}'"
        self.__executereq(req)

    def remove(self, data=None, **kwargs) -> None:
        """
        Delete records matching specific criteria.
        Args:
            data: dict | filter criteria
        """
        if data is not None and isinstance(data, dict):
            kwargs = data
        req = f"DELETE FROM '{self.name}' WHERE "
        param = []
        for key in kwargs:
            req += f"{key}=? AND "
            param.append(kwargs[key])
        req = req[:-4]
        self.__executereq(req, param=tuple(param))


class DataObject:
    """
    Wrapper for a single record from the database.
    """
    def __init__(self, fields, datas, base_name, table_name) -> None:
        self.fields = fields
        self.base_name = base_name
        self.name = table_name
        self.datas = datas
        self.data_dic = {}
        self.__update_content_values()
        self.base = SQLModel(fields=self.fields, base_name=self.base_name, name=self.name)

    def __update_content_values(self):
        """
        Update the object's attributes from the data tuple.
        """
        for i, field in enumerate(self.fields):
            try:
                self.data_dic[field[0]] = self.datas[i]
            except IndexError:
                self.data_dic[field[0]] = None
        self.__dict__.update(self.data_dic)

    def __str__(self) -> str:
        self.__unp()
        return f"{self.data_dic}"

    def __unp(self):
        """
        Update the data_dic from the object's attributes.
        """
        for key in self.data_dic.keys():
            self.data_dic[key] = self.__dict__[key]

    def save(self) -> None:
        """
        Save changes to the database.
        """
        if self.isExist():
            for key in self.__dict__.keys():
                if key != 'id' and key in self.data_dic.keys():
                    self.base.update(col=key, value=self.__dict__[key], setcond=f'id={self.__dict__["id"]}')
        else:
            self.base.add(data=self.data_dic)

    def remove(self):
        """
        Remove this record from the database.
        """
        self.base.remove(id=self.__dict__["id"])

    def newTableToConnect(self, name):
        """
        Connect this object to a different table.
        """
        self.base = SQLModel(base_name=self.base_name, name=name)
        self.fields = [(fd,) for fd in self.base.get_tables_meta(name)]
        self.base.fields = self.fields
        self.__update_content_values()

    def isExist(self) -> bool:
        """
        Check if this record exists in the database.
        """
        values = self.base.get(id=self.__dict__["id"])
        return bool(values)

if __name__ == '__main__':
    fields = [
        ('id', 'INTEGER PRIMARY KEY'),
        ('nom', 'TEXT', 'UNIQUE'),
        ('prenom', 'TEXT', 'UNIQUE'),
        ('age', 'INTEGER', 'NOT NULL')
    ]
    model = SQLModel(fields=fields, name='aa_tb', base_name='test.sqlite3')
    # model.create()
    data = model.all()[0]
    data.nom = "BALA"
    data.save()