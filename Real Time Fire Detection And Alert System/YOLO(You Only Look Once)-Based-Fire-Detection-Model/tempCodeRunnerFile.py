            frame_diff = np.zeros_like(gray)

        results = model.predict(frame, conf=0.5, vid_stride=1, show_labels=True, show_conf=False)
        fire_boxes = []

        for box, c in zip(results[0].boxes.xyxy, results[0].boxes.cls):
            if model.names[int(c)] == 'fire':
                coords = box.cpu().numpy().astype(int)
                x1, y1, x2, y2 = coords
                area = (x2 - x1) * (y2 - y1)
                if area >= MIN_FIRE_BOX_AREA:
                    fire_boxes.append(coords)

        faces = face_cascade.detectMultiScale(gray, 1.1, 4)
        filtered_fire_boxes = []
        for box in fire_boxes:
            x1, y1, x2, y2 = box
            is_face_overlap = False
            for (fx, fy, fw, fh) in faces:
                if fx < x1 < fx+fw and fy < y1 < fy+fh:
                    is_face_overlap = True
                    break
            if not is_face_overlap:
                filtered_fire_boxes.append(box)

        flicker_detected = False
        for box in filtered_fire_boxes:
            x1, y1, x2, y2 = box
            fire_region = gray[y1:y2, x1:x2]
            if fire_region.size > 0:
                brightness = np.mean(fire_region)
                brightness_history.append(brightness)
                if len(brightness_history) > BRIGHTNESS_HISTORY_LEN: