from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, List, Optional

app = FastAPI(title="Beryl_MVP API", version="0.1.0")


# ---------- Modèles ----------

class RegisterRequest(BaseModel):
    email: str
    password: str


class LoginRequest(BaseModel):
    email: str
    password: str


class WalletOperation(BaseModel):
    amount: float
    description: Optional[str] = None


class WalletResponse(BaseModel):
    user_id: int
    balance: float


class Transaction(BaseModel):
    type: str              # "deposit" ou "withdraw"
    amount: float
    description: Optional[str] = None
    balance_after: float


# ---------- Stockage en mémoire (MVP) ----------

users: Dict[int, Dict[str, str]] = {}          # user_id -> {"email", "password"}
wallets: Dict[int, float] = {}                 # user_id -> balance
history: Dict[int, List[Transaction]] = {}     # user_id -> [Transaction]
next_user_id: int = 1


# ---------- Endpoints simples ----------

@app.get("/")
def read_root():
    return {"message": "API Beryl_MVP opérationnelle"}


@app.get("/addition")
def addition(a: int, b: int):
    return {"result": a + b}


@app.get("/moyenne")
def moyenne(a: float, b: float, c: float):
    return {"result": (a + b + c) / 3}


# ---------- Authentification basique ----------

@app.post("/users/register")
def register_user(data: RegisterRequest):
    global next_user_id

    # Vérifie si email déjà utilisé
    for uid, u in users.items():
        if u["email"] == data.email:
            raise HTTPException(status_code=400, detail="Email déjà enregistré")

    user_id = next_user_id
    next_user_id += 1

    users[user_id] = {"email": data.email, "password": data.password}
    wallets[user_id] = 0.0
    history[user_id] = []

    return {"status": "success", "user_id": user_id}


@app.post("/users/login")
def login_user(data: LoginRequest):
    for user_id, u in users.items():
        if u["email"] == data.email and u["password"] == data.password:
            return {
                "status": "success",
                "user_id": user_id,
                "token": "fake-jwt-token"
            }
    raise HTTPException(status_code=401, detail="Identifiants invalides")


# ---------- Wallet ----------

@app.get("/wallet/{user_id}", response_model=WalletResponse)
def get_wallet(user_id: int):
    if user_id not in wallets:
        raise HTTPException(status_code=404, detail="Utilisateur introuvable")
    return WalletResponse(user_id=user_id, balance=wallets[user_id])


@app.post("/wallet/{user_id}/deposit", response_model=WalletResponse)
def wallet_deposit(user_id: int, op: WalletOperation):
    if user_id not in wallets:
        raise HTTPException(status_code=404, detail="Utilisateur introuvable")
    if op.amount <= 0:
        raise HTTPException(status_code=400, detail="Montant invalide")

    wallets[user_id] += op.amount

    tx = Transaction(
        type="deposit",
        amount=op.amount,
        description=op.description or "Dépôt BerylPay",
        balance_after=wallets[user_id],
    )
    history[user_id].append(tx)

    return WalletResponse(user_id=user_id, balance=wallets[user_id])


@app.post("/wallet/{user_id}/withdraw", response_model=WalletResponse)
def wallet_withdraw(user_id: int, op: WalletOperation):
    if user_id not in wallets:
        raise HTTPException(status_code=404, detail="Utilisateur introuvable")
    if op.amount <= 0:
        raise HTTPException(status_code=400, detail="Montant invalide")
    if wallets[user_id] < op.amount:
        raise HTTPException(status_code=400, detail="Solde insuffisant")

    wallets[user_id] -= op.amount

    tx = Transaction(
        type="withdraw",
        amount=op.amount,
        description=op.description or "Retrait BerylPay",
        balance_after=wallets[user_id],
    )
    history[user_id].append(tx)

    return WalletResponse(user_id=user_id, balance=wallets[user_id])


@app.get("/wallet/{user_id}/transactions", response_model=List[Transaction])
def wallet_transactions(user_id: int):
    if user_id not in history:
        raise HTTPException(status_code=404, detail="Utilisateur introuvable")
    return history[user_id]
# =========================
# BérylCommunity (MVP)
# =========================
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel

# Stockage en mémoire
community_posts: dict[int, dict] = {}          # post_id -> {id, user_id, content, image_url, created_at, likes}
community_comments: dict[int, list] = {}       # post_id -> [ {id, post_id, user_id, text, created_at} ]
_next_post_id = 1
_next_comment_id = 1


# --------- Schemas ----------
class PostCreate(BaseModel):
    user_id: int
    content: str
    image_url: Optional[str] = None


class PostOut(BaseModel):
    id: int
    user_id: int
    content: str
    image_url: Optional[str] = None
    created_at: str
    likes: int


class CommentCreate(BaseModel):
    user_id: int
    text: str


