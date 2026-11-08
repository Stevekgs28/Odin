import cv2
import mediapipe as mp
import subprocess
import time
import webbrowser
import urllib.request
import os
import platform

# ==========================================
# CONFIGURATION
# ==========================================

CAMERA_ID = 0

# Nombre de secondes pendant lesquelles
# un geste doit rester stable
TEMPS_VALIDATION = 0.8

# Temps minimum entre deux actions
TEMPS_ENTRE_ACTIONS = 1.5

# Chemin du modèle MediaPipe
MODEL_PATH = "hand_landmarker.task"

MODEL_URL = (
    "https://storage.googleapis.com/"
    "mediapipe-models/hand_landmarker/"
    "hand_landmarker/float16/1/"
    "hand_landmarker.task"
)

# ==========================================
# TELECHARGEMENT DU MODELE
# ==========================================

if not os.path.exists(MODEL_PATH):
    print("Telechargement du modele MediaPipe...")
    urllib.request.urlretrieve(MODEL_URL, MODEL_PATH)
    print("Modele telecharge !")

# ==========================================
# INITIALISATION MEDIAPIPE
# ==========================================

BaseOptions = mp.tasks.BaseOptions
HandLandmarker = mp.tasks.vision.HandLandmarker
HandLandmarkerOptions = mp.tasks.vision.HandLandmarkerOptions
VisionRunningMode = mp.tasks.vision.RunningMode

options = HandLandmarkerOptions(
    base_options=BaseOptions(
        model_asset_path=MODEL_PATH
    ),
    running_mode=VisionRunningMode.VIDEO,
    num_hands=1,
    min_hand_detection_confidence=0.6,
    min_hand_presence_confidence=0.6,
    min_tracking_confidence=0.6
)

# ==========================================
# FONCTIONS
# ==========================================

def doigts_leves(landmarks):
    """
    Retourne l'etat des 5 doigts :
    [pouce, index, majeur, annulaire, auriculaire]

    1 = leve
    0 = baisse
    """

    doigts = []

    # Pouce : comparaison des distances
    # entre son extremite et la base de l'index
    pouce_tip = landmarks[4]
    pouce_ip = landmarks[3]
    index_base = landmarks[5]

    distance_tip = (
        (pouce_tip.x - index_base.x) ** 2
        + (pouce_tip.y - index_base.y) ** 2
    )

    distance_ip = (
        (pouce_ip.x - index_base.x) ** 2
        + (pouce_ip.y - index_base.y) ** 2
    )

    doigts.append(
        1 if distance_tip > distance_ip * 1.3 else 0
    )

    # Autres doigts
    # Comparaison de la pointe avec
    # l'articulation centrale
    for tip, pip in [
        (8, 6),
        (12, 10),
        (16, 14),
        (20, 18)
    ]:
        doigts.append(
            1 if landmarks[tip].y < landmarks[pip].y else 0
        )

    return doigts


def reconnaitre_geste(doigts):
    """
    Identifie le geste selon les doigts leves.
    """
    
    if doigts == [0,0,0,0,0]:
        return "ZERO"
        pass
    
    elif doigts == [0,1,0,0,0]:
        return "UN"
    
    elif doigts == [0,1,1,0,0]:
        return "DEUX"
    
    elif doigts == [1,1,1,0,0]:
        return "TROIS"
    
    elif doigts == [0,1,1,1,1]:
        return "QUATRE"
    
    elif doigts == [1,1,1,1,1]:
        return "CINQ"

    return "INCONNU"


def executer_action(geste):
    print("Geste detecte : ", geste)


    if geste == "ZERO" :
        print("Zéro")
        return "Volume augmente"

    elif geste == "UN" :
        webbrowser.open("https://youtu.be/_zSEMC9tbcw?t=62")
        return "Volume diminue"

    elif geste == "DEUX" :
        print("Deux")
        webbrowser.open("https://chatgpt.com")
        return "Lecture / Pause"

    elif geste == "TROIS" :
        print("Trois")
        webbrowser.open("https://open.spotify.com")
        return "Spotify ouvert"

    elif geste == "QUATRE" :
        print("Quatre")
        webbrowser.open("https://youtube.com")
        return "YouTube ouvert"

    elif geste == "CINQ" :
        print("Cinq")
        webbrowser.open("https://youtube.com")
        return "Cinq"

    return "Aucune action"


