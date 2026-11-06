# Log analysis

Run the report from this directory with:

```powershell
python main.py
```

The program saves each failed-password and invalid-user event to PostgreSQL.
Set `DATABASE_URL` before running it, for example:

```powershell
$env:DATABASE_URL = "postgresql://username:password@localhost:5432/log_analysis"
python main.py
```

The program creates the `auth_events` table if it does not exist. Stored
columns include event time, type, IP, bot/human label, city, country, and the
original log row.

The report counts matching failed-password and invalid-user log rows and
prints each matching original row with its IP address. `ingest()` reads every
regular file in the data directory, including gzip-compressed logs, and
combines their rows in filename order.