class CommentOut(BaseModel):
    id: int
    post_id: int
    user_id: int
    text: str
    created_at: str


# --------- Helpers ----------
def _now_iso() -> str:
    return datetime.utcnow().isoformat(timespec="seconds") + "Z"


# --------- Endpoints ----------
@app.post("/community/posts", response_model=PostOut, tags=["community"])
def community_create_post(data: PostCreate):
    global _next_post_id
    # garde-fou: l'utilisateur doit exister dans le MVP courant
    if data.user_id not in users:
        raise HTTPException(status_code=404, detail="Utilisateur introuvable")

    post = {
        "id": _next_post_id,
        "user_id": data.user_id,
        "content": data.content.strip(),
        "image_url": data.image_url,
        "created_at": _now_iso(),
        "likes": 0,
    }
    community_posts[_next_post_id] = post
    community_comments[_next_post_id] = []
    _next_post_id += 1
    return post


@app.get("/community/feed", response_model=List[PostOut], tags=["community"])
def community_feed(limit: int = 20, offset: int = 0):
    # tri anti-chronologique
    posts = sorted(community_posts.values(), key=lambda p: p["created_at"], reverse=True)
    return posts[offset : offset + limit]


@app.post("/community/posts/{post_id}/comments", response_model=CommentOut, tags=["community"])
def community_add_comment(post_id: int, data: CommentCreate):
    global _next_comment_id
    if post_id not in community_posts:
        raise HTTPException(status_code=404, detail="Post introuvable")
    if data.user_id not in users:
        raise HTTPException(status_code=404, detail="Utilisateur introuvable")

    comment = {
        "id": _next_comment_id,
        "post_id": post_id,
        "user_id": data.user_id,
        "text": data.text.strip(),
        "created_at": _now_iso(),
    }
    community_comments[post_id].append(comment)
    _next_comment_id += 1
    return comment


@app.get("/community/posts/{post_id}/comments", response_model=List[CommentOut], tags=["community"])
def community_list_comments(post_id: int):
    if post_id not in community_posts:
        raise HTTPException(status_code=404, detail="Post introuvable")
    return community_comments.get(post_id, [])


@app.post("/community/posts/{post_id}/like", response_model=PostOut, tags=["community"])
def community_like_post(post_id: int, user_id: int):
    if post_id not in community_posts:
        raise HTTPException(status_code=404, detail="Post introuvable")
    if user_id not in users:
        raise HTTPException(status_code=404, detail="Utilisateur introuvable")

    community_posts[post_id]["likes"] += 1
    return community_posts[post_id]
# =========================
# Beryl E-Mobility (MVP)
# =========================
from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime

# Stockage en mémoire
rides: dict[int, dict] = {}  # ride_id -> ride dict
_next_ride_id = 1

RIDE_STATUSES = {"requested", "assigned", "in_progress", "completed", "canceled", "payment_failed"}


def _iso_now() -> str:
    return datetime.utcnow().isoformat(timespec="seconds") + "Z"


# ---------- Schémas ----------
class RideCreate(BaseModel):
    user_id: int
    pickup: str
    destination: str
    estimated_fare: float  # FCFA


class RideOut(BaseModel):
    id: int
    user_id: int
    driver_id: Optional[int] = None
    pickup: str
    destination: str
    status: str
    estimated_fare: float
    actual_fare: Optional[float] = None
    distance_km: Optional[float] = None
    duration_min: Optional[int] = None
    created_at: str
    updated_at: str


class RideComplete(BaseModel):
    actual_fare: float
    distance_km: float
    duration_min: int
    note: Optional[str] = None


# ---------- Endpoints ----------
@app.post("/mobility/rides", response_model=RideOut, tags=["mobility"])
def create_ride(data: RideCreate):
    global _next_ride_id
    if data.user_id not in users:
        raise HTTPException(status_code=404, detail="Utilisateur introuvable")
    if data.estimated_fare <= 0:
        raise HTTPException(status_code=400, detail="estimated_fare doit être > 0")

    ride = {
        "id": _next_ride_id,
        "user_id": data.user_id,
        "driver_id": None,
        "pickup": data.pickup.strip(),
        "destination": data.destination.strip(),
        "status": "requested",
        "estimated_fare": float(data.estimated_fare),
        "actual_fare": None,
        "distance_km": None,
        "duration_min": None,
        "created_at": _iso_now(),
        "updated_at": _iso_now(),
    }
    rides[_next_ride_id] = ride
    _next_ride_id += 1
    return ride


@app.post("/mobility/rides/{ride_id}/assign", response_model=RideOut, tags=["mobility"])
def assign_ride(ride_id: int, driver_id: int):
    ride = rides.get(ride_id)
    if not ride:
        raise HTTPException(status_code=404, detail="Trajet introuvable")
    if ride["status"] not in {"requested", "canceled", "payment_failed"}:
        raise HTTPException(status_code=409, detail="Le trajet n'est pas assignable")
    ride["driver_id"] = driver_id
    ride["status"] = "assigned"
    ride["updated_at"] = _iso_now()
    return ride


