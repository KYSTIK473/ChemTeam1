from threading import Thread, Semaphore
import cv2
import os
import numpy as np
import math
import time


sas = ["A1"] * 4
obj = 4 
long = 20

sem = Semaphore(5)

video_capture = cv2.VideoCapture(0)

frame_width = int(video_capture.get(3))

frame_height = int(video_capture.get(4))

ret, frame = video_capture.read()
current_dir = os.path.dirname(os.path.abspath(__file__))
folder = "data"
file = "dat.txt"

line_view =   True
object_view = True
stat = True
arr = []
points = []
ras = 4 
stat = False 
global nubb
nubb = 0

global sum_distance
global sum_vector
sum_vector = (0, 0)
sum_distance = 0

def set_obj(coll):
   global obj 
   obj = coll

def set_line(x,y):
   global vert_l
   global gorizont_l
   vert_l = x
   gorizont_l = y

def draw_line(image, start_point, end_point, color=(0, 0, 255), thickness=4):
    start_point = (int(start_point[0]), int(start_point[1]))
    end_point = (int(end_point[0]), int(end_point[1]))
    cv2.line(image, start_point, end_point, color, thickness)
    return 

def get_pixel_coordinates(cell_label, frame_width, frame_height, vert_l, gorizont_l):
    # Получаем числовую часть и буквенную часть координаты ячейки
    num = int(''.join(filter(str.isdigit, cell_label))) - 1
    letter = ord(''.join(filter(str.isalpha, cell_label))) - ord('A')
    
    # Вычисляем пиксельные координаты x и y для верхнего левого угла
    x1 = letter * frame_width // vert_l
    y1 = num * frame_height // gorizont_l

    # Добавляем половину ширины и высоты ячейки, чтобы получить центр
    x_center = x1 + frame_width // (2 * vert_l)
    y_center = y1 + frame_height // (2 * gorizont_l)

    return x_center, y_center

def add_to_array(data, array):
    array.append(data)

def sitt(frame):
    rois = []
    with open(os.path.join(current_dir, folder, file), 'r') as f:
        content = f.read().strip()
        for item in content.split('\n'):
            # Удаление скобок и других нежелательных символов
            item = item.replace('(', '').replace(')', '')
            values = list(map(int, item.split(',')))
            rois.append(tuple(values))
    rois_and_histograms = []
    for roi in rois:
        x, y, w, h = roi
        roi_frame = frame[y:y+h, x:x+w]
        hsv_roi = cv2.cvtColor(roi_frame, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv_roi, np.array((0., 60., 32.)), np.array((180., 255., 255.)))
        roi_hist = cv2.calcHist([hsv_roi], [0], mask, [180], [0, 180])
        cv2.normalize(roi_hist, roi_hist, 0, 255, cv2.NORM_MINMAX)
        rois_and_histograms.append((roi_hist, roi))

    # Определение параметров алгоритма Mean Shift
    term_criteria = (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 1)
    return rois_and_histograms, term_criteria

def get_cell_coordinates(image, x, y):
  
  # Создаем список словарей для ячеек
  cells = []
  for i in range(vert_l):
    for j in range(gorizont_l):
      x1 = (i) * frame_width // (vert_l)
      x2 = (i + 1) * frame_width // (vert_l)
      y1 = (j) * frame_height // (gorizont_l)
      y2 = (j + 1) * frame_height // (gorizont_l)
      cells.append({
        "x1": x1,
        "y1": y1,
        "x2": x2,
        "y2": y2,
      })

  # Проверка, в какой ячейке находится точка:
  for cell in cells:
    if cell["x1"] <= x <= cell["x2"] and cell["y1"] <= y <= cell["y2"]:
      # Возвращаем координаты ячейки в виде "2A"
      return f"{cell['y1'] // (frame_height // gorizont_l) + 1}{chr(ord('A') + cell['x1'] // (frame_width // vert_l))}"

  # Если точка не находится ни в одной ячейке
  return None

def matt(st):
    if 'arr' not in matt.__dict__:
        matt.arr = []
    matt.arr.append(st)
    if len(matt.arr) == 4:
       #print((' '.join(matt.arr))+' ')  # Вывод с пробелами после каждого элемента
        matt.arr = []  # Очистка массива для следующей строки

def draw_coord(frame,com,ccod):
    pixel_coordinates1 = get_pixel_coordinates(ccod, frame_width, frame_height, vert_l, gorizont_l)
    draw_line(frame,com,pixel_coordinates1)