def dessiner_main(image, landmarks):
    """
    Dessine les 21 points et les connexions.
    """

    h, w, _ = image.shape

    points = []

    for landmark in landmarks:
        x = int(landmark.x * w)
        y = int(landmark.y * h)
        points.append((x, y))

        cv2.circle(
            image,
            (x, y),
            5,
            (0, 255, 0),
            -1
        )

    connexions = [
        (0, 1), (1, 2), (2, 3), (3, 4),
        (0, 5), (5, 6), (6, 7), (7, 8),
        (5, 9), (9, 10), (10, 11), (11, 12),
        (9, 13), (13, 14), (14, 15), (15, 16),
        (13, 17), (17, 18), (18, 19), (19, 20),
        (0, 17)
    ]

    for debut, fin in connexions:
        cv2.line(
            image,
            points[debut],
            points[fin],
            (255, 255, 255),
            2
        )


# ==========================================
# PROGRAMME PRINCIPAL
# ==========================================

def main():

    camera = cv2.VideoCapture(CAMERA_ID)

    if not camera.isOpened():
        print("ERREUR : Webcam introuvable.")
        return

    camera.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

    mode_actif = True

    dernier_geste = None
    debut_geste = time.monotonic()
    derniere_action = 0
    geste_deja_execute = False

    message_action = "Systeme pret"

    print("================================")
    print(" CONTROLE GESTUEL ACTIVE")
    print("================================")
    print("Appuie sur Q pour quitter")
    print("Appuie sur M pour activer/desactiver")
    print("================================")

    with HandLandmarker.create_from_options(options) as landmarker:

        dernier_timestamp = -1

        while True:

            success, image = camera.read()

            if not success:
                print("Erreur de lecture webcam.")
                break

            image = cv2.flip(image, 1)

            rgb = cv2.cvtColor(
                image,
                cv2.COLOR_BGR2RGB
            )

            mp_image = mp.Image(
                image_format=mp.ImageFormat.SRGB,
                data=rgb
            )

            # Timestamp croissant requis par VIDEO
            timestamp = int(time.monotonic() * 1000)
            timestamp = max(
                timestamp,
                dernier_timestamp + 1
            )
            dernier_timestamp = timestamp

            result = landmarker.detect_for_video(
                mp_image,
                timestamp
            )

            geste = "AUCUN"

            if result.hand_landmarks:

                landmarks = result.hand_landmarks[0]

                dessiner_main(image, landmarks)

                doigts = doigts_leves(landmarks)

                geste = reconnaitre_geste(doigts)

            maintenant = time.monotonic()

            # ==================================
            # STABILISATION DES GESTES
            # ==================================

            if geste != dernier_geste:

                dernier_geste = geste
                debut_geste = maintenant
                geste_deja_execute = False

            duree_geste = maintenant - debut_geste

            if (
                geste not in ["AUCUN", "INCONNU"]
                and not geste_deja_execute
                and duree_geste >= TEMPS_VALIDATION
                and maintenant - derniere_action
                    >= TEMPS_ENTRE_ACTIONS
            ):

                if geste == "POUCE":

                    mode_actif = not mode_actif

                    if mode_actif:
                        message_action = "Mode ACTIVE"
                    else:
                        message_action = "Mode DESACTIVE"

                elif mode_actif:

                    try:
                        message_action = executer_action(
                            geste
                        )
                    except Exception as erreur:
                        message_action = (
                            f"Erreur : {erreur}"
                        )
                        print(message_action)

                else:
                    message_action = "Mode desactive"

                derniere_action = maintenant
                geste_deja_execute = True

            # ==================================
            # AFFICHAGE
            # ==================================

            couleur_mode = (
                (0, 255, 0)
                if mode_actif
                else (0, 0, 255)
            )

            texte_mode = (
                "ACTIF"
                if mode_actif
                else "DESACTIVE"
            )

            cv2.rectangle(
                image,
                (0, 0),
                (image.shape[1], 150),
                (30, 30, 30),
                -1
            )

            cv2.putText(
                image,
                f"MODE : {texte_mode}",
                (20, 35),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                couleur_mode,
                2
            )

            cv2.putText(
                image,
                f"GESTE : {geste}",
                (20, 75),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (255, 255, 255),
                2
            )

            cv2.putText(
                image,
                f"ACTION : {message_action}",
                (20, 115),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 255, 255),
                2
            )

            # Barre de progression du geste
            if geste not in ["AUCUN", "INCONNU"]:

                progression = min(
                    duree_geste / TEMPS_VALIDATION,
                    1.0
                )

                largeur = int(
                    progression * image.shape[1]
                )

                cv2.rectangle(
                    image,
                    (0, image.shape[0] - 15),
                    (largeur, image.shape[0]),
                    (0, 255, 0),
                    -1
                )

            cv2.imshow(
                "Controle Gestuel - Chambre",
                image
            )

            touche = cv2.waitKey(1) & 0xFF

            if touche == ord("q"):
                break

            elif touche == ord("m"):
                mode_actif = not mode_actif

                message_action = (
                    "Mode ACTIVE"
                    if mode_actif
                    else "Mode DESACTIVE"
                )

    camera.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()