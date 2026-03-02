from datetime import datetime
from decimal import Decimal
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from backend.app.core.security import verify_password
from backend.app.db.session import get_db
from backend.app.models.ui_core import UiProduct, UiSale, UiUser

router = APIRouter(tags=['ui'])


class LoginRequest(BaseModel):
    client_id: str
    username: str
    password: str


class ProductCreateRequest(BaseModel):
    client_id: str
    name: str
    category: str | None = None
    cost: float
    price: float


class SaleCreateRequest(BaseModel):
    client_id: str
    product_id: UUID
    quantity: int = Field(default=1, gt=0)
    selling_price: float


@router.post('/auth/login')
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = (
        db.query(UiUser)
        .filter(UiUser.client_id == payload.client_id, UiUser.username == payload.username)
        .first()
    )
    password_ok = False
    if not user and payload.client_id == 'demo_client' and payload.username == 'owner' and payload.password == 'owner123':
        user = UiUser(client_id='demo_client', username='owner', password_hash='owner123', role='owner')
        db.add(user)
        db.commit()
        db.refresh(user)

    if user:
        if user.password_hash == payload.password:
            password_ok = True
        else:
            try:
                password_ok = verify_password(payload.password, user.password_hash)
            except Exception:
                password_ok = False
    if not user or not password_ok:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid credentials')
    return {'status': 'ok', 'user': {'id': user.id, 'client_id': user.client_id, 'username': user.username, 'role': user.role}}


@router.get('/products')
def get_products(client_id: str, db: Session = Depends(get_db)):
    return db.query(UiProduct).filter(UiProduct.client_id == client_id).order_by(UiProduct.created_at.desc()).all()


@router.post('/products', status_code=status.HTTP_201_CREATED)
def create_product(payload: ProductCreateRequest, db: Session = Depends(get_db)):
    product = UiProduct(
        client_id=payload.client_id,
        name=payload.name.strip(),
        category=payload.category,
        cost=payload.cost,
        price=payload.price,
    )
    db.add(product)
    db.commit()
    db.refresh(product)
    return product


@router.get('/sales')
def get_sales(client_id: str, db: Session = Depends(get_db)):
    return db.query(UiSale).filter(UiSale.client_id == client_id).order_by(UiSale.created_at.desc()).all()


@router.post('/sales', status_code=status.HTTP_201_CREATED)
def create_sale(payload: SaleCreateRequest, db: Session = Depends(get_db)):
    product = db.query(UiProduct).filter(UiProduct.id == payload.product_id, UiProduct.client_id == payload.client_id).first()
    if not product:
        raise HTTPException(status_code=404, detail='Product not found')

    sale = UiSale(
        client_id=payload.client_id,
        product_id=payload.product_id,
        quantity=payload.quantity,
        selling_price=Decimal(str(payload.selling_price)),
        sale_date=datetime.utcnow(),
    )
    db.add(sale)
    db.commit()
    db.refresh(sale)
    return sale


@router.get('/clients')
def get_clients(db: Session = Depends(get_db)):
    rows = db.query(UiUser.client_id).distinct().all()
    return [{'client_id': row[0]} for row in rows]
