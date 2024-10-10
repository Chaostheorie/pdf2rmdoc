# pdf2rmdoc

A simple tool to translate PDF files into RMDOC notebooks for the reMarkable Paper Pro. It also lets you upload them to the tablet automatically.

## Usage
```
usage: pdf2rmdoc [-h] [-o OUTPUT] [-u IP] [--template-name {none,P Grid small,P Grid medium}]
                 [-n NAME]
                 input_pdf

Translate a PDF file to an RMDOC for reMarkable Paper Pro

positional arguments:
  input_pdf

options:
  -h, --help            show this help message and exit
  -o OUTPUT, --output OUTPUT
                        Name of the output file
  -u IP, --upload IP    IP of the device to upload to (overloads --output) f.ex. 10.11.99.1
  --template-name {none,P Grid small,P Grid medium}
  -n NAME, --name NAME

This program requires drawj2d to work. Please make sure it is installed.
```

## Credits

This program is inspired by [pdf2rmnotebook](https://github.com/JCN-9000/pdf2rmnotebook). It too uses [drawj2d](https://sourceforge.net/projects/drawj2d) to process the PDF files into .RM pages.
