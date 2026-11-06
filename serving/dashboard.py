import os
from pathlib import Path
import webbrowser

import matplotlib.pyplot as plt
import psycopg2

DASHBOARD_PATH = Path(__file__).resolve().parents[1] / "country_dashboard.svg"


def fetch_country_counts() -> list[tuple[str, int, int]]:
    connection = psycopg2.connect(os.environ["DATABASE_URL"])
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    BTRIM(country) AS country,
                    COUNT(*) FILTER (WHERE event_type = 'Failed') AS failed_passwords,
                    COUNT(*) FILTER (WHERE event_type = 'Invalid') AS invalid_users
                FROM auth_events
                WHERE event_type IN ('Failed', 'Invalid')
                    AND country IS NOT NULL
                    AND BTRIM(country) <> ''
                    AND LOWER(BTRIM(country)) NOT IN ('unknown', 'not found')
                GROUP BY BTRIM(country)
                ORDER BY country
                """
            )
            rows = cursor.fetchall()
    finally:
        connection.close()

    return sorted(rows, key=lambda row: row[1] + row[2], reverse=True)


def show_dashboard() -> None:
    country_counts = fetch_country_counts()
    figure, axis = plt.subplots(
        figsize=(12, max(5, 0.42 * len(country_counts))),
        dpi=120,
    )

    if not country_counts:
        axis.text(
            0.5,
            0.5,
            "No failed-password or invalid-user events with a known country.",
            ha="center",
            va="center",
            transform=axis.transAxes,
        )
        axis.set_axis_off()
    else:
        countries = [row[0] for row in country_counts]
        failed_passwords = [row[1] for row in country_counts]
        invalid_users = [row[2] for row in country_counts]
        positions = list(range(len(countries)))
        bar_height = 0.36

        failed_bars = axis.barh(
            [position - bar_height / 2 for position in positions],
            failed_passwords,
            height=bar_height,
            label="Failed password",
            color="#d95f59",
        )
        invalid_bars = axis.barh(
            [position + bar_height / 2 for position in positions],
            invalid_users,
            height=bar_height,
            label="Invalid user",
            color="#4c8cbd",
        )
        axis.bar_label(
            failed_bars,
            labels=[str(count) if count else "" for count in failed_passwords],
            padding=4,
            fontsize=8,
        )
        axis.bar_label(
            invalid_bars,
            labels=[str(count) if count else "" for count in invalid_users],
            padding=4,
            fontsize=8,
        )
        axis.set_yticks(positions, labels=countries)
        axis.invert_yaxis()
        axis.set_xlabel("Number of events")
        axis.set_ylabel("Country")
        axis.legend(loc="lower right")
        axis.grid(axis="x", linestyle=":", alpha=0.5)
        axis.set_axisbelow(True)
        axis.margins(x=0.12)

    axis.set_title(
        "SSH authentication events by country\n"
        "(events without a known country are excluded)"
    )
    axis.tick_params(axis="y", labelsize=9)
    figure.tight_layout()
    figure.savefig(DASHBOARD_PATH, format="svg", bbox_inches="tight")
    plt.close(figure)
    if webbrowser.open(DASHBOARD_PATH.as_uri()):
        print(f"Dashboard opened in your browser: {DASHBOARD_PATH}")
    else:
        print(f"Dashboard saved; open this file in a browser: {DASHBOARD_PATH}")


if __name__ == "__main__":
    show_dashboard()
