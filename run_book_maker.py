
import os
import sqlite3
from geektime_ebook.maker import render_all_source_files
from ebook_maker import maker as ebook_maker

db_url = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'spider/output/sqlite3.db')

source_base_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'output/ebook_source')
output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'output/ebook')

# render_all_source_files()


def make_book():
    conn = sqlite3.connect(db_url)

    cur = conn.cursor()
    cur.execute('SELECT column_id, column_title FROM columns ORDER BY column_id')

    columns = cur.fetchall()
    cur.close()
    conn.close()

    for column_id, column_title in columns:
        source_dir = os.path.join(source_base_dir, str(column_id))

        ebook_maker.make_ebook(source_dir=source_dir, output_dir=output_dir)


make_book()




