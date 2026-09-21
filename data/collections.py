# Коллекция газов (модель-коллекция, без БД)
# image_key, video_key — ключи в Minio (наименование на латинице)
# image_url, video_url — полные URL из Minio (http://localhost:9000/media/<key>)
# Для демонстрации в песочнице image_url переключён на локальные статические файлы

MINIO_BASE = "http://localhost:9000/media"

gases_db = [
    {
        "id": 1,
        "name": "Азот",
        "molar_mass": 28.014,
        "density": 1.2506,
        "description": (
            "Азот — бесцветный инертный газ без запаха, составляющий около 78% "
            "атмосферы Земли. Широко применяется в промышленности: при производстве "
            "аммиака, в качестве защитной среды при сварке и металлообработке, "
            "а также в медицине для криоконсервации."
        ),
        "status": "published",
        "likes": [1, 3, 5, 7],
        "image_key": "nitrogen.jpg",
        "video_key": "nitrogen.mp4",
        "image_url": f"{MINIO_BASE}/nitrogen.jpg",
        "video_url": f"{MINIO_BASE}/nitrogen.mp4",
    },
    {
        "id": 2,
        "name": "Кислород",
        "molar_mass": 31.998,
        "density": 1.4290,
        "description": (
            "Кислород — активный газ, необходимый для дыхания всех аэробных "
            "организмов и поддержания горения. Второй по распространённости "
            "компонент атмосферы Земли (около 21%). Применяется в металлургии, "
            "медицине и ракетных двигателях."
        ),
        "status": "published",
        "likes": [2, 4, 6, 8, 10],
        "image_key": "oxygen.jpg",
        "video_key": "oxygen.mp4",
        "image_url": f"{MINIO_BASE}/oxygen.jpg",
        "video_url": f"{MINIO_BASE}/oxygen.mp4",
    },
    {
        "id": 3,
        "name": "Гелий",
        "molar_mass": 4.003,
        "density": 0.1785,
        "description": (
            "Гелий — лёгкий инертный одноатомный газ, второй по лёгкости элемент "
            "после водорода. Используется в аэростатах, криогенике, медицинских "
            "томографах (МРТ) и как охладитель сверхпроводящих магнитов."
        ),
        "status": "published",
        "likes": [1, 2, 9],
        "image_key": "helium.jpg",
        "video_key": "helium.mp4",
        "image_url": f"{MINIO_BASE}/helium.jpg",
        "video_url": f"{MINIO_BASE}/helium.mp4",
    },
    {
        "id": 4,
        "name": "Аргон",
        "molar_mass": 39.948,
        "density": 1.7837,
        "description": (
            "Аргон — инертный одноатомный газ, третий по распространённости в "
            "атмосфере (около 0,93%). Применяется в сварке и резке металлов как "
            "защитная среда, в производстве электрических ламп накаливания и "
            "в лазерных технологиях."
        ),
        "status": "published",
        "likes": [3, 5, 7, 9],
        "image_key": "argon.jpg",
        "video_key": "argon.mp4",
        "image_url": f"{MINIO_BASE}/argon.jpg",
        "video_url": f"{MINIO_BASE}/argon.mp4",
    },
    {
        "id": 5,
        "name": "Углекислый газ",
        "molar_mass": 44.010,
        "density": 1.9640,
        "description": (
            "Диоксид углерода (CO₂) — бесцветный газ без запаха. Продукт горения "
            "органического топлива и клеточного дыхания. Используется в "
            "пожаротушении, газировании напитков и как промышленный хладагент."
        ),
        "status": "published",
        "likes": [1, 4, 6],
        "image_key": "co2.jpg",
        "video_key": "co2.mp4",
        "image_url": f"{MINIO_BASE}/co2.jpg",
        "video_url": f"{MINIO_BASE}/co2.mp4",
    },
    {
        "id": 6,
        "name": "Неон",
        "molar_mass": 20.180,
        "density": 0.9002,
        "description": (
            "Неон — инертный одноатомный газ, светящийся характерным оранжево-красным "
            "светом при прохождении электрического тока. Применяется в рекламных "
            "неоновых трубках, лазерах и плазменных панелях."
        ),
        "status": "deleted",
        "likes": [],
        "image_key": "neon.jpg",
        "video_key": "neon.mp4",
        "image_url": f"{MINIO_BASE}/neon.jpg",
        "video_url": f"{MINIO_BASE}/neon.mp4",
    },
    {
        "id": 7,
        "name": "Водород",
        "molar_mass": 2.016,
        "density": 0.0899,
        "description": (
            "Водород — самый лёгкий и самый распространённый элемент во Вселенной. "
            "Перспективный энергоноситель будущего, применяется в топливных "
            "элементах, ракетном топливе и химической промышленности."
        ),
        "status": "draft",
        "likes": [],
        "image_key": "hydrogen.jpg",
        "video_key": "hydrogen.mp4",
        "image_url": f"{MINIO_BASE}/hydrogen.jpg",
        "video_url": f"{MINIO_BASE}/hydrogen.mp4",
    },
]
