import argshell
from griddle import griddy
from pathier import Pathier, Pathish

from databased import Databased, __version__, dbparsers
from databased.create_shell import create_shell


class DBShell(argshell.ArgShell):
    _dbpath: Pathier = None  # type: ignore
    connection_timeout: float = 10
    detect_types: bool = True
    enforce_foreign_keys: bool = True
    intro = f"Starting dbshell v{__version__} (enter help or ? for arg info)...\n"
    prompt = f"based>"

    @property
    def dbpath(self) -> Pathier:
        return self._dbpath

    @dbpath.setter
    def dbpath(self, path: Pathish):
        self._dbpath = Pathier(path)
        self.prompt = f"{self._dbpath.name}>"

    def _DB(self) -> Databased:
        return Databased(
            self.dbpath,
            self.connection_timeout,
            self.detect_types,
            self.enforce_foreign_keys,
        )

    def default(self, line: str):
        line = line.strip("_")
        with self._DB() as db:
            self.display(db.query(line))

    def display(self, data: list[dict]):
        """Print row data to terminal in a grid."""
        try:
            print(griddy(data, "keys"))
        except Exception as e:
            print("Could not fit data into grid :(")
            print(e)

    # Seat

    @argshell.with_parser(dbparsers.get_add_column_parser)
    def do_add_column(self, args: argshell.Namespace):
        """Add a new column to the specified tables."""
        with self._DB() as db:
            db.add_column(args.table, args.column_def)

    @argshell.with_parser(dbparsers.get_backup_parser)
    def do_backup(self, args: argshell.Namespace):
        """Create a backup of the current db file."""
        print(f"Creating a back up for {self.dbpath}...")
        backup_path = self.dbpath.backup(args.timestamp)
        print("Creating backup is complete.")
        print(f"Backup path: {backup_path}")

    def do_customize(self, name: str):
        """Generate a template file in the current working directory for creating a custom DBShell class.
        Expects one argument: the name of the custom dbshell.
        This will be used to name the generated file as well as several components in the file content.
        """
        try:
            create_shell(name)
        except Exception as e:
            print(f"{type(e).__name__}: {e}")

    def do_dbpath(self, _: str):
        """Print the .db file in use."""
        print(self.dbpath)

    @argshell.with_parser(dbparsers.get_delete_parser)
    def do_delete(self, args: argshell.Namespace):
        """Delete rows from the database.

        Syntax:
        >>> delete {table} {where}
        >>> based>delete users "username LIKE '%chungus%"

        ^will delete all rows in the 'users' table whose username contains 'chungus'^"""
        print("Deleting records...")
        with self._DB() as db:
            num_rows = db.delete(args.table, args.where)
            print(f"Deleted {num_rows} rows from {args.table} table.")

    def do_describe(self, tables: str):
        """Describe each table in `tables`. If no table list is given, all tables will be described."""
        with self._DB() as db:
            table_list = tables.split() or db.tables
            for table in table_list:
                print(f"<{table}>")
                print(db.to_grid(db.describe(table)))

    @argshell.with_parser(dbparsers.get_drop_column_parser)
    def do_drop_column(self, args: argshell.Namespace):
        """Drop the specified column from the specified table."""
        with self._DB() as db:
            db.drop_column(args.table, args.column)

    def do_drop_table(self, table: str):
        """Drop the specified table."""
        with self._DB() as db:
            db.drop_table(table)

    def do_flush_log(self, _: str):
        """Clear the log file for this database."""
        log_path = self.dbpath.with_name(self.dbpath.name.replace(".", "") + ".log")
        if not log_path.exists():
            print(f"No log file at path {log_path}")
        else:
            print(f"Flushing log...")
            log_path.write_text("")

    def do_help(self, args: str):
        """Display help messages."""
        super().do_help(args)
        if args == "":
            print("Unrecognized commands will be executed as queries.")
            print(
                "Use the `query` command explicitly if you don't want to capitalize your key words."
            )
            print("All transactions initiated by commands are committed immediately.")
        print()

    def do_properties(self, _: str):
        """See current database property settings."""
        for property_ in ["connection_timeout", "detect_types", "enforce_foreign_keys"]:
            print(f"{property_}: {getattr(self, property_)}")

    def do_query(self, query: str):
        """Execute a query against the current database."""
        print(f"Executing {query}")
        with self._DB() as db:
            results = db.query(query)
        self.display(results)
        print(f"{db.cursor.rowcount} affected rows")

    @argshell.with_parser(dbparsers.get_rename_column_parser)
    def do_rename_column(self, args: argshell.Namespace):
        """Rename a column."""
        with self._DB() as db:
            db.rename_column(args.table, args.column, args.new_name)

    @argshell.with_parser(dbparsers.get_rename_table_parser)
    def do_rename_table(self, args: argshell.Namespace):
        """Rename a table."""
        with self._DB() as db:
            db.rename_table(args.table, args.new_name)

    def do_restore(self, file: str):
        """Replace the current db file with the given db backup file."""
        backup = Pathier(file.strip('"'))
        if not backup.exists():
            print(f"{backup} does not exist.")
        else:
            print(f"Restoring from {file}...")
            self.dbpath.write_bytes(backup.read_bytes())
            print("Restore complete.")

    @argshell.with_parser(dbparsers.get_scan_dbs_parser)
    def do_scan(self, args: argshell.Namespace):
        """Scan the current working directory for database files."""
        dbs = self._scan(args.extensions, args.recursive)
        for db in dbs:
            print(db.separate(Pathier.cwd().stem))

    @argshell.with_parser(dbparsers.get_schema_parser)
    def do_schema(self, args: argshell.Namespace):
        """Print out the names of the database tables, their columns, and, optionally, the number of rows."""
        print("Getting database schema...")
        with self._DB() as db:
            tables = args.tables or db.tables
            info = [
                {
                    "Table Name": table,
                    "Columns": ", ".join(db.get_columns(table)),
                    "Number of Rows": db.count(table) if args.rowcount else "n/a",
                }
                for table in tables
            ]
        self.display(info)

    @argshell.with_parser(dbparsers.get_select_parser, [dbparsers.select_post_parser])
    def do_select(self, args: argshell.Namespace):
        """Execute a SELECT query with the given args."""
        print(f"Querying {args.table}... ")
        with self._DB() as db:
            rows = db.select(
                table=args.table,
                columns=args.columns,
                joins=args.joins,
                where=args.where,
                group_by=args.group_by,
                having=args.Having,
                order_by=args.order_by,
                limit=args.limit,
            )
            print(f"Found {len(rows)} rows:")
            self.display(rows)
            print(f"{len(rows)} rows from {args.table}")

    def do_set_connection_timeout(self, seconds: str):
        """Set database connection timeout to this number of seconds."""
        self.connection_timeout = float(seconds)

    def do_set_detect_types(self, should_detect: str):
        """Pass a `1` to turn on and a `0` to turn off."""
        self.detect_types = bool(int(should_detect))

    def do_set_enforce_foreign_keys(self, should_enforce: str):
        """Pass a `1` to turn on and a `0` to turn off."""
        self.enforce_foreign_keys = bool(int(should_enforce))

    def do_size(self, _: str):
        """Display the size of the the current db file."""
        print(f"{self.dbpath.name} is {self.dbpath.formatted_size}.")

    @argshell.with_parser(dbparsers.get_update_parser)
    def do_update(self, args: argshell.Namespace):
        """Update a column to a new value.

        Syntax:
        >>> update {table} {column} {value} {where}
        >>> based>update users username big_chungus "username = lil_chungus"

        ^will update the username in the users 'table' to 'big_chungus' where the username is currently 'lil_chungus'^
        """
        print("Updating rows...")
        with self._DB() as db:
            num_updates = db.update(args.table, args.column, args.new_value, args.where)
            print(f"Updated {num_updates} rows in table {args.table}.")

    def do_use(self, arg: str):
        """Set which database file to use."""
        dbpath = Pathier(arg)
        if not dbpath.exists():
            print(f"{dbpath} does not exist.")
            print(f"Still using {self.dbpath}")
        elif not dbpath.is_file():
            print(f"{dbpath} is not a file.")
            print(f"Still using {self.dbpath}")
        else:
            self.dbpath = dbpath
            self.prompt = f"{self.dbpath.name}>"

    def do_vacuum(self, _: str):
        """Reduce database disk memory."""
        print(f"Database size before vacuuming: {self.dbpath.formatted_size}")
        print("Vacuuming database...")
        with self._DB() as db:
            freedspace = db.vacuum()
        print(f"Database size after vacuuming: {self.dbpath.formatted_size}")
        print(f"Freed up {Pathier.format_bytes(freedspace)} of disk space.")

    # Seat

    def _choose_db(self, options: list[Pathier]) -> Pathier:
        """Prompt the user to select from a list of files."""
        cwd = Pathier.cwd()
        paths = [path.separate(cwd.stem) for path in options]
        while True:
            print(
                f"DB options:\n{' '.join([f'({i}) {path}' for i, path in enumerate(paths, 1)])}"
            )
            choice = input("Enter the number of the option to use: ")
            try:
                index = int(choice)
                if not 1 <= index <= len(options):
                    print("Choice out of range.")
                    continue
                return options[index - 1]
            except Exception as e:
                print(f"{choice} is not a valid option.")

    def _scan(
        self, extensions: list[str] = [".sqlite3", ".db"], recursive: bool = False
    ) -> list[Pathier]:
        cwd = Pathier.cwd()
        dbs = []
        globber = cwd.glob
        if recursive:
            globber = cwd.rglob
        for extension in extensions:
            dbs.extend(list(globber(f"*{extension}")))
        return dbs

    def preloop(self):
        """Scan the current directory for a .db file to use.
        If not found, prompt the user for one or to try again recursively."""
        if self.dbpath:
            self.dbpath = Pathier(self.dbpath)
            print(f"Defaulting to database {self.dbpath}")
        else:
            print("Searching for database...")
            cwd = Pathier.cwd()
            dbs = self._scan()
            if len(dbs) == 1:
                self.dbpath = dbs[0]
                print(f"Using database {self.dbpath}.")
            elif dbs:
                self.dbpath = self._choose_db(dbs)
            else:
                print(f"Could not find a .db file in {cwd}.")
                path = input(
                    "Enter path to .db file to use or press enter to search again recursively: "
                )
                if path:
                    self.dbpath = Pathier(path)
                elif not path:
                    print("Searching recursively...")
                    dbs = self._scan(recursive=True)
                    if len(dbs) == 1:
                        self.dbpath = dbs[0]
                        print(f"Using database {self.dbpath}.")
                    elif dbs:
                        self.dbpath = self._choose_db(dbs)
                    else:
                        print("Could not find a .db file.")
                        self.dbpath = Pathier(input("Enter path to a .db file: "))
        if not self.dbpath.exists():
            raise FileNotFoundError(f"{self.dbpath} does not exist.")
        if not self.dbpath.is_file():
            raise ValueError(f"{self.dbpath} is not a file.")


def main():
    DBShell().cmdloop()
