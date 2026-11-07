import os

import pymysql
from flask import Flask, make_response, render_template
from werkzeug.middleware.proxy_fix import ProxyFix

app = Flask(__name__)

# Nginx kertoo alkuperäisen yhteyden tiedot ja sovelluksen alipolun (/viikko2).
app.wsgi_app = ProxyFix(
    app.wsgi_app,
    x_for=1,
    x_proto=1,
    x_prefix=1,
)


def kasvata_laskuria():
    yhteys = pymysql.connect(
        unix_socket="/run/mysqld/mysqld.sock",
        user="viikko2app",
        password=os.environ["DB_PASSWORD"],
        database="viikko2",
        charset="utf8mb4",
        autocommit=False,
    )
    try:
        with yhteys.cursor() as kursori:
            kursori.execute(
                "UPDATE laskuri SET kaynnit = kaynnit + 1 WHERE id = 1"
            )
            kursori.execute(
                "SELECT kaynnit FROM laskuri WHERE id = 1"
            )
            kaynnit = kursori.fetchone()[0]
        yhteys.commit()
        return kaynnit
    except Exception:
        yhteys.rollback()
        raise
    finally:
        yhteys.close()


@app.route("/")
def etusivu():
    kaynnit = kasvata_laskuria()
    vastaus = make_response(render_template("index.html", kaynnit=kaynnit))
    # Selain ei saa näyttää vanhaa laskurin arvoa välimuistista
    vastaus.headers["Cache-Control"] = "no-store"
    return vastaus

