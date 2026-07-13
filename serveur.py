import sqlite3
from flask import Flask, render_template, Response, abort

app = Flask(__name__)
DB_PATH = "carte_annecy.mbtiles"

@app.route('/')
def accueil():
    # Affiche la page web
    return render_template('index.html')

@app.route('/tiles/<int:z>/<int:x>/<int:y>.png')
def get_tile(z, x, y):
    # Leaflet utilise XYZ, mais MBTiles utilise TMS (axe Y inversé)
    # On recalcule le Y pour que la requête SQL trouve la bonne image
    tms_y = (2 ** z - 1) - y
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # La requête SQL pour extraire l'image binaire de la tuile
        cursor.execute(
            "SELECT tile_data FROM tiles WHERE zoom_level=? AND tile_column=? AND tile_row=?",
            (z, x, tms_y)
        )
        row = cursor.fetchone()
        conn.close()

        if row:
            # On renvoie l'image au navigateur
            return Response(row[0], mimetype='image/png')
        else:
            abort(404)
            
    except sqlite3.Error as e:
        print(f"Erreur SQL: {e}")
        abort(500)

if __name__ == '__main__':
    app.run(debug=True, port=5000)