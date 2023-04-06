from contextlib import closing
from flask import *
from itertools import groupby
from io import BytesIO
import matplotlib.pyplot as plt
from os.path import dirname, exists, join
import sqlite3

app = Flask(__name__)

DB_PATH = join(dirname(__file__), "ensembl_hs63_simple.sqlite")
if not exists(DB_PATH):
    print("Base de données manquante : ", DB_PATH)
    exit(-1)

def get_db():
    return closing(sqlite3.connect("ensembl_hs63_simple.sqlite"))


@app.route("/")
def root():
    return render_template('root.html')


@app.route("/domains/")
def domain_list():
    with get_db() as conn:
        c = conn.cursor()
        c.execute("""
            SELECT Interpro_ID, Interpro_Short_Description, count(Ensembl_Protein_ID)
            FROM Domains
            NATURAL JOIN Proteins2Domains
            GROUP BY Interpro_ID
            ORDER BY Interpro_Short_Description
        """);
        return render_template("domain_list.html", domains=c.fetchall())


@app.route("/domains/<did>")
def domain_view(did):
    ctype = request.accept_mimetypes.best_match(
        ['text/html', 'application/json'],
        'test/html',
    )
    if ctype == 'application/json':
        return domain_view_json(did)
    else:
        return domain_view_html(did)


@app.route("/domains/<did>.html")
def domain_view_html(did):
    with get_db() as conn:
        c = conn.cursor()
        c.execute("""
            SELECT Interpro_ID, Interpro_Short_Description, Interpro_Description
            FROM Domains
            WHERE Interpro_ID = ?
        """, [did]);
        domain = c.fetchone()

        c.execute("""
            SELECT p.Ensembl_Protein_ID, HGNC_Symbol,
                GROUP_CONCAT(d2.Interpro_ID, " ")
            FROM Proteins2Domains AS d1
            JOIN Proteins AS P ON d1.Ensembl_Protein_ID=p.Ensembl_Protein_ID
            LEFT JOIN Proteins2Domains AS d2 ON p.Ensembl_Protein_ID=d2.Ensembl_Protein_ID
            WHERE d1.Interpro_ID = ?
            GROUP BY p.Ensembl_Protein_ID
        """, [did]);
        proteins = c.fetchall()

        c.execute("""
            SELECT DISTINCT d2.Interpro_ID, d2.Interpro_Short_Description
            FROM Proteins2Domains AS d1p
            JOIN Proteins AS P ON d1p.Ensembl_Protein_ID=p.Ensembl_Protein_ID
            LEFT JOIN Proteins2Domains AS pd2 ON p.Ensembl_Protein_ID=pd2.Ensembl_Protein_ID
            LEFT JOIN Domains AS d2 ON pd2.Interpro_ID=d2.Interpro_ID
            WHERE d1p.Interpro_ID = ?
              AND pd2.Interpro_ID != ?
            ORDER BY d2.Interpro_Short_Description
        """, [did, did]);
        related = c.fetchall()
        
        return render_template("domain_view.html", domain=domain, proteins=proteins, related=related)


@app.route("/domains/<did>.json")
def domain_view_json(did):
    with get_db() as conn:
        c = conn.cursor()
        c.execute("""
            SELECT Interpro_ID, Interpro_Short_Description, Interpro_Description
            FROM Domains
            NATURAL JOIN Proteins2Domains
            WHERE Interpro_ID = ?
            GROUP BY Interpro_ID
        """, [did]);
        row = c.fetchone()
        if row is None:
            abort(404)
        data = dict(zip(['id', 'short_description', 'description'], row))

        c.execute("""
            SELECT Ensembl_Protein_ID
            FROM Proteins2Domains
            WHERE Interpro_ID = ?
        """, [did]);
        data['proteins'] = list(c.fetchall())

        return jsonify(data)


@app.route("/proteins/")
def protein_list():
    with get_db() as conn:
        limit = request.args.get("limit", 100, int)
        offset = request.args.get("offset", 0, int)
        c = conn.cursor()
        c.execute("""
            SELECT Ensembl_Protein_ID, HGNC_Symbol, count(Ensembl_Protein_ID)
            FROM Proteins
            NATURAL JOIN Proteins2Domains
            GROUP BY Ensembl_Protein_ID
            ORDER BY Ensembl_Protein_ID
            LIMIT ? OFFSET ?
        """, [limit, offset])
        return render_template("protein_list.html", proteins=c.fetchall(), limit=limit, offset=offset)


@app.route("/proteins/<pid>")
def protein_view(pid):
    with get_db() as conn:
        c = conn.cursor()
        c.execute("""
            SELECT Ensembl_Protein_ID, Ensembl_Transcript_ID, HGNC_Symbol, count(Ensembl_Protein_ID)
            FROM Proteins
            NATURAL JOIN Proteins2Domains
            WHERE Ensembl_Protein_ID = ?
            GROUP BY Ensembl_Protein_ID
        """, [pid])
        protein = c.fetchone()
        if protein is None:
            abort(404)
        c.execute("""
            SELECT p1.Interpro_ID, Interpro_Short_Description, count(p2.Ensembl_Protein_ID)
            FROM Domains
            NATURAL JOIN Proteins2Domains AS p1
            LEFT JOIN Proteins2Domains AS p2 ON p1.Interpro_ID = p2.Interpro_ID
            WHERE p1.Ensembl_Protein_ID = ?
            GROUP BY p1.Interpro_ID
            ORDER BY Interpro_Short_Description
        """, [pid]);
        domains = c.fetchall()
        return render_template("protein_view.html", protein=protein, domains=domains)
