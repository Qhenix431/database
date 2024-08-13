from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import requests
import logging

app = Flask(__name__)
DATABASE = '/Users/sidharthdeepak/Desktop/test/pythonProject/database.db'

logging.basicConfig(level=logging.DEBUG)

def get_db_connection():
    try:
        conn = sqlite3.connect(DATABASE)
        conn.row_factory = sqlite3.Row
        return conn
    except Exception as e:
        app.logger.error(f"Error connecting to database: {e}")
        return None

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/url')
def url_master():
    try:
        conn = get_db_connection()
        urls = conn.execute('SELECT * FROM URL_MASTER').fetchall()
        conn.close()
        return render_template('index.html', urls=urls)
    except Exception as e:
        app.logger.error(f"Error fetching URLs: {e}")
        return render_template('index.html', urls=[])

@app.route('/add', methods=('GET', 'POST'))
def add():
    if request.method == 'POST':
        url_name = request.form.get('url_name')
        url = request.form.get('url')
        url_type = request.form.get('url_type')

        if not url_name or not url or not url_type:
            app.logger.error(f"Missing form data: url_name={url_name}, url={url}, url_type={url_type}")
            return redirect(url_for('add'))

        try:
            conn = get_db_connection()
            conn.execute('INSERT INTO URL_MASTER (URL_NAME, URL, TYPE) VALUES (?, ?, ?)', (url_name, url, url_type))
            conn.commit()
            conn.close()
        except Exception as e:
            app.logger.error(f"Error adding URL: {e}")
        return redirect(url_for('url_master'))
    return render_template('add_update.html', url=None, action="Add")

@app.route('/update/<int:id>', methods=('GET', 'POST'))
def update(id):
    try:
        conn = get_db_connection()
        url = conn.execute('SELECT * FROM URL_MASTER WHERE URL_ID = ?', (id,)).fetchone()

        if not url:
            app.logger.error(f"URL not found for id: {id}")
            return redirect(url_for('url_master'))

        if request.method == 'POST':
            url_name = request.form.get('url_name')
            url = request.form.get('url')
            url_type = request.form.get('url_type')

            if not url_name or not url or not url_type:
                app.logger.error(f"Missing form data: url_name={url_name}, url={url}, url_type={url_type}")
                return redirect(url_for('update', id=id))

            conn.execute('UPDATE URL_MASTER SET URL_NAME = ?, URL = ?, TYPE = ? WHERE URL_ID = ?',
                         (url_name, url, url_type, id))
            conn.commit()
            conn.close()
            return redirect(url_for('url_master'))
        conn.close()
        return render_template('add_update.html', url=url, action="Update")
    except Exception as e:
        app.logger.error(f"Error updating URL: {e}")
        return redirect(url_for('url_master'))

@app.route('/delete/<int:id>', methods=('POST',))
def delete(id):
    try:
        conn = get_db_connection()
        conn.execute('DELETE FROM URL_MASTER WHERE URL_ID = ?', (id,))
        conn.commit()
        conn.close()
    except Exception as e:
        app.logger.error(f"Error deleting URL: {e}")
    return redirect(url_for('url_master'))


@app.route('/fetch-data', methods=['GET', 'POST'])
def fetch_data():
    conn = get_db_connection()
    query_types = conn.execute('SELECT URL_ID as id, URL_NAME as name, TYPE as type FROM URL_MASTER').fetchall()

    # Debugging: Log the query results
    app.logger.debug(f"Query Types: {query_types}")
    results = []

    if request.method == 'POST':
        query_type = request.form.get('query_type_hidden')
        query_id = request.form.get('query_id_hidden')
        data_value = request.form.get('data_value')

        if query_type and data_value:
            try:
                url = conn.execute('SELECT URL FROM URL_MASTER WHERE URL_ID=?', (query_id,)).fetchone()[0]
                params = {
                    'type': query_type,
                    query_type: data_value
                }

                response = requests.get(url, params=params)

                if response.status_code == 200:
                    results = response.json()
                else:
                    app.logger.error(f"Failed to fetch data. Status code: {response.status_code}")
            except Exception as e:
                app.logger.error(f"Error fetching data: {e}")
        else:
            app.logger.error("Missing form data: query_type or data_value")

    conn.close()
    return render_template('fetchData.html', query_types=query_types, results=results)


if __name__ == '__main__':
    app.run(debug=True, port=5001)