@app.post("/mobility/rides/{ride_id}/start", response_model=RideOut, tags=["mobility"])
def start_ride(ride_id: int):
    ride = rides.get(ride_id)
    if not ride:
        raise HTTPException(status_code=404, detail="Trajet introuvable")
    if ride["status"] != "assigned":
        raise HTTPException(status_code=409, detail="Le trajet doit être 'assigned' pour démarrer")
    ride["status"] = "in_progress"
    ride["updated_at"] = _iso_now()
    return ride


@app.post("/mobility/rides/{ride_id}/complete", response_model=RideOut, tags=["mobility"])
def complete_ride(ride_id: int, data: RideComplete):
    ride = rides.get(ride_id)
    if not ride:
        raise HTTPException(status_code=404, detail="Trajet introuvable")
    if ride["status"] != "in_progress":
        raise HTTPException(status_code=409, detail="Le trajet doit être 'in_progress' pour être clôturé")
    if data.actual_fare <= 0:
        raise HTTPException(status_code=400, detail="actual_fare doit être > 0")

    user_id = ride["user_id"]
    # Paiement automatique via BerylPay
    balance = wallets.get(user_id)
    if balance is None:
        raise HTTPException(status_code=404, detail="Wallet introuvable")

    if balance < data.actual_fare:
        ride["status"] = "payment_failed"
        ride["actual_fare"] = float(data.actual_fare)
        ride["distance_km"] = float(data.distance_km)
        ride["duration_min"] = int(data.duration_min)
        ride["updated_at"] = _iso_now()
        raise HTTPException(status_code=400, detail="Solde insuffisant, paiement échoué")

    # Débit du wallet + enregistrement transaction
    wallets[user_id] -= data.actual_fare
    history[user_id].append(Transaction(
        type="withdraw",
        amount=data.actual_fare,
        description=f"Paiement trajet #{ride_id}",
        balance_after=wallets[user_id]
    ))

    ride["status"] = "completed"
    ride["actual_fare"] = float(data.actual_fare)
    ride["distance_km"] = float(data.distance_km)
    ride["duration_min"] = int(data.duration_min)
    ride["updated_at"] = _iso_now()
    return ride


@app.get("/mobility/rides/{ride_id}", response_model=RideOut, tags=["mobility"])
def get_ride(ride_id: int):
    ride = rides.get(ride_id)
    if not ride:
        raise HTTPException(status_code=404, detail="Trajet introuvable")
    return ride


@app.get("/mobility/rides", response_model=List[RideOut], tags=["mobility"])
def list_rides(user_id: Optional[int] = None, status: Optional[str] = None, limit: int = 50, offset: int = 0):
    data = list(rides.values())
    if user_id is not None:
        data = [r for r in data if r["user_id"] == user_id]
    if status is not None:
        if status not in RIDE_STATUSES:
            raise HTTPException(status_code=400, detail="status invalide")
        data = [r for r in data if r["status"] == status]
    # anti-chronologique
    data.sort(key=lambda r: r["updated_at"], reverse=True)
    return data[offset: offset + limit]
# =========================
# ESG Podometer (MVP)
# =========================
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

# Facteur d’évitement CO2 (kg CO2 / km) pour comparaison thermique -> VE.
CO2_FACTOR_KG_PER_KM = 0.192

# Stockage en mémoire
_esg_activities: dict[int, list] = {}   # user_id -> [activity dict]
_next_esg_id = 1


def _iso_now() -> str:
    return datetime.utcnow().isoformat(timespec="seconds") + "Z"


class ESGActivityCreate(BaseModel):
    user_id: int
    activity_type: str            # "walk" | "e_ride" | "charge" | "bike" | "other"
    distance_km: float = 0.0      # km évités/ parcourus en mode bas-carbone
    co2_factor_override: Optional[float] = None
    note: Optional[str] = None


class ESGActivityOut(BaseModel):
    id: int
    user_id: int
    activity_type: str
    distance_km: float
    co2_saved_kg: float
    note: Optional[str] = None
    timestamp: str


class ESGSummaryOut(BaseModel):
    user_id: int
    total_distance_km: float
    total_co2_saved_kg: float
    activities_count: int


def _compute_co2_saved(distance_km: float, factor: Optional[float]) -> float:
    f = CO2_FACTOR_KG_PER_KM if factor is None else factor
    return round(max(distance_km, 0.0) * max(f, 0.0), 4)


