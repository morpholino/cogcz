#!/usr/bin/env python3.8
"""
titulek:    Jinja2 templating
vysledek:   vysledne html
autor:      medulka
verze:      week24
datum:      od 21. kvetna 2021 a dale
"""

import datetime
import csv
from re import A
from turtle import screensize
from jinja2 import DictLoader, Environment, FileSystemLoader, PackageLoader, select_autoescape, Template
from weasyprint import HTML
import shutil
import os
import base64

#update regularly
DF_DATE = "2.7.2021"
ACTUAL_SAMPLE_SIZE = "5 004"
SAMPLES_FOR_ANALYSES = "4 790"
SAMPLES_WEEKS = '4 113'
SAMPLES_REGIONS ='4 894'
LINEAGE_COUNTS = "54"
WEEK = "26"
SEQUENCED_RATIO = "0,5-2,5"
MUTATIONS_COUNT = "4 581"
NOW=datetime.datetime.now().strftime('%d. %m. %Y' )
TYDNY_NAZPET = "15"

# #vytvoreni prostredi
# env = Environment(
#     loader = PackageLoader('__main__', '.'),
#     autoescape = select_autoescape(['html']),
#     extensions=['jinja2.ext.debug']
#     )

#vytvoreni prostredi
env = Environment(
    loader = FileSystemLoader('.'),
    autoescape = select_autoescape(['html']),
    extensions=['jinja2.ext.debug']
    )

#seznam kapitol - obsah
def precti_seznam_kapitol(filename):
    seznam_kap = []  
    with open(filename, newline = '') as f:
        csvreader = csv.reader(f)
        for row in csvreader:
            seznam_kap.append(row)
    return seznam_kap 

#vytvareni tabulek
def input_table_tsv(src_file):
    "a text file transformation to an item"
    with open(src_file) as g:
        lst = []
        for line in g:
            items = line.split('\t')
            items = [item.strip("\"").strip("\n").strip(" ") for item in items]
            lst.append(items)    
        for line in lst:
            if lst[1][-1] == "Count":
                line[-1] = int(line[-1])
                table.sort(key=lambda x:x[-1], reverse=True)
    return lst 
    
def prejmenovani_hlavicky(hlavicka, zkratky_regionu):
    "in: tabulka, out: prvni radek s prejmenovanymi sloupci"
    print('-----------')
    print(zkratky_regionu)
    print(hlavicka)
    list_zkratek = [] 
    for item in hlavicka:
        for key in zkratky_regionu:
            if key in item:
                list_zkratek.append(zkratky_regionu[key]) 
                break
        else:   
            print(item," - nazev nenalezen v hashovaci tabulce")    
    return list_zkratek

#tab 5 and 6
def is_non_zero_line(line):
    "in: a line, boolean value"
    summ = sum([ float(item) for item in line[-11:-2] ])
    return summ > 0.0


#tab7
def is_non_zero_line_mutations(line):
    "in: a line, boolean value"
    summ = sum([ float(item) for item in line[1:] ])
    return summ > 0.0

#tab7
def sort_time_table(tbl):
    "in: slices of the table, only rows with mutations, out: table"
    tbl.sort(key=lambda x:int(x[-1]), reverse=True)
    return tbl

def open_hash_table(filename):
    hash_table = {}   
    with open(filename, newline = '') as f:
        csvreader = csv.reader(f)
        for row in csvreader:
            key = row[0]
            value = row[1]
            hash_table[key] = value
        return hash_table   

def color_class(line,item):
    "in: item of a sublist, out: str"
    max_item = max([int(i) for i in line[1:] if i != ''])
    if item != "":
        item = int(item)
        if item/max_item  > 0.8:
            color_class = "level_80"
        elif item/max_item  > 0.6:
            color_class = "level_60"
        elif item/max_item  > 0.4:
            color_class = "level_40"
        elif item/max_item  > 0.4:
            color_class = "level_40"
        elif item/max_item  > 0.2:
            color_class = "level_20"
        elif item/max_item  > 0.01:
            color_class = "level_01" 
        else:
            color_class = ""
    else:
       color_class = "" 
    return color_class


def main():
    #the templates to be used    
    seznam_kapitol = precti_seznam_kapitol("template/seznam_kapitol.csv")

    #nacteni hashovaci tabulky
    zkratky_regionu = open_hash_table("template/hash_table_regions.csv")

    #copy css
    shutil.copyfile("template/report.css", "output/report.css")

    #nacteni template
    template = env.get_template("template/template_main.html")

    #kopirovani obrazku z adresare input do output
    #vlozeni obrazku do html - konvertovani obrazku do data url formatu
    obrazky = []
    def obrazek(tmpl, src):
        "input: cesta, jmeno obrazku, outpt: zkopirovany obrazek do adresare output"
        tdir = os.path.split(tmpl)[0]
        obrazky.append(os.path.join(tdir, src))
        src_file = os.path.join(tdir, src)
        if os.path.getsize(src_file) > 1500000:
            target_file = os.path.join("output", src)
            shutil.copyfile(src_file, target_file)
            return src
        else:
            with open(src_file, "rb") as obr:
                encoded_obr = base64.b64encode(obr.read()).decode("utf-8")       
            if src.lower().endswith('.png'):
                prefix = "data:image/png;base64,"
            elif src.lower().endswith('.svg'):        
                prefix = "data:image/svg+xml;base64,"
            else:
                raise RuntimeError("neznama pripona obrazku")
            return prefix + encoded_obr

    #zalozeni vychoziho souboru - main.html
    with open("output/main.html","w") as f_result:
        content = template.render(
            NOW = NOW, 
            DF_DATE = DF_DATE,
            ACTUAL_SAMPLE_SIZE = ACTUAL_SAMPLE_SIZE,
            SAMPLES_REGIONS = SAMPLES_REGIONS,
            SAMPLES_FOR_ANALYSES = SAMPLES_FOR_ANALYSES,
            SAMPLES_WEEKS = SAMPLES_WEEKS,
            WEEK = WEEK,
            LINEAGE_COUNTS = LINEAGE_COUNTS,
            SEQUENCED_RATIO = SEQUENCED_RATIO,
            TYDNY_NAZPET = TYDNY_NAZPET,
            seznam_kapitol = seznam_kapitol, 
            enumerate = enumerate,  
            float = float, 
            int = int,
            sort_time_table = sort_time_table,
            len = len,
            input_table_tsv = input_table_tsv,
            is_non_zero_line = is_non_zero_line, 
            is_non_zero_line_mutations = is_non_zero_line_mutations,
            obrazek = obrazek,
            color_class = color_class,
            prejmenovani_hlavicky = prejmenovani_hlavicky,
            zkratky_regionu = zkratky_regionu
        )
        f_result.write(content)     
 
        
        
    #print(f"Obrazky: {' '.join(obrazky)}")
    HTML("output/main.html").write_pdf("output/report.pdf")

if __name__ == '__main__':
    main()