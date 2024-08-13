from flask import Flask, request, jsonify
import sqlite3


def get_connection():
    try:
        conn = sqlite3.connect('database.db')
        return conn
    except sqlite3.Error as e:
        print(f"Database connection error: {e}")
        return None


def query_database(query_type, data):
    conn = get_connection()
    if conn is None:
        raise ConnectionError("Failed to connect to the database")

    cursor = conn.cursor()
    results = []

    try:
        if query_type == 'order_id':
            cursor.execute('SELECT * FROM sampleData WHERE ORDER_ID = ?', (data,))
        elif query_type == 'pid':
            cursor.execute('SELECT * FROM sampleData WHERE PID = ?', (data,))
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
    except sqlite3.Error as e:
        print(f"Database query error: {e}")
        results = []
    finally:
        conn.close()

    return results


app = Flask(__name__)


@app.route('/data', methods=['GET', 'POST'])
def database():
    conn = get_connection()
    if conn is None:
        return 'Failed to connect to the database', 500

    cursor = conn.cursor()
    if request.method == 'GET':
        try:
            cursor.execute("SELECT * FROM sampleData")
            sample = [
                dict(PID=row[0], ORDER_ID=row[1], FIN=row[2], EN_LOC_NURSE_UNIT_DISP=row[3], ACCN=row[4],
                     ORDER_MNEMONIC=row[5], TASK_ASSAY_CD=row[6], R_TASK_ASSAY_DISP=row[7], RESULT_VALUE_NUMERIC=row[8],
                     PERFORM_DT_TM=row[9])
                for row in cursor.fetchall()
            ]
            if sample:
                return jsonify(sample)
            else:
                return jsonify([]), 204
        except sqlite3.Error as e:
            return f"Database query error: {e}", 500
        finally:
            conn.close()

    if request.method == 'POST':
        if not request.is_json:
            return 'Content-Type must be application/json', 415

        new_entry = request.get_json()
        required_fields = ["PID", "ORDER_ID", "FIN", "EN_LOC_NURSE_UNIT_DISP", "ACCN",
                           "ORDER_MNEMONIC", "TASK_ASSAY_CD", "R_TASK_ASSAY_DISP",
                           "RESULT_VALUE_NUMERIC", "PERFORM_DT_TM"]

        missing_fields = [field for field in required_fields if field not in new_entry]
        if missing_fields:
            return f"Missing fields: {', '.join(missing_fields)}", 400

        try:
            sql = """INSERT INTO sampleData (PID, ORDER_ID, FIN, EN_LOC_NURSE_UNIT_DISP, ACCN, ORDER_MNEMONIC,
            TASK_ASSAY_CD, R_TASK_ASSAY_DISP, RESULT_VALUE_NUMERIC, PERFORM_DT_TM)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"""
            cursor.execute(sql, (
                new_entry["PID"], new_entry["ORDER_ID"], new_entry["FIN"], new_entry["EN_LOC_NURSE_UNIT_DISP"],
                new_entry["ACCN"], new_entry["ORDER_MNEMONIC"], new_entry["TASK_ASSAY_CD"],
                new_entry["R_TASK_ASSAY_DISP"], new_entry["RESULT_VALUE_NUMERIC"], new_entry["PERFORM_DT_TM"]
            ))
            conn.commit()
            return 'Data added successfully', 201
        except sqlite3.Error as e:
            return f"Database insert error: {e}", 500
        finally:
            conn.close()


@app.route('/fetch', methods=['GET'])
def fetch():
    try:
        type_param = request.args.get('type')
        order_id = request.args.get('ORDER_ID')
        pid = request.args.get('PID')

        if not type_param:
            raise ValueError("Type parameter is missing")

        if type_param.lower() == 'order_id':
            if not order_id:
                raise ValueError("Order ID parameter is missing")
            results = query_database('order_id', order_id)
        elif type_param.lower() == 'pid':
            if not pid:
                raise ValueError("PID parameter is missing")
            results = query_database('pid', pid)
        else:
            raise ValueError("Invalid type parameter")

        return jsonify(results)
    except ValueError as ve:
        return jsonify({'error': str(ve)}), 400
    except Exception as e:
        app.logger.error(f"Error in fetch: {e}")
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)
