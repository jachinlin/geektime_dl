
import os
from geektime_ebook.maker import render_all_source_files
from ebook_maker.maker import make_ebook


source_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'output/ebook')
output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'output/ebook_output')

render_all_source_files()

# make_ebook(source_dir=source_dir, output_dir=output_dir)


