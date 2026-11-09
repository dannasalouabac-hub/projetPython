import os

import matplotlib.pyplot as plt
import psycopg2


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


def draw_dashboard(axis, country_counts: list[tuple[str, int, int]]) -> None:
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
            color="#ac34db",
        )
        bot_bars = axis.barh(
            [position + bar_height / 2 for position in positions],
            bots,
            height=bar_height,
            label="Bot",
            color="#8b5f35",
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

    axis.set_title("Human and bot events by country", pad=12)
    axis.tick_params(axis="y", labelsize=9)


def show_dashboard() -> None:
    country_counts = fetch_country_actor_counts()[:20]
    figure, axis = plt.subplots(
        figsize=(12, max(5, 0.42 * len(country_counts))),
        dpi=120,
    )
    draw_dashboard(axis, country_counts)
    figure.tight_layout()
    plt.show()


if __name__ == "__main__":
    show_dashboard()
