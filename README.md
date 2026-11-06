# Log analysis

Run the complete workflow from this directory with:

```powershell
python main.py
```

The program reads all log files, analyzes them, saves failed-password and
invalid-user events to PostgreSQL, then creates and opens both country
dashboards: event type by country, and human/bot counts by country.
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

The dashboard uses the same `DATABASE_URL` environment variable as the
analysis program.
Events whose country is blank, `Unknown`, or `not found` are excluded from
the chart. Bar labels show the count for each event type. The full-height
chart is saved as `country_dashboard.svg` in the project directory and opened
in the default browser, where all countries can be viewed by scrolling. The
human/bot dashboard is saved as `country_actor_dashboard.svg`.