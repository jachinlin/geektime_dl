
import os
from geektime_ebook.maker import test
from ebook_maker.maker import make_ebook


source_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'output/ebook')
output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'output/ebook_output')

# test()

make_ebook(source_dir=source_dir, output_dir=output_dir)


