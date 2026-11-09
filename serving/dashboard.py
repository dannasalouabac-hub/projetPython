import os

import matplotlib.pyplot as plt
import psycopg2


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


def draw_dashboard(axis, country_counts: list[tuple[str, int, int]]) -> None:
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
            color="#ccba16",
        )
        invalid_bars = axis.barh(
            [position + bar_height / 2 for position in positions],
            invalid_users,
            height=bar_height,
            label="Invalid user",
            color="#a1bbcf",
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

    axis.set_title("SSH authentication events by country", pad=12)
    axis.tick_params(axis="y", labelsize=9)


def show_dashboard() -> None:
    country_counts = fetch_country_counts()[:20]
    figure, axis = plt.subplots(
        figsize=(12, max(5, 0.42 * len(country_counts))),
        dpi=120,
    )
    draw_dashboard(axis, country_counts)
    figure.tight_layout()
    plt.show()


def show_all_dashboards() -> None:
    from serving import actor_dashboard, successful_user_dashboard

    country_counts = fetch_country_counts()[:20]
    actor_counts = actor_dashboard.fetch_country_actor_counts()[:20]
    user_counts = successful_user_dashboard.fetch_successful_connection_counts()
    country_chart_height = max(
        7,
        0.38 * max(len(country_counts), len(actor_counts)),
    )
    user_chart_height = max(4, 0.4 * len(user_counts))
    figure = plt.figure(
        figsize=(18, country_chart_height + user_chart_height + 1),
        dpi=120,
        constrained_layout=True,
    )
    grid = figure.add_gridspec(
        2,
        2,
        height_ratios=(country_chart_height, user_chart_height),
    )
    country_axis = figure.add_subplot(grid[0, 0])
    actor_axis = figure.add_subplot(grid[0, 1])
    user_axis = figure.add_subplot(grid[1, :])

    draw_dashboard(country_axis, country_counts)
    actor_dashboard.draw_dashboard(actor_axis, actor_counts)
    successful_user_dashboard.draw_dashboard(user_axis, user_counts)

    figure.suptitle("Authentication Dashboard", fontsize=16)
    plt.show()


if __name__ == "__main__":
    show_all_dashboards()
