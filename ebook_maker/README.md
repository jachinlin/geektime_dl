a tool to make mobi-format file wich could be load into Kindle

## public api:

maker.make_book(source_dir, output_dir)

input args:
- source_dir : directory contains all source files, which includes:
    - a plain text file named `toc.md` with toc information
    - html files for chapter

- output: output directory of the ebook
