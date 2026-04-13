# API de Cashback – Fintech Nology

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import databases
import sqlalchemy
import os
from datetime import datetime

# ==============================
# DATABASE
# ==============================

DATABASE_URL = os.getenv("DATABASE_URL")

if DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")

database = databases.Database(DATABASE_URL)
metadata = sqlalchemy.MetaData()

consultas = sqlalchemy.Table(
    "consultas",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("ip", sqlalchemy.String(64), nullable=False),
    sqlalchemy.Column("tipo_cliente", sqlalchemy.String(16), nullable=False),
    sqlalchemy.Column("valor_compra", sqlalchemy.Float, nullable=False),
    sqlalchemy.Column("desconto", sqlalchemy.Float, nullable=False, default=0),
    sqlalchemy.Column("cashback", sqlalchemy.Float, nullable=False),
    sqlalchemy.Column(
        "criado_em",
        sqlalchemy.DateTime,
        default=datetime.utcnow  # ✅ default correto
    ),
)

# Remove asyncpg para sync engine (create_all)
sync_database_url = DATABASE_URL.replace("+asyncpg", "")

engine = sqlalchemy.create_engine(sync_database_url)

metadata.create_all(engine)

# ==============================
# APP
# ==============================

app = FastAPI(title="Cashback API – Nology")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup():
    await database.connect()

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()

# ==============================
# LOGICA DE NEGOCIO
# ==============================

def calcular_cashback(valor_compra: float, desconto_percentual: float, vip: bool) -> dict:
    desconto = valor_compra * (desconto_percentual / 100)
    valor_final = valor_compra - desconto

    cashback_base = valor_final * 0.05
    bonus_vip = cashback_base * 0.10 if vip else 0.0
    cashback_subtotal = cashback_base + bonus_vip

    dobrado = valor_final > 500
    cashback_final = cashback_subtotal * (2 if dobrado else 1)

    return {
        "valor_compra": round(valor_compra, 2),
        "desconto_percentual": desconto_percentual,
        "desconto_reais": round(desconto, 2),
        "valor_final": round(valor_final, 2),
        "vip": vip,
        "cashback_base": round(cashback_base, 2),
        "bonus_vip": round(bonus_vip, 2),
        "cashback_subtotal": round(cashback_subtotal, 2),
        "dobrado": dobrado,
        "cashback_final": round(cashback_final, 2),
    }

# ==============================
# SCHEMA
# ==============================

class ConsultaRequest(BaseModel):
    tipo_cliente: str   # "vip" ou "regular"
    valor_compra: float
    desconto: float = 0.0

# ==============================
# ENDPOINTS
# ==============================

@app.post("/calcular")
async def calcular(req: ConsultaRequest, request: Request):
    vip = req.tipo_cliente.lower() == "vip"

    resultado = calcular_cashback(
        req.valor_compra,
        req.desconto,
        vip
    )

    # Captura IP
    ip = request.headers.get("x-forwarded-for", request.client.host)
    ip = ip.split(",")[0].strip()

    # 🔥 NÃO precisa passar criado_em (já tem default)
    query = consultas.insert().values(
        ip=ip,
        tipo_cliente=req.tipo_cliente.lower(),
        valor_compra=req.valor_compra,
        desconto=req.desconto,
        cashback=resultado["cashback_final"],
    )

    await database.execute(query)

    return resultado


@app.get("/historico")
async def historico(request: Request):
    ip = request.headers.get("x-forwarded-for", request.client.host)
    ip = ip.split(",")[0].strip()

    query = (
        consultas.select()
        .where(consultas.c.ip == ip)
        .order_by(consultas.c.criado_em.desc())
        .limit(50)
    )

    rows = await database.fetch_all(query)

    return [
        {
            "tipo_cliente": r["tipo_cliente"],
            "valor_compra": r["valor_compra"],
            "desconto": r["desconto"],
            "cashback": r["cashback"],
            "criado_em": r["criado_em"].isoformat() if r["criado_em"] else None,
        }
        for r in rows
    ]


@app.get("/health")
async def health():
    return {"status": "ok"}