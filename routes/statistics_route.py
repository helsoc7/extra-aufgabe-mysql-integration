from database.database import get_db_connection
from flask import jsonify, request


def register_statistics_routes(app):
    # Statistik-Route, um Daten aus beiden Tabellen anzuzeigen
    @app.route("/api/stats", methods=["GET"])
    def get_statistics():
        """
        Statistiken über Tiere und Besitzer
        ---
        responses:
            200:
                description: Statistiken über Tiere und Besitzer
                examples:
                    application/json:
                        {
                            "animals_by_genus":
                            {
                                "birds": 1,
                                "mammals": 3
                            },
                            "total_animals": 4,
                            "total_owners": 3
                        }
        """
        con = get_db_connection()
        cur = con.cursor()
        animal_count = cur.execute('SELECT COUNT(*) FROM Animals').fetchone()[0]
        owner_count = cur.execute('SELECT COUNT(*) FROM Owners').fetchone()[0]
        # Nach Gattung filtern
        genus_stats = cur.execute(
            '''
            SELECT genus, COUNT(*) as count FROM Animals
            WHERE genus IS NOT NULL
            GROUP BY genus
            '''
        ).fetchall() # ("mammals", 3), ("birds", 2), ...

        # genus_stats_rows = []
        # for row in genus_stats:
        #     genus_stats_rows.append(row["genus"]: row[])

        con.close()
        stats = {
            "total_animals": animal_count,
            "total_owners": owner_count,
            "animals_by_genus": {row["genus"]: row["count"] for row in genus_stats}
        }

        return jsonify(stats), 200