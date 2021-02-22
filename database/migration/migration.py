import pymysql
import config

old_conn = pymysql.connect(host=config.DB_HOST,
                           db='proyectos3',
                           user=config.DB_USER,
                           password=config.DB_PASS,
                           charset='utf8mb4',
                           cursorclass=pymysql.cursors.DictCursor)

new_conn = pymysql.connect(host=config.DB_HOST,
                           db='proyectos3_test',
                           user=config.DB_USER,
                           password=config.DB_PASS,
                           charset='utf8mb4',
                           cursorclass=pymysql.cursors.DictCursor)

with old_conn.cursor() as old_cur:
    with new_conn.cursor() as new_cur:
        old_cur.execute("SELECT DISTINCT(name) FROM Indexes")
        idxs = [(idx['name'],) for idx in old_cur.fetchall()]

        new_cur.executemany("INSERT INTO indexes(name) VALUES(%s)", idxs)
        new_cur.execute("SELECT * FROM indexes")
        all_idxs = {idx['name']: idx['id'] for idx in new_cur.fetchall()}

        old_cur.execute("SELECT * FROM Indexes")
        new_values = [(all_idxs[idx['name']], idx['value'], idx['variation'], idx['date']) for idx in old_cur.fetchall()]
        if new_values:
            new_cur.executemany("""INSERT INTO `values`(index_id, value, variation, timestamp)
                                   VALUES (%s, %s, %s, %s)
                                """, new_values)
            new_conn.commit()

old_conn.close()
new_conn.close()
