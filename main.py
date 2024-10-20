from pypdf import PdfReader
from os.path import splitext, basename
from datetime import datetime
from zipfile import ZipFile
from uuid import uuid4 as _uuid4
from subprocess import Popen
from os import unlink
from io import BytesIO
import requests
import argparse
import tempfile
import json

SCALE = ".75"

def translate_page(pdf_name, page_idx):
    outf = tempfile.mktemp()
    inf = tempfile.mktemp()
    with open(inf, 'w') as e:
        e.write(
f"""
moveto 0 0
image {{{pdf_name}}} {page_idx + 1} 0 0 {SCALE}
"""
        )
    # drawj2d -q -T rm -o /tmp/tmp.hMicOX0mJx/Notebook/02af22c3-c444-4c8a-ae9b-73b7625be940/0.rm /tmp/tmp.hMicOX0mJx/P_0.hcl
    proc = Popen(['drawj2d', '-q', '-T', 'rm', '-o', outf, inf])
    proc.wait()
    unlink(inf)
    return outf

def uuid4():
    return str(_uuid4())

def timestamp():
    return int(datetime.now().timestamp() * 1000)

def generate_idx(idx):
    v_0, v_1 = divmod(idx, 26)
    c_0, c_1 = chr(v_0 + ord('b')), chr(v_1 + ord('a'))
    return c_0 + c_1 

def main():
    args = argparse.ArgumentParser(
        prog="pdf2rmdoc",
        description="Translate a PDF file to an RMDOC for reMarkable Paper Pro",
        epilog="This program requires drawj2d to work. Please make sure it is installed."
    )

    args.add_argument("input_pdf")
    args.add_argument("-o", "--output", required=False, help="Name of the output file")
    args.add_argument("-u", "--upload", required=False, help="Upload to 10.11.99.1 (overloads --output)", action='store_true')
    args.add_argument("--template-name", choices=['none', 'P Grid small', 'P Grid medium'], default='none')
    args.add_argument("-n", "--name")
    args = args.parse_args()

    in_pdf = args.input_pdf
    doc_name = args.name or splitext(basename(in_pdf))[0]
    template_name = args.template_name
    out_name = args.output or f"{splitext(basename(in_pdf))[0]}.rmdoc"

    document_uuid = uuid4()

    pdf_file = PdfReader(in_pdf)

    template_addon_file = {
        "template": {
            "timestamp": "1:1",
            "value": template_name
        },
    } if template_name else {}

    bytes_to_upload = BytesIO()
    
    with ZipFile(bytes_to_upload if args.upload else out_name, 'w') as output_zip:
        page_list = [
            {
                "id": uuid4(),
                "idx": {
                    "timestamp": "1:2",
                    "value": generate_idx(index)
                },
                **template_addon_file,
            } for index in range(len(pdf_file.pages))
        ]

        output_zip.writestr(f"{document_uuid}.metadata", f"""
            {{
                "createdTime": "{timestamp()}",
                "lastModified": "{timestamp()}",
                "lastOpened": "{timestamp()}",
                "lastOpenedPage": 0,
                "parent": "",
                "pinned": false,
                "type": "DocumentType",
                "visibleName": "{doc_name}"
            }}
        """)
        print("Written content table.")
        output_zip.writestr(f"{document_uuid}.content", f"""
            {{
                "cPages": {{
                    "original": {{
                        "timestamp": "0:0",
                        "value": -1
                    }},
                    "pages": {json.dumps(page_list)}
                }},
                "coverPageNumber": -1,
                "customZoomCenterX": 0,
                "customZoomCenterY": 936,
                "customZoomOrientation": "portrait",
                "customZoomPageHeight": 1872,
                "customZoomPageWidth": 1404,
                "customZoomScale": 1,
                "documentMetadata": {{
                }},
                "extraMetadata": {{
                    "LastActiveTool": "primary",
                    "LastBallpointv2Color": "Red",
                    "LastBallpointv2Size": "2",
                    "LastEraserColor": "Black",
                    "LastEraserSize": "2",
                    "LastEraserTool": "Eraser",
                    "LastHighlighterv2Color": "ArgbCode",
                    "LastHighlighterv2ColorCode": "4294951820",
                    "LastHighlighterv2Size": "1",
                    "LastPen": "Ballpointv2",
                    "LastPencilv2Color": "Red",
                    "LastPencilv2Size": "3",
                    "LastSelectionToolColor": "Black",
                    "LastSelectionToolSize": "2",
                    "SecondaryHighlighterv2Color": "ArgbCode",
                    "SecondaryHighlighterv2ColorCode": "4294962549",
                    "SecondaryHighlighterv2Size": "1",
                    "SecondaryPen": "Highlighterv2"
                }},
                "fileType": "notebook",
                "fontName": "",
                "formatVersion": 2,
                "lineHeight": -1,
                "margins": 125,
                "orientation": "portrait",
                "pageCount": 6,
                "pageTags": [],
                "sizeInBytes": "430763",
                "tags": [
                ],
                "textAlignment": "justify",
                "textScale": 1,
                "zoomMode": "bestFit"
            }}
        """)
        print("Written metadata table.")

        for i, page_def in enumerate(page_list):
            page_file_name = translate_page(in_pdf, i)
            output_zip.write(page_file_name, f'{document_uuid}/{page_def['id']}.rm')
            unlink(page_file_name)
            print(f"Written page {i + 1}.")
    print("File written.")

    if args.upload:
        bytes_to_upload.seek(0)
        print(f"Uploading to 10.11.99.1")
        resp = requests.post(f"http://10.11.99.1/upload", files={'file': ('file.rmdoc', bytes_to_upload, 'application/octet-stream')}).text
        print("Uploaded")

    


if __name__ == "__main__": main()
