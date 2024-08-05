from flask import Flask, request, jsonify, render_template
import sqlite3

def get_connection():
    conn = None
    try:
        conn = sqlite3.connect('database.db')
    except sqlite3.error as e:
        print(e)
    return conn

def query_database(type ,data):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    results = []
    if type == 'order_id':
        cursor.execute('SELECT * FROM sampleData WHERE ORDER_ID =?',(data,))
        rows = cursor.fetchall()

        for row in rows:
            results.append({
                'PID': row[0],
                'ORDER_ID': row[1],
                'FIN': row[2],
                'EN_LOC_NURSE_UNIT_DISP': row[3],
                'ACCN': row[4],
                'ORDER_MNEMONIC': row[5],
                'TASK_ASSAY_CD': row[6],
                'R_TASK_ASSAY_DISP': row[7],
                'RESULT_VALUE_NUMERIC': row[8],
                'PERFORM_DT_TM': row[9]
            })

        conn.close()
        return results
    elif type == 'pid':
        cursor.execute('SELECT * FROM sampleData WHERE PID =?', (data,))
        rows = cursor.fetchall()

        for row in rows:
            results.append({
                'PID': row[0],
                'ORDER_ID': row[1],
                'FIN': row[2],
                'EN_LOC_NURSE_UNIT_DISP': row[3],
                'ACCN': row[4],
                'ORDER_MNEMONIC': row[5],
                'TASK_ASSAY_CD': row[6],
                'R_TASK_ASSAY_DISP': row[7],
                'RESULT_VALUE_NUMERIC': row[8],
                'PERFORM_DT_TM': row[9]
            })

        conn.close()
        return results

app = Flask(__name__)

@app.route('/')
def index():
   return render_template('index.html')

@app.route('/data', methods=['GET', 'POST'])
def database():
    conn = get_connection()
    cur = conn.cursor()
    if request.method == 'GET':
        cursor = conn.execute("SELECT * FROM sampleData")
        sample = [
            dict( PID=row[0], ORDER_ID=row[1], FIN=row[2], EN_LOC_NURSE_UNIT_DISP=row[3], ACCN=row[4],
                  ORDER_MNEMONIC=row[5], TASK_ASSAY_CD=row[6], R_TASK_ASSAY_DISP=row[7], RESULT_VALUE_NUMERIC=row[8],
                  PERFORM_DT_TM=row[9])
            for row in cursor.fetchall()
        ]
        if sample is not None:
            return jsonify(sample)


    if request.method == 'POST':
        if request.is_json:
            new_entry = request.get_json()
            if not new_entry:
                return 'Invalid input', 400

            new_pid = new_entry.get("PID")
            new_order_id = new_entry.get("ORDER_ID")
            new_fin = new_entry.get("FIN")
            new_EN_LOC_NURSE_UNIT_DISP = new_entry.get("EN_LOC_NURSE_UNIT_DISP")
            new_accn = new_entry.get("ACCN")
            new_order_mnenmonic = new_entry.get("ORDER_MNEMONIC'")
            new_TASK_ASSAY_CD = new_entry.get("TASK_ASSAY_CD")
            new_R_TASK_ASSAY_DISP = new_entry.get("R_TASK_ASSAY_DISP")
            new_RESULT_VALUE_NUMERIC = new_entry.get("RESULT_VALUE_NUMERIC")
            new_PERFORM_DT_TM = new_entry.get("PERFORM_DT_TM")
            sql = """INSERT INTO sampleData (PID, ORDER_ID, FIN, EN_LOC_NURSE_UNIT_DISP, ACCN, ORDER_MNEMONIC,
            TASK_ASSAY_CD, R_TASK_ASSAY_DISP, RESULT_VALUE_NUMERIC, PERFORM_DT_TM)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?) """
            cursor = cur.execute(sql,(new_pid,  new_order_id, new_fin, new_EN_LOC_NURSE_UNIT_DISP,
                                       new_accn, new_order_mnenmonic,new_TASK_ASSAY_CD, new_R_TASK_ASSAY_DISP,
                                       new_RESULT_VALUE_NUMERIC, new_PERFORM_DT_TM))
            conn.commit()
            return f"data added successfully ", 201
        else:
            return 'Content-Type must be application/json', 415


@app.route('/fetch', methods=['GET'])
def fetch_record():
    order_id = request.args.get('ORDER_ID')
    type_check = request.args.get('type')
    pid = request.args.get('PID')
    if not order_id and not pid:
        return 'Invalid input: Missing data', 401
    if not type_check:
        return 'Missing type check', 403
    if type_check not in ['ORDER_ID','PID']:
        return 'Invalid type', 402

    try:
        if order_id:
            data_type = 'order_id'
            results = query_database(data_type, order_id)
        else:
            data_type = 'pid'
            results = query_database(data_type, pid)
    except Exception as e:
        return f'Error querying data: {str(e)}', 500

    return jsonify(results), 200

if __name__ == '__main__':
    app.run(debug=True)
