import os

import matplotlib.pyplot as plt
import psycopg2


def fetch_successful_connection_counts() -> list[tuple[str, int]]:
    connection = psycopg2.connect(os.environ["DATABASE_URL"])
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT BTRIM(username) AS username, COUNT(*) AS connections
                FROM auth_events
                WHERE event_type = 'Accepted'
                    AND username IS NOT NULL
                    AND BTRIM(username) <> ''
                GROUP BY BTRIM(username)
                ORDER BY connections DESC, username
                """
            )
            rows = cursor.fetchall()
    finally:
        connection.close()

    return rows


def show_dashboard() -> None:
    user_counts = fetch_successful_connection_counts()
    figure, axis = plt.subplots(
        figsize=(12, max(5, 0.45 * len(user_counts))),
        dpi=120,
    )

    if not user_counts:
        axis.text(
            0.5,
            0.5,
            "No successful connections with a recorded username.",
            ha="center",
            va="center",
            transform=axis.transAxes,
        )
        axis.set_axis_off()
    else:
        usernames = [row[0] for row in user_counts]
        connection_counts = [row[1] for row in user_counts]
        bars = axis.barh(
            usernames,
            connection_counts,
            color="#4c8cbd",
        )
        axis.bar_label(
            bars,
            labels=[str(count) for count in connection_counts],
            padding=4,
            fontsize=8,
        )
        axis.invert_yaxis()
        axis.set_xlabel("Successful connections")
        axis.set_ylabel("Username")
        axis.grid(axis="x", linestyle=":", alpha=0.5)
        axis.set_axisbelow(True)
        axis.margins(x=0.12)

    axis.set_title("connections by user")
    axis.tick_params(axis="y", labelsize=9)
    figure.tight_layout()
    plt.show()


if __name__ == "__main__":
    show_dashboard()
