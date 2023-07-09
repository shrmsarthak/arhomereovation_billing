from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
import pickle

from reportlab.pdfgen import canvas
import pathlib
from pathlib import Path

from random import *
from datetime import datetime

import os

from django.core.files.storage import FileSystemStorage
from django.http import FileResponse

BASE_DIR = Path(__file__).resolve().parent.parent

def index(request):

    if request.method == "POST":
        name = request.POST.get('name')
        address = request.POST.get("address")
        province = request.POST.get("province")
        country = request.POST.get("country")
        postalcode = request.POST.get("postalcode")

        request.session["name"] = name
        request.session["address"] = address
        request.session["province"] = province
        request.session["country"] = country
        request.session["postalcode"] = postalcode

        pickle_out = open("invoice.pickle","wb")
        pickle.dump({}, pickle_out)
        pickle_out.close()

        return redirect('index_two')

    return render(request, "index.html")

def index_two(request):

    items_dict = {}

    if 'additem' in request.POST:

        try:
            pickle_in = open("invoice.pickle","rb")
            items_dict = pickle.load(pickle_in)
        except:
            pass

        description = request.POST.get("description")
        quantityorarea = request.POST.get("quantityorarea")
        unitprice = request.POST.get("unitprice")

        if(len(description) != 0 and len(quantityorarea) !=0 and len(unitprice) != 0):
            request.session["description"] = description
            request.session["quantityorarea"] = quantityorarea
            request.session["unitprice"] = unitprice

            items_dict["item"+str(len(items_dict))] = {'description':description,
            'quantityorarea':quantityorarea,
            'unitprice':unitprice}

            pickle_out = open("invoice.pickle","wb")
            pickle.dump(items_dict, pickle_out)
            pickle_out.close()

            print(items_dict)

        else:
            return render(request, 'index_two.html', {"mymessage": "Please enter data in the given field.","Flag":"True"})

    elif 'generateinvoice' in request.POST:


        pickle_in = open("invoice.pickle","rb")
        items_dict = pickle.load(pickle_in)

        name = request.session["name"]
        address = request.session["address"]
        province = request.session["province"]
        country = request.session["country"]
        postalcode = request.session["postalcode"]
        postalcode = postalcode[:3]+" "+postalcode[3:]

        can = canvas.Canvas("final_invoice.pdf")

        #head
        file_name = os.path.join(BASE_DIR, 'myapp/static/myapp/header.png')

        #billed to
        can.drawImage(file_name, 0, 570, width=570, preserveAspectRatio=True, mask='auto')
        can.setFont("Helvetica", 10)

        can.drawString(25, 720, "Date: "+datetime.today().strftime('%Y-%m-%d'))
        can.drawString(25, 710, "Invoice No. "+str(randint(1, 100000)))

        can.drawString(25, 680, "BILLED TO")
        can.drawString(25, 660, name)
        can.drawString(25, 650, address+", "+province)
        can.drawString(25, 640, country+" "+postalcode)

        can.line(570, 610, 25, 610)
        #owner name
        can.setFont("Helvetica", 10)

        can.drawString(345, 700, "Amandeep Singh")
        can.drawString(345, 680, "AR Home Renovation & Construction Inc. C/O")
        can.drawString(345, 670, "411 Popular Avenue, Summerside")
        can.drawString(345, 660, "Canada C1N 2B9")
        

        can.drawString(25, 595, "Description")
        can.drawString(225, 595, "Quantity or Area")
        can.drawString(400, 595, "Price")
        can.drawString(520, 595, "Total")

        can.line(570, 585, 25, 585)

        description_array = []
        quantityorarea_array = []
        unitprice_array = []
        total_array = []

        for i in items_dict:
            description_array.append(items_dict.get(i)["description"])
            quantityorarea_array.append(items_dict.get(i)["quantityorarea"])
            unitprice_array.append(items_dict.get(i)["unitprice"])
            total_array.append(str(int(items_dict.get(i)["quantityorarea"]) * int(items_dict.get(i)["unitprice"])))

        base  = 595
        current_base = 0

        for i in range(len(description_array)):
            can.drawString(25, base-(i+1)*25, description_array[i])
            can.drawString(260, base-(i+1)*25, quantityorarea_array[i])
            can.drawString(405, base-(i+1)*25, "$"+unitprice_array[i])
            can.drawString(525, base-(i+1)*25, "$"+total_array[i])

            if i == len(description_array)-1:
                current_base = base-(i+1)*25

        can.line(570, current_base-12, 25, current_base-12)

        #sub total
        subtotal = 0
        for i in total_array:
            subtotal += int(i)

        can.drawString(405, current_base-30, "Sub Total")
        can.drawString(525, current_base-30, "$"+str(subtotal))

        #Total after tax
        can.drawString(405, current_base-50, "Tax (15%)")
        can.drawString(525, current_base-50, "$"+str(subtotal*.15))

        can.line(570, current_base-60, 400, current_base-60)

        can.drawString(405, current_base-80, "Total")
        can.drawString(525, current_base-80, "$"+str(subtotal + (subtotal*.15)))

        can.drawString(25, 175, "CONTACT INFORMATION")
        can.drawString(25, 150, "Phone : 647-622-4449")
        can.drawString(25, 140, "Email: Arhomerenovation1@gmail.com")
        can.drawString(25, 130, "Website: https://arhomerenovation.ca/")

        can.drawString(450, 130, "HST No. 732134002RT001")

        footer_filename = os.path.join(BASE_DIR, 'myapp/static/myapp/footer.png')

        can.drawImage(footer_filename, 0, -130, width=570, preserveAspectRatio=True, mask='auto')
        
        can.showPage()
        can.save()


        return render(request, 'index_two.html', {"mymessage": "Invoice Generated.","Flag":"True"})


    return render(request, "index_two.html")


