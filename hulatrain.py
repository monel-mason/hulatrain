from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS, cross_origin
from flask import send_file
from threading import Thread
from datetime import datetime
import json
import math
import os
import base64
import glob

import matplotlib.pyplot as plt
import numpy as np
import cv2

app = Flask(__name__)
app.config['CORS_HEADERS'] = 'Content-Type'
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

recording = False
fn = ''
camera = None


@app.route("/refreshThumbs")
@cross_origin()
def refreshThumbs():
    pager = request.args.get("slider")
    Thread(target=generateThumbs()).start()
    return "Thumbs Generated"


@app.route("/getMetas")
@cross_origin()
def getMetas():
    json_list = glob.glob('/home/mason/Pictures/hula/meta/*json')
    json_list = [os.path.basename(x) for x in json_list]
    json_list.sort()
    return jsonify(
        message="Metadata list",
        result=json_list[-10::]
    )


@app.route("/getThumbs")
@cross_origin()
def getThumbs():
    ret = []
    img_list = glob.glob('/home/mason/Pictures/hula/thumbnails/tt*jpg')
    img_list_thumbnails = [os.path.basename(x) for x in img_list]
    img_list_thumbnails.sort()
    img_list = glob.glob('/home/mason/Pictures/hula/aa*json')
    for x in img_list:
        f = open(x, "r")
        result = json.load(f)
        ret.extend(result)
    result.sort()
    return jsonify(
        message="Thumbnails list",
        result=img_list_thumbnails,
        bookmark=ret
    )


@app.route("/getMasks")
@cross_origin()
def getMasks():
    img_list = glob.glob('/home/mason/Pictures/hula/meta/*json')
    f = open(img_list[-1], "r")
    masks = json.load(f)
    masks = [x for x in masks if x.get('category', 'NA') == "fungo"]
    for i in masks:
        print("processing: %s" % (i))
        img = cv2.imread("/home/mason/Pictures/hula/" + i.get("img"))
        for ij, j in enumerate(i.get("rects")):
            crop = img[j.get("rect0").get("y") * 3:j.get("rect1").get("y") * 3,
                   j.get("rect0").get("x") * 3:j.get("rect1").get("x") * 3]
            filename = i.get("img")[0] + "m" + i.get("img")[2:-4] + "-" + str(ij) + "rect.jpg"
            cv2.imwrite("/home/mason/Pictures/hula/masks/" + filename, crop)

    mask_list = glob.glob('/home/mason/Pictures/hula/masks/*jpg')

    return jsonify(
        message="Masks generated",
        result=mask_list
    )


@app.route("/getMeta")
@cross_origin()
def getMeta():
    meta = request.args.get('meta')
    f = open("/home/mason/Pictures/hula/meta/" + meta, "r")
    return jsonify(
        message="Metadata listcommunity/python-matplotlib",
        result=json.load(f)
    )


@app.route("/saveMeta", methods=['POST'])
@cross_origin()
def saveMeta():
    f = open("/home/mason/Pictures/hula/meta/mm_" + datetime.now().strftime('%Y%m%d-%H%M%S:%f') + '.json', "w")
    json.dump(request.json, f)
    return jsonify(
        message="Metadata Saved"
    )


@app.route('/thumbnails/<filename>')
@cross_origin()
def send_thumbnail(filename):
    return send_from_directory('/home/mason/Pictures/hula/thumbnails', filename)


@app.route('/images/<filename>')
@cross_origin()
def send_image(filename):
    return send_from_directory('/home/mason/Pictures/hula', filename)


def generateThumbs():
    img_list = glob.glob('/home/mason/Pictures/hula/thumbnails/tt*jpg')
    img_list_thumbnails = [os.path.basename(x) for x in img_list]
    img_list_thumbnails.sort()
    img_list = glob.glob('/home/mason/Pictures/hula/thumbnails/tm*-0canny.jpg')
    img_list_canny = [os.path.basename(x) for x in img_list]
    img_list_canny.sort()
    img_list = glob.glob('/home/mason/Pictures/hula/tt*jpg')
    img_list = [os.path.basename(x) for x in img_list]
    img_list.sort()
    for x in img_list:
        c0 = x[0] + "m" + x[2:-4] + "-0canny.jpg"
        if x not in img_list_thumbnails:
            f = cv2.imread('/home/mason/Pictures/hula/' + x)
            rows, cols, channels = f.shape
            f = cv2.resize(f, (cols // 6, rows // 6))
            cv2.imwrite('/home/mason/Pictures/hula/thumbnails/' + x, f)
        if c0 not in img_list_canny:
            f = cv2.imread('/home/mason/Pictures/hula/' + x)
            rows, cols, channels = f.shape
            f = cv2.resize(f, (cols // 6, rows // 6))
            f = cv2.Canny(f, 55, 230)
            cv2.imwrite('/home/mason/Pictures/hula/thumbnails/' + c0, f)
    generateIndex()


def generateIndex():
    index = []
    img_list = glob.glob('/home/mason/Pictures/hula/thumbnails/tt*jpg')
    img_list_thumbnails = [os.path.basename(x) for x in img_list]
    img_list_thumbnails.sort()
    for x in range(0, 36):
        print(x * len(img_list_thumbnails) // 36)
        print(img_list_thumbnails[x * len(img_list_thumbnails) // 36])
        f = cv2.imread('/home/mason/Pictures/hula/' + img_list_thumbnails[x * len(img_list_thumbnails) // 36])
        f = cv2.resize(f, (96 // 2, 54))
        index.append(f)
    f = cv2.hconcat(index)
    cv2.imwrite('/home/mason/Pictures/hula/thumbnails/index.jpg', f)


@app.before_first_request
def _run_on_start():
    global camera

    print("bef fisrt req")


if __name__ == "__main__":
    # Thread(target = recordTask, args=[10]).start()
    app.run(host='0.0.0.0', debug=True)
