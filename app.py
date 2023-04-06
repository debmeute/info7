import sqlite3
from flask import Flask,url_for,render_template,g,request,redirect,make_response,json,Response,jsonify
import matplotlib.pyplot as plt
import numpy as np
from io import BytesIO


DATAB = '../ensembl_hs63_simple.sqlite'
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATAB)
    return db

def get_dbase():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATAB)
        db.row_factory = sqlite3.Row
    return db

def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv

def query_dbase(query, args=(), one=False):
    cur = get_dbase().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv

app=Flask(__name__)

@app.route("/") #racine
def index():
    c=get_db().cursor
    part = []
    for gene in query_db('select distinct atlas_organism_part from Expression where atlas_organism_part is NOT NULL order by atlas_organism_part asc'):
        part += gene
    return render_template('first_page.html', part=part)

@app.route("/parts/<part>/genes")
def gene(part):
    c=get_db().cursor
    ids = []
    for id, name in query_db('SELECT DISTINCT g.ensembl_gene_id, associated_gene_name FROM Genes as g NATURAL JOIN Transcripts as t NATURAL JOIN Expression as e WHERE atlas_organism_part = ? ORDER BY g.ensembl_gene_id',[part]):
        ids.append([id, name])
    return render_template('second_page.html', salut=ids)

@app.route("/genes/<id>")
def gene_id(id):
    c=get_db().cursor
    infos=query_db('SELECT * FROM Genes as g WHERE Ensembl_Gene_ID = ?',[id])
    transcript=[]
    org_parts=[]
    for id_t,start_t,end_t in query_db('SELECT t.Ensembl_Transcript_ID, t.Transcript_Start, t.Transcript_END FROM Genes as g NATURAL JOIN Transcripts as t WHERE Ensembl_Gene_ID = ?',[id]):
        transcript.append([id_t,start_t,end_t])
    for org_part in query_db('SELECT DISTINCT e.Atlas_Organism_Part FROM Expression as e NATURAL JOIN Genes as g NATURAL JOIN Transcripts as t WHERE g.Ensembl_Gene_ID = ? AND atlas_organism_part is NOT NULL ORDER BY Atlas_Organism_Part',[id]):
        org_parts+=org_part
    return render_template('third_page.html', info=infos, t=transcript,org_part=org_parts) #,code_svg=svf

@app.route("/genes/<id>/edit", methods=['POST','GET'])
def form(id):
    infos=query_db('SELECT * FROM Genes as g WHERE Ensembl_Gene_ID = ?',[id])
    if request.method == 'POST':
        n = request.form['g_name']
        b = request.form['band']
        strand = request.form['strand']
        start = request.form['start']
        end = request.form['end']
        connexion = sqlite3.connect(DATAB)
        c=connexion.cursor()
        c.execute("UPDATE Genes SET Chromosome_Name = ?, Band = ?, Strand = ?, Gene_Start = ?, Gene_End = ? WHERE Ensembl_Gene_ID = ?", [n,b,strand,start,end,id])
        connexion.commit()
        connexion.close()
        return redirect(url_for('gene_id',id=id))
    return render_template('formulaire.html', list=infos)

@app.route("/trancripts/<id>")
def transcript(id):
    org_parts=[]
    t_infos=query_db('SELECT * FROM Transcripts WHERE Ensembl_Transcript_ID = ?',[id])
    for org_part in query_db('SELECT DISTINCT e.Atlas_Organism_Part FROM Expression as e NATURAL JOIN Transcripts as t WHERE t.Ensembl_Transcript_ID = ? AND atlas_organism_part is NOT NULL ORDER BY Atlas_Organism_Part',[id]):
        org_parts+=org_part
    return render_template('transcripts.html', info=t_infos, org_part=org_parts)


@app.route("/genes/<id>/parts.png")
def parts_png(id):
    #partie sql query
    c=get_db().cursor
    part = []
    nb=[]
    for gene in query_db('select distinct atlas_organism_part from Expression as e NATURAL Join Transcripts as t where atlas_organism_part is NOT NULL and t.Ensembl_Gene_ID = ? order by atlas_organism_part asc',[id]):
        part += gene
    for org in part:
        num=query_db('SELECT COUNT(DISTINCT t.Ensembl_Transcript_ID) FROM Expression as e NATURAL JOIN Transcripts as t where e.atlas_organism_part = ? and t.Ensembl_Gene_ID = ?',[org,id])
        nb.append(num[0][0])
    #list=query_db('SELECT DISTINCT atlas_organism_part, COUNT(*) FROM Genes as g NATURAL JOIN Transcripts as t NATURAL JOIN Expression as e WHERE g.Ensembl_gene_id = ? and atlas_organism_part is NOT NULL GROUP BY atlas_organism_part',[id])
    #print(list)
    #print(nb[0])
    #matplotlib
    plt.rcdefaults()
    fig, ax = plt.subplots()
    y_pos = np.arange(len(part))
    ax.barh(y_pos, nb, align='center')
    ax.set_yticks(y_pos, labels=part)
    ax.invert_yaxis()  # labels read top-to-bottom
    ax.set_xlabel('Number of related transcript')
    ax.set_title(f'Number of related trasncripts of the gene {id} according to each organsim part')
    fig.tight_layout()
    #plt.show()
    b = BytesIO()
    fig.savefig(b, format="png")

    resp = make_response(b.getvalue())
    resp.headers['content-type'] = 'image/png'
    return resp

    #fabriquer la reponse

