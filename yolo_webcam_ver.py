'''
MIT License

Copyright (c) 2018 Arun Ponnusamy

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
'''

import time
import cv2
import argparse
import numpy as np

ap = argparse.ArgumentParser()
ap.add_argument('-c', '--config', required=True,
                help = 'path to yolo config file')
ap.add_argument('-w', '--weights', required=True,
                help = 'path to yolo pre-trained weights')
ap.add_argument('-cl', '--classes', required=True,
                help = 'path to text file containing class names')
args = ap.parse_args()


def get_output_layers(net):
    
    layer_names = net.getLayerNames()
    
    output_layers = [layer_names[i[0] - 1] for i in net.getUnconnectedOutLayers()]

    return output_layers


def draw_prediction(img, class_id, confidence, x, y, x_plus_w, y_plus_h):

    label = str(classes[class_id])

    color = COLORS[class_id]

    cv2.rectangle(img, (x,y), (x_plus_w,y_plus_h), color, 2)

    cv2.putText(img, label, (x-10,y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

classes = None
with open(args.classes, 'r') as f:
	classes = [line.strip() for line in f.readlines()]

net = cv2.dnn.readNet(args.weights, args.config)	

start = time.time()
#vid = cv2.VideoCapture('ip/stream.mjpg')
vid = cv2.VideoCapture(0)

while(vid.isOpened()):
	ret, image = vid.read()
	Width = image.shape[1]
	Height = image.shape[0]
	scale = 0.00392


	COLORS = np.random.uniform(0, 255, size=(len(classes), 3))


	blob = cv2.dnn.blobFromImage(image, scale, (416,416), (0,0,0), True, crop=False)

	net.setInput(blob)

	outs = net.forward(get_output_layers(net))

	class_ids = []
	confidences = []
	boxes = []
	conf_threshold = 0.5
	nms_threshold = 0.4


	for out in outs:
		for detection in out:
			scores = detection[5:]
			class_id = np.argmax(scores)
			confidence = scores[class_id]
			if confidence > 0.5:
				center_x = int(detection[0] * Width)
				center_y = int(detection[1] * Height)
				w = int(detection[2] * Width)
				h = int(detection[3] * Height)
				x = center_x - w / 2
				y = center_y - h / 2
				class_ids.append(class_id)
				confidences.append(float(confidence))
				boxes.append([x, y, w, h])


	indices = cv2.dnn.NMSBoxes(boxes, confidences, conf_threshold, nms_threshold)

	for i in indices:
		i = i[0]
		box = boxes[i]
		x = box[0]
		y = box[1]
		w = box[2]
		h = box[3]
		if class_ids[i] == 0:
			draw_prediction(image, class_ids[i], confidences[i], round(x), round(y), round(x+w), round(y+h))
	
	total_people = 0	
	for i in indices:	
		i = i[0]
		#print(class_ids[i])
		if class_ids[i] == 0:
			total_people = total_people + 1
	print("total_people:" + str(total_people))	
	
	
	end = time.time()
	elapsed = end - start
	msg = 'Time taken: %.2f seconds' % elapsed
	print(msg)	
	start = end	
	cv2.imshow("object detection", image)
	#k = cv2.waitKey()
	if cv2.waitKey(1) == 13:
		break
cv2.destroyAllWindows()