def found(q): 
    global stat
    global combo
    global coll  
    coll = 0
    ret, frame = video_capture.read()
    rois_and_histograms, term_criteria = sitt(frame)  
    while True:
            if coll < obj:
                ret, frame = video_capture.read()
                if not ret:
                    break
                for index, (roi_hist, roi) in enumerate(rois_and_histograms):
                    x, y, w, h = roi
                    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
                    dst = cv2.calcBackProject([hsv], [0], roi_hist, [0, 180], 1)
                    _, new_roi = cv2.meanShift(dst, roi, term_criteria)
                    rois_and_histograms[index] = (roi_hist, new_roi)
                    x, y, w, h = new_roi
                    draw_lines_with_labels(frame,vert_l,gorizont_l)
                    
                    cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
                    x_center = x + w / 2
                    y_center = y + h / 2
                    
                    combo = x_center,y_center
                    coord = get_cell_coordinates(frame,x_center,y_center)
                    draw_coord(frame,combo,sas[coll])
                    matt(coord)
                    Thread(target=ezd, args=(combo, coll)).start()
                    coll = coll + 1
                    stat = True
                    cv2.imshow("frame",frame)
                q.put(frame)    
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    video_capture.release()
                    cv2.destroyAllWindows()
            else:
               coll = 0 

def draw_lines_with_labels(image, num_vertical_lines, num_horizontal_lines):
  bright = 100
  # Рисуем вертикальные линии
  vertical_spacing = frame_width // (num_vertical_lines + 1)
  for i in range(num_vertical_lines):
    x = (i + 1) * vertical_spacing
    cv2.line(image, (x, 0), (x, frame_height), (0, 0, bright), 2)

  # Рисуем горизонтальные линии
  horizontal_spacing = frame_height // (num_horizontal_lines + 1)
  for i in range(num_horizontal_lines):
    y = (i + 1) * horizontal_spacing
    cv2.line(image, (0, y), (frame_width, y), (0, 0, bright), 2)

  # Добавляем цифры и буквы
  font = cv2.FONT_HERSHEY_SIMPLEX
  font_scale = 0.5
  thickness = 2
  color_y = (255, 0, 0) 
  # Цифры для горизонтальных линий
  for i in range(num_horizontal_lines):
    y = (i + 1) * horizontal_spacing
    text = str(i + 1)
    text_size, _ = cv2.getTextSize(text, font, font_scale, thickness)
    text_x = 0  # Координата x для текста
    text_y = (y + text_size[1] // 2) -10  # Координата y для текста
    cv2.putText(image, text, (text_x, text_y), font, font_scale, color_y, thickness)

  # Буквы для вертикальных линий
  letters = [chr(i) for i in range(ord('A'), ord('Z') + 1)]
  letter_index = 0
  for i in range(num_vertical_lines):
    x = (i + 1) * vertical_spacing
    text = letters[letter_index]
    letter_index += 1
    if letter_index == len(letters):  # Переход к комбинированным буквам
      letter_index = 0
      text = f"{letters[0]}{letters[letter_index]}"
      letter_index += 1

    text_size, _ = cv2.getTextSize(text, font, font_scale, thickness)
    text_x = (x - text_size[0] // 2)  # Координата x для текста
    text_y = (frame_height//2)-220 # Координата y для текста
    cv2.putText(image, text, (text_x, text_y), font, font_scale, color_y, thickness)

  return image

def set_pos(combo, obj_count):
    if obj_count <= obj:
        for i in range(obj_count):
            sas[i] = combo[i] 
    return sas

def calculate_vector_and_distance(x1, y1, x2, y2):
    # Вычисляем вектор
    vector = (x2 - x1, y2 - y1)
    # Вычисляем расстояние
    distance = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
    ds = distance // long
    return vector,ds

def ezd(nA,it):
  global sum_distance
  with sem:
    if nubb > 99:
      x1,y1 = nA
      ixel_coordinates1 = get_pixel_coordinates(sas[it],frame_width, frame_height, vert_l, gorizont_l)
      x2,y2 = ixel_coordinates1
      points.appened(calculate_vector_and_distance(x1, y1, x2, y2))
    else:
       for (x1, y1, x2, y2) in points:
        vector, distance = calculate_vector_and_distance(x1, y1, x2, y2)
        sum_vector = (sum_vector[0] + vector[0], sum_vector[1] + vector[1])
        sum_distance += distance

        # Вычисляем средние значения
        average_vector = (sum_vector[0] / 100, sum_vector[1] / 100)
        average_distance = sum_distance / 100
          