@app.route("/genes/<id>/transcripts.svg")
def t_rep(id):
    c=get_db().cursor
    transcript=[]
    for id_t,start_t,end_t in query_db('SELECT t.Ensembl_Transcript_ID, t.Transcript_Start, t.Transcript_END FROM Genes as g NATURAL JOIN Transcripts as t WHERE Ensembl_Gene_ID = ?',[id]):
        transcript.append([id_t,start_t,end_t])
    start=query_db("SELECT Gene_Start, Gene_End FROM Genes WHERE Ensembl_Gene_ID = ?",[id])
    print(start[0])

    svg_string='<svg xmlns="http://www.w3.org/2000/svg" viewBox="-50 -50 100 100">'

    svg_string+='<line x1="-100" y1="-10" x2="100" y2="-10" style="stroke:black"/>'
    svg_string+='<line x1="-100" y1="-15" x2="-100" y2="-5" style="stroke:black"/>'
    svg_string+='<line x1="100" y1="-15" x2="100" y2="-5" style="stroke:black"/>'
    for i in range(len(transcript)):
        svg_string+=draw_rect(transcript[i],start[0][0],start[0][1],i)
    svg_string+='</svg>'
    return Response(svg_string,mimetype='image/svg+xml')

def draw_rect(t,s_s,s_e,num):
    taille_gene = s_e-s_s
    x=200*(t[1]-s_s)/taille_gene-100
    y=10+((num+1)*5)
    taille=(t[2]-t[1])*200/taille_gene
    svg = '<rect x="'+str(x)+'" y="'+str(y)+'" width="'+str(taille)+'" height="0.5" rx="0.05" style="fill:teal"/>'
    return svg


@app.route("/api/genes/<id>",methods=['GET','DELETE'])
def rep_det(id):
    if request.method=='GET':
        c=get_dbase().cursor
        gene = query_dbase('SELECT * FROM Genes WHERE Ensembl_Gene_ID = ?',[id], one=True)
        if gene is None:
            return jsonify({"error":"Ce gène n'existe pas"}),404
        transcripts = query_dbase('SELECT t.Ensembl_Transcript_ID, t.Transcript_Start, t.Transcript_END From Transcripts as t NATURAL JOIN Genes as g WHERE t.Ensembl_Gene_ID = ?',[id])
        list=[]
        for t in transcripts:
            list.append(dict(t))
        gene=dict(gene)
        gene['Transcripts']=list
        return jsonify(gene)
    elif request.method=='DELETE':
        connexion = sqlite3.connect(DATAB)
        c=connexion.cursor()
        c.execute("DELETE FROM Genes WHERE Ensembl_Gene_ID = ?", [id])
        connexion.commit()
        connexion.close()
        return jsonify({"deleted": id})

@app.route("/api/genes/",methods=['GET','POST'])
def genes_100():
    #passer parametre dans url? pour savoir à partir du ombien on prend, et en prendre les 100 premiers
    if request.method=='POST':
        #envoyer requete on ne peut pas le faire avec navigateur, on peut faire avec extension
        #récupérer les données (lire json de la requete qu'on recoit), prendre le json et le mettre sous forme dic, créer requete SQL pour créer nouveau gène, création url
        result=request.get_json('http://127.0.0.1:5000/api/genes/')
        if type(result['Band']) is not str:
            return jsonify({"error":"Band doit etre une chaine"}),404
        connexion = sqlite3.connect(DATAB)
        c=connexion.cursor()
        c.execute("INSERT INTO Genes (Ensembl_Gene_ID, Chrososome_Name, Band, Strand, Gene_Start, Gene_End, Associated_Gene_Name) VALUES (?, ?, ?, ?, ?, ?, ?)", [result['Ensembl_Gene_ID'],result['Chromosome_Name'],result['Band'],result['Strand'],result['Gene_End'],result['Gene_Start'],result['Associated_Gene_Name']])
        connexion.commit()
        connexion.close()
        return jsonify({"create":url_for('rep_det',id=result['Ensembl_Gene_ID'],_external=True)}),201
    elif request.method=='GET':
        args = request.args
        offset = args.get("offset",0)
        gene = query_dbase('SELECT * FROM Genes ORDER BY Ensembl_Gene_ID LIMIT 100 OFFSET '+str(offset))
        list=[]
        for t in gene:
            t = dict(t)
            t['href']=url_for('rep_det',id=t['Ensembl_Gene_ID'],_external=True)
            list.append(t)
        return jsonify(list)
