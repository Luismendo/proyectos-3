import pymysql
import config

conn = pymysql.connect(host=config.HOST,
                       db=config.DB_DATABASE,
                       user=config.DB_USER,
                       password=config.DB_PASS,
                       charset='utf8mb4',
                       cursorclass=pymysql.cursors.DictCursor)

with conn.cursor() as cur:
    cur.execute("SELECT DISTINCT(name) FROM indexes_old")
    idxs = [(idx['name'],) for idx in cur.fetchall()]
    cur.executemany("INSERT INTO indexes(name) VALUES(%s)", idxs)

    cur.execute("SELECT * FROM indexes")
    all_idxs = {idx['name']: idx['id'] for idx in cur.fetchall()}

    cur.execute("SELECT * FROM indexes_old")
    old_idxs = cur.fetchall()

    new_idxs = list()
    for idx in old_idxs:
        new_idxs.append((all_idxs[idx['name']], idx['value'], idx['variation'], idx['date']))

    if new_idxs:
        cur.executemany("""INSERT INTO data(index_id, value, variation, timestamp)
                           VALUES (%s, %s, %s, %s)
                        """, new_idxs)

    cur.execute("SELECT id, company FROM opinions")
    opinions = cur.fetchall()

    opinion_updates = list()
    for opinion in opinions:
        opinion_updates.append((all_idxs[opinion['company']], opinion['id']))

    if opinion_updates:
        cur.executemany("""UPDATE opinions SET index_id = %s
                           WHERE id = %s
                        """, opinion_updates)

    conn.commit()

conn.close()