@app.post("/esg/activity", response_model=ESGActivityOut, tags=["esg"])
def esg_add_activity(data: ESGActivityCreate):
    global _next_esg_id
    if data.user_id not in users:
        raise HTTPException(status_code=404, detail="Utilisateur introuvable")
    if data.distance_km < 0:
        raise HTTPException(status_code=400, detail="distance_km doit être >= 0")

    co2_saved = _compute_co2_saved(data.distance_km, data.co2_factor_override)

    act = {
        "id": _next_esg_id,
        "user_id": data.user_id,
        "activity_type": data.activity_type.strip(),
        "distance_km": float(data.distance_km),
        "co2_saved_kg": co2_saved,
        "note": (data.note or "").strip() or None,
        "timestamp": _iso_now(),
    }
    _esg_activities.setdefault(data.user_id, []).append(act)
    _next_esg_id += 1
    return act


@app.get("/esg/history/{user_id}", response_model=List[ESGActivityOut], tags=["esg"])
def esg_history(user_id: int, limit: int = 50, offset: int = 0):
    if user_id not in users:
        raise HTTPException(status_code=404, detail="Utilisateur introuvable")
    data = list(reversed(_esg_activities.get(user_id, [])))  # anti-chronologique
    return data[offset: offset + limit]


@app.get("/esg/summary/{user_id}", response_model=ESGSummaryOut, tags=["esg"])
def esg_summary(user_id: int):
    if user_id not in users:
        raise HTTPException(status_code=404, detail="Utilisateur introuvable")
    acts = _esg_activities.get(user_id, [])
    total_km = round(sum(a["distance_km"] for a in acts), 3)
    total_co2 = round(sum(a["co2_saved_kg"] for a in acts), 3)
    return ESGSummaryOut(
        user_id=user_id,
        total_distance_km=total_km,
        total_co2_saved_kg=total_co2,
        activities_count=len(acts),
    )
# =========================
# Profil Utilisateur (MVP)
# =========================
from typing import Optional
from pydantic import BaseModel

# Assure la présence des champs de profil pour les users existants
def _ensure_profile(user_id: int):
    if user_id in users:
        u = users[user_id]
        if "display_name" not in u: u["display_name"] = None
        if "phone" not in u: u["phone"] = None
        if "avatar_url" not in u: u["avatar_url"] = None

# Étend l'inscription existante si tu veux enrichir à la création
# (à utiliser si tu modifies /users/register)
# users[user_id] = {"email": data.email, "password": data.password,
#                   "display_name": None, "phone": None, "avatar_url": None}

class ProfileOut(BaseModel):
    user_id: int
    email: str
    display_name: Optional[str] = None
    phone: Optional[str] = None
    avatar_url: Optional[str] = None

class ProfileUpdate(BaseModel):
    display_name: Optional[str] = None
    phone: Optional[str] = None
    avatar_url: Optional[str] = None

@app.get("/users/{user_id}/profile", response_model=ProfileOut, tags=["users"])
def get_profile(user_id: int):
    if user_id not in users:
        raise HTTPException(status_code=404, detail="Utilisateur introuvable")
    _ensure_profile(user_id)
    u = users[user_id]
    return ProfileOut(
        user_id=user_id,
        email=u["email"],
        display_name=u.get("display_name"),
        phone=u.get("phone"),
        avatar_url=u.get("avatar_url"),
    )

@app.patch("/users/{user_id}/profile", response_model=ProfileOut, tags=["users"])
def update_profile(user_id: int, data: ProfileUpdate):
    if user_id not in users:
        raise HTTPException(status_code=404, detail="Utilisateur introuvable")
    _ensure_profile(user_id)
    u = users[user_id]

    if data.display_name is not None:
        name = data.display_name.strip()
        u["display_name"] = name if name else None

    if data.phone is not None:
        phone = data.phone.strip()
        # contrôle simple; durcis si besoin (regex)
        if phone and len(phone) < 6:
            raise HTTPException(status_code=400, detail="Numéro invalide")
        u["phone"] = phone if phone else None

    if data.avatar_url is not None:
        url = data.avatar_url.strip()
        u["avatar_url"] = url if url else None

    return ProfileOut(
        user_id=user_id,
        email=u["email"],
        display_name=u.get("display_name"),
        phone=u.get("phone"),
        avatar_url=u.get("avatar_url"),
    )

# Raccourci pour mettre à jour seulement l'avatar via query string
@app.post("/users/{user_id}/avatar", response_model=ProfileOut, tags=["users"])
def set_avatar(user_id: int, url: str):
    if user_id not in users:
        raise HTTPException(status_code=404, detail="Utilisateur introuvable")
    _ensure_profile(user_id)
    users[user_id]["avatar_url"] = url.strip() or None
    u = users[user_id]
    return ProfileOut(
        user_id=user_id,
        email=u["email"],
        display_name=u.get("display_name"),
        phone=u.get("phone"),
        avatar_url=u.get("avatar_url"),
    )
