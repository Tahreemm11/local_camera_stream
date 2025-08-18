# stream/utils.py
import numpy as np
from deepface import DeepFace
from .models import Person, ExpressionRecord
from numpy.linalg import norm
from django.db import transaction

EMBED_MODEL = "Facenet"  

def get_embedding(face_img_rgb):
    """
    face_img_rgb: numpy array in RGB (H, W, 3)
    returns embedding list or None
    """
    try:
        emb = DeepFace.represent(face_img_rgb, model_name=EMBED_MODEL, enforce_detection=False)
        # DeepFace.represent may return a list or vector depending on version
        if isinstance(emb, list) and emb:
            first = emb[0]
            if isinstance(first, dict) and "embedding" in first:
                return first["embedding"]
            # maybe it's list of floats already
            if isinstance(first, (list, np.ndarray)):
                return list(first)
        # if emb is array-like
        if isinstance(emb, (list, np.ndarray)):
            return list(emb)
    except Exception as e:
        print("get_embedding error:", e)
    return None

def cosine_distance(a, b):
    a = np.array(a); b = np.array(b)
    if norm(a) == 0 or norm(b) == 0:
        return 1.0
    return 1 - np.dot(a, b) / (norm(a) * norm(b))

def find_matching_person(embedding, threshold=0.45):
    if not embedding:
        return None
    persons = Person.objects.exclude(embedding__isnull=True)
    best = None
    best_dist = 1.0
    for p in persons:
        try:
            dist = cosine_distance(embedding, p.embedding)
            if dist < best_dist:
                best_dist = dist
                best = p
        except Exception:
            continue
    if best and best_dist <= threshold:
        return best
    return None

@transaction.atomic
def update_expression_for_face(face_img_rgb):
    """
    face_img_rgb: face crop in RGB colorspace
    returns (person, expression)
    """
    # 1. compute embedding
    embedding = get_embedding(face_img_rgb)

    # 2. find existing person by embedding
    person = None
    if embedding:
        person = find_matching_person(embedding)

    # 3. create new person if none
    if not person:
        person = Person.objects.create(embedding=embedding)

    # 4. update total detections
    person.total_detections = (person.total_detections or 0) + 1
    if embedding and not person.embedding:
        # store embedding if not stored
        person.embedding = embedding
    person.save()

    # 5. predict emotion
    try:
        res = DeepFace.analyze(face_img_rgb, actions=['emotion'], enforce_detection=False)
        if isinstance(res, list):
            res = res[0]
        expression = res.get('dominant_emotion') or "unknown"
    except Exception as e:
        print("DeepFace.analyze error:", e)
        expression = "unknown"

    # 6. update expression count
    expr_obj, _ = ExpressionRecord.objects.get_or_create(person=person, expression=expression)
    expr_obj.count += 1
    expr_obj.save()

    return person, expression
