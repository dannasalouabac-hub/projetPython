import os
from pathlib import Path
import webbrowser

import matplotlib.pyplot as plt
import psycopg2

ACTOR_DASHBOARD_PATH = (
    Path(__file__).resolve().parents[1] / "country_actor_dashboard.svg"
)


def fetch_country_actor_counts() -> list[tuple[str, int, int]]:
    connection = psycopg2.connect(os.environ["DATABASE_URL"])
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    BTRIM(country) AS country,
                    COUNT(*) FILTER (
                        WHERE LOWER(BTRIM(actor)) = 'human'
                    ) AS humans,
                    COUNT(*) FILTER (
                        WHERE LOWER(BTRIM(actor)) = 'bot'
                    ) AS bots
                FROM auth_events
                WHERE event_type IN ('Failed', 'Invalid')
                    AND actor IS NOT NULL
                    AND LOWER(BTRIM(actor)) IN ('human', 'bot')
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
    country_counts = fetch_country_actor_counts()
    figure, axis = plt.subplots(
        figsize=(12, max(5, 0.42 * len(country_counts))),
        dpi=120,
    )

    if not country_counts:
        axis.text(
            0.5,
            0.5,
            "No human or bot events with a known country.",
            ha="center",
            va="center",
            transform=axis.transAxes,
        )
        axis.set_axis_off()
    else:
        countries = [row[0] for row in country_counts]
        humans = [row[1] for row in country_counts]
        bots = [row[2] for row in country_counts]
        positions = list(range(len(countries)))
        bar_height = 0.36

        human_bars = axis.barh(
            [position - bar_height / 2 for position in positions],
            humans,
            height=bar_height,
            label="Human",
            color="#4c8cbd",
        )
        bot_bars = axis.barh(
            [position + bar_height / 2 for position in positions],
            bots,
            height=bar_height,
            label="Bot",
            color="#e08b3e",
        )
        axis.bar_label(
            human_bars,
            labels=[str(count) if count else "" for count in humans],
            padding=4,
            fontsize=8,
        )
        axis.bar_label(
            bot_bars,
            labels=[str(count) if count else "" for count in bots],
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

    axis.set_title("Human and bot authentication events by country")
    axis.tick_params(axis="y", labelsize=9)
    figure.tight_layout()
    figure.savefig(ACTOR_DASHBOARD_PATH, format="svg", bbox_inches="tight")
    plt.close(figure)
    if webbrowser.open(ACTOR_DASHBOARD_PATH.as_uri()):
        print(f"Human/bot dashboard opened: {ACTOR_DASHBOARD_PATH}")
    else:
        print(
            "Human/bot dashboard saved; open this file in a browser: "
            f"{ACTOR_DASHBOARD_PATH}"
        )


if __name__ == "__main__":
    show_dashboard()
