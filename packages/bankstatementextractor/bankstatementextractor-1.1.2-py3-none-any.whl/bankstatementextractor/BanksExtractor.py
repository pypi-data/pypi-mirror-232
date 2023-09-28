import base64
import cv2
import io
import numpy as np
import re
from datetime import datetime
from PIL import Image
from bankstatementextractor.bank_utils import *
from bankstatementextractor.banks import Banks
from pdf2image import convert_from_bytes
import fitz  # PyMuPDF library
import PyPDF2  # PyPDF2 library
import os
import subprocess
import torch
from pdf2image import convert_from_path
from unidecode import unidecode
import pandas as pd
import itertools    
os.sys.path
from io import StringIO
from io import BytesIO
import pkg_resources


class BankExtractor:

    def __init__(self):
        """
        This is the initialization function of a class that imports a spoof model and loads an BS
        extractor.
        """
        self.bank_labels = ["adib_1","cbd_1","liv_1"]
    #     self.bank_labels = {
    # #                 "adcb_1": extract_adcb_1,
    # #                 "adcb_2": extract_adcb_2,
    # #                 "adcb_3": extract_adcb_3,
    # #                 "adcb_4": extract_adcb_4,
    # #                 "adcb_5": extract_adcb_5,
    # #                 "adcb_6": extract_adcb_6,
    #                 "adib_1": extract_adib_1,
    # #                 "adib_2": extract_adib_2,
    # #                 "adib_3": extract_adib_3,
    # #                 "ajman_1": extract_ajman_1,
    # #                 "ajman_2": extract_ajman_2,
    # #                 "ajman_3": extract_ajman_3,
    # #                 "alhilal_1":extract_alhilal_1,
    # #                 "alhilal_2":extract_alhilal_2,
    # #                 "alhilal_3":extract_alhilal_3,
    #                 "cbd_1": extract_cbd_1,
    # #                 "citi_1": extract_citi_1,
    # #                 "dib_1": extract_dib_1,
    # #                 "ei_1": extract_ei_1,
    # #                 "ei_2": extract_ei_2,
    # #                 "ei_3": extract_ei_3,
    # #                 "ei_4": extract_ei_4,
    # #                 "enbd_1": extract_enbd_1,
    # #                 "enbd_2": extract_enbd_2,
    # #                 "enbd_3": extract_enbd_3,
    # #                 "enbd_4": extract_enbd_4,
    # #                 "fab_1": extract_fab_1,
    # #                 "fab_2": extract_fab_2,
    # #                 "fab_3": extract_fab_3,
    # #                 "hsbc_1": extract_hsbc_1,
    # #                 "hsbc_2": extract_hsbc_2,
    #                 "liv_1": extract_liv_1,
    # #                 "mashreq_1": extract_mashreq_1,
    # #                 "mashreq_2": extract_mashreq_2,
    # #                 "mashreq_3": extract_mashreq_3,
    # #                 "rak_1": extract_rak_1,
    # #                 "sc_1": extract_sc_1,
    # #                 "sc_2": extract_sc_2,
    # #                 "sib_1": extract_sib_1,
    # #                 "sib_2": extract_sib_2
    #     }    
    
    def __check_pdf_metadata(self, pdf_bytes):
        # Define the lists of good and bad creator and producer strings
        creator_lst_good = [
            "3-Heights(TM) Image to PDF Converter",
            "PDFium",
            "pdfmake",
            "Style Report",
            "Crystal Reports",
            "JasperReports",
            "wkhtmltopdf 0.12.6",
            "wkhtmltopdf",
            "Ricoh Americas Corporation",
            "BIRT Report Engine .",
            "BIRT Engine",
            "FreeFlow VI eCompose 15.0.3.0",
            "iECCM, using PDF Engine.",
            "STANDARD CHARTERED BANK",
            "PDFKit",
            "Octagon 5.0",
            "alrajhi bank",
            "GMC Software AG",
            "HP Exstream Version",
            "OpenText Exstream Version",
            "vDOX"
        ]

        creator_lst_bad = [
            "Chrome",
            "Mozilla",
            "Microsoft",
            "Safari",
            "Samsung",
            "Acrobat",
            "macOS",
        ]

        producer_lst_good = [
            "iText",
            "pdfmake",
            "Ricoh Americas Corporation",
            "Powered By Crystal",
            "Style Report",
            "Qt 4.8.7"
        ]

        producer_lst_bad = [
            "3-Heights(TM)",
            "pdfium",
            "ilovePDF",
            "iOS",
            "macOS Version 13.3.1 (a) (Build 22E772610a) Quartz PDFContext",
            "OpenPDF 1.3.26",
            "PSPDFKit",
            "Tango+ PDF Writer",
            "excel",
            "canva",
            "word"
        ]


        try:
            pdfinfo_output = subprocess.Popen(["pdfinfo", "-"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
            # Pass the PDF content to pdfinfo
            pdfinfo_output, pdfinfo_error = pdfinfo_output.communicate(input=pdf_bytes)

            if pdfinfo_output.returncode != 0:
                return False, "Error running pdfinfo: " + pdfinfo_error.strip()
        except FileNotFoundError:
            return False, "pdfinfo command not found. Make sure it's installed and in your PATH."

        # Extract the creator and producer strings, created_at, and modified_at from the pdfinfo output
        creator_string = None
        producer_string = None
        created_at = None
        modified_at = None

        for line in pdfinfo_output.splitlines():
            if line.startswith("Creator:"):
                creator_string = line[len("Creator:"):].strip()
            elif line.startswith("Producer:"):
                producer_string = line[len("Producer:"):].strip()
            elif line.startswith("CreationDate:"):
                created_at = line[len("CreationDate:"):].strip()
            elif line.startswith("ModDate:"):
                modified_at = line[len("ModDate:"):].strip()

        # Check conditions based on the presence of strings in the lists and created/modified timestamps
        if creator_string in creator_lst_good and producer_string in producer_lst_good:
            return True, None
        elif creator_string in creator_lst_good and producer_string in producer_lst_bad:
            return False, "Upload a non-edited PDF"
        elif creator_string in creator_lst_bad and producer_string in producer_lst_good:
            return False, "Upload a non-edited PDF"
        elif creator_string in creator_lst_bad and producer_string in producer_lst_bad:
            return False, "Upload a non-edited PDF"
        elif creator_string not in creator_lst_good + creator_lst_bad and producer_string in producer_lst_good:
            if created_at == modified_at:
                return True, None
            else:
                return False, "Upload a non-edited PDF"
        elif creator_string not in creator_lst_good + creator_lst_bad and producer_string in producer_lst_bad:
            return False, "Upload a non-edited PDF"
        elif creator_string in creator_lst_good and producer_string not in producer_lst_good + producer_lst_bad:
            if created_at == modified_at:
                return True, None
            else:
                return False, "Upload a non-edited PDF"
        elif creator_string in creator_lst_bad and producer_string not in producer_lst_good + producer_lst_bad:
            return False, "Upload a non-edited PDF"
        else:
            if created_at == modified_at:
                return True, None
            else:
                return False, "Upload a non-edited PDF"

        print("Creator:", creator_string)
        print("Producer:", producer_string)
        print("CreationDate:", created_at)
        print("ModDate:", modified_at)    

    # Function to convert PDF to images using pdf2image library
    def convert_pdf_to_images(self, pdf_content_stream):
        try:
            images = convert_from_bytes(pdf_content_stream.read(), dpi=300)
            return images
        except Exception as e:
            return []
    
    def __process_pdf_and_detect_labels(self, pdf_content, confidence_threshold=0.85):
        try:
            # Convert the PDF content bytes into a readable stream
            pdf_content_stream = BytesIO(pdf_content)

            # Convert the first page of the PDF to an image
            images = self.convert_pdf_to_images(pdf_content_stream)

            if images:
                # Convert PIL image to a bytes-like object
                img_byte_array = BytesIO()
                images[0].save(img_byte_array, format='JPEG')
                img_byte_array.seek(0)

                # Load the YOLOv5 model
                model_path = pkg_resources.resource_filename('bankstatementextractor', 'models/best.pt')
                model = torch.hub.load('ultralytics/yolov5', 'custom', path=model_path)

                # Load the image from the bytes-like object
                img = Image.open(img_byte_array)

                # Perform inference
                results = model(img)

                # Get bounding box coordinates, confidence scores, and labels
                boxes = results.pred[0][:, :4].cpu().numpy()
                confidences = results.pred[0][:, 4].cpu().numpy()
                labels = results.pred[0][:, 5].cpu().numpy().astype(int)

                detected_labels = []

                # Filter detections based on confidence threshold and collect labels
                for box, confidence, label in zip(boxes, confidences, labels):
                    if confidence >= confidence_threshold:
                        label_name = model.names[label]
                        detected_labels.append(label_name)

                return detected_labels
            else:
                return []
        except Exception as e:
            return []
            
            
    def extract(self, pdf_bytes):
        data=[]
        # Check PDF metadata
        metadata_result, metadata_message = self.__check_pdf_metadata(pdf_bytes)
        if metadata_result:
            # Process PDF and detect labels
            detected_labels = self.__process_pdf_and_detect_labels(pdf_bytes)
            if detected_labels:
                print("Detected Labels:", detected_labels)
                banks = Banks()
                for label in detected_labels:
                    if label in self.bank_labels:
                        data.append(getattr(banks, label)(pdf_bytes))
                        # bank_labels[label](file_path)  # Call the corresponding function with the file_path
                    else:
                        print(f"No function found for label: {label}")
            else:
                print("No labels detected.")
        else:
            print("Metadata Check Failed:", metadata_message)
        
        return data
        
