"""
Authors: Kyle Holmberg and Zoe Olson
Email: kylemh@protonmail.com or zoeo@cs.uoregon.edu

Database System and Data Visualization Project
CIS407 and CIS451 at the University of Oregon

Flask front-end for MySQL database-driven visualizations and queries
"""

from flask import Flask, request, render_template
import pandas
from sqlalchemy import create_engine


app = Flask(__name__)


@app.route('/')
def index():
    con = create_engine('mysql+mysqldb://zoeo:Moraga17.@ix.cs.uoregon.edu:3640/fpl', echo=False)
    #get data
    datar = pandas.read_sql('SELECT * FROM players', con)

    return render_template('index.html', table=datar)


@app.route('/Player', methods = ['GET', 'POST'])
def players():
    con=create_engine('mysql+mysqldb://zoeo:Moraga17.@ix.cs.uoregon.edu:3640/fpl', echo=False)
    country = request.form['country']
    data=pandas.read_sql("SELECT id, nationality FROM Player WHERE nationality LIKE '" + country + "'", con)
    # cursor.execute("SELECT id, nationality FROM players WHERE nationality LIKE '" + country + "'")
    # entries = [dict(id=row[0], nationality=row[1]) for row in datar]
    entries = data.T.to_dict().values()
    return render_template('players.html', entries = entries)


if __name__ == "__main__":
    app.run(host='128.223.4.35', port=5558, debug=True)
