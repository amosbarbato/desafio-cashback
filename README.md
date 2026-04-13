# Cashback App – Fintech Nology

App fullstack para cálculo e histórico de cashback.

## Estrutura

```
app/
├── api/
│   ├── main.py          # FastAPI – lógica de cashback + endpoints
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   └── index.html       # Frontend estático (HTML/CSS/JS puro)
└── docker-compose.yml   # Sobe tudo: Postgres + API + Frontend
```

## Rodando com Docker Compose (recomendado)

```bash
cd app
docker compose up --build
```

- Frontend: http://localhost:3000
- API: http://localhost:8000
- Docs API (Swagger): http://localhost:8000/docs

## Rodando localmente (sem Docker)

### API

```bash
cd app/api
pip install -r requirements.txt

# SQLite (padrão – sem configuração extra)
uvicorn main:app --reload

# Postgres (opcional)
DATABASE_URL=postgresql://user:pass@localhost/cashback uvicorn main:app --reload
```

### Frontend

Abra `frontend/index.html` diretamente no navegador **ou** sirva com:

```bash
cd app/frontend
npx serve .
```

> Certifique-se que `API_BASE` em `index.html` aponta para a URL correta da API.

## Endpoints da API

| Método | Rota        | Descrição                                    |
|--------|-------------|----------------------------------------------|
| POST   | /calcular   | Calcula cashback e salva no banco             |
| GET    | /historico  | Retorna histórico de consultas do IP atual    |
| GET    | /health     | Health check                                 |
| GET    | /docs       | Swagger UI (documentação interativa)         |

### POST /calcular – Payload

```json
{
  "tipo_cliente": "vip",    // "vip" ou "regular"
  "valor_compra": 600.00,
  "desconto": 15.0          // percentual (0–100)
}
```

## Deploy em produção

Opções gratuitas recomendadas:

- **API**: Railway, Render, Fly.io (suportam Postgres + Python nativamente)
- **Frontend**: Vercel, Netlify, GitHub Pages (arquivo estático)

Lembre de atualizar `API_BASE` no `index.html` com a URL da API em produção.

## Regras de negócio implementadas

1. Cashback base = 5% sobre o valor final (após desconto)
2. Bônus VIP = +10% sobre o cashback base
3. Compras com valor final > R$ 500 → cashback × 2
4. Ordem: valor final → base → VIP → dobro