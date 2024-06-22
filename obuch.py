import cv2
import os
import numpy as np

def obuch(stat,obj):  
        if stat == True:
            # Захват видеопотока с камеры
            video_capture = cv2.VideoCapture(0)

            # Чтение первого кадра
            ret, frame = video_capture.read()

            current_dir = os.path.dirname(os.path.abspath(__file__))
            folder = "data"
            file = "dat.txt"

            if not os.path.exists(os.path.join(current_dir, folder)):
                os.makedirs(os.path.join(current_dir, folder))

            if not os.path.exists(os.path.join(current_dir, folder, file)):
                with open(os.path.join(current_dir, folder, file), 'w') as f:
                    f.write('')

            # Выбор ROI с помощью selectROI
            rois = []
            for i in range(obj):  # Позволяет выбрать 4 ROI
                roi = cv2.selectROI('Выбор ROI', frame)
                rois.append(roi)
                cv2.destroyAllWindows()

            with open(os.path.join(current_dir, folder, file), 'w') as f:
                for i in range(4):
                    # Добавляем данные в файл
                    f.write(str(rois[i]) + '\n')
        else:
            print("Obuch_None")
