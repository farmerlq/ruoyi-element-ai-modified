from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from core.database import get_db
from core.deps import get_current_user_or_raise
from models.merchant import Merchant
from schemas.merchant import MerchantCreate, MerchantUpdate, Merchant as MerchantSchema

router = APIRouter()

@router.post("/", response_model=MerchantSchema, status_code=status.HTTP_201_CREATED)
def create_merchant(
    merchant: MerchantCreate, 
    db: Session = Depends(get_db),
    current_user: Merchant = Depends(get_current_user_or_raise)
):
    db_merchant = Merchant(**merchant.dict())
    db.add(db_merchant)
    db.commit()
    db.refresh(db_merchant)
    return db_merchant

@router.get("/{merchant_id}", response_model=MerchantSchema)
def read_merchant(
    merchant_id: int, 
    db: Session = Depends(get_db),
    current_user: Merchant = Depends(get_current_user_or_raise)
):
    db_merchant = db.query(Merchant).filter(Merchant.id == merchant_id).first()
    if db_merchant is None:
        raise HTTPException(status_code=404, detail="Merchant not found")
    return db_merchant

@router.get("/", response_model=List[MerchantSchema])
def read_merchants(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db),
    current_user: Merchant = Depends(get_current_user_or_raise)
):
    merchants = db.query(Merchant).offset(skip).limit(limit).all()
    return merchants

@router.put("/{merchant_id}", response_model=MerchantSchema)
def update_merchant(
    merchant_id: int, 
    merchant: MerchantUpdate, 
    db: Session = Depends(get_db),
    current_user: Merchant = Depends(get_current_user_or_raise)
):
    db_merchant = db.query(Merchant).filter(Merchant.id == merchant_id).first()
    if db_merchant is None:
        raise HTTPException(status_code=404, detail="Merchant not found")
    
    for key, value in merchant.dict(exclude_unset=True).items():
        setattr(db_merchant, key, value)
        
    db.commit()
    db.refresh(db_merchant)
    return db_merchant

@router.delete("/{merchant_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_merchant(
    merchant_id: int, 
    db: Session = Depends(get_db),
    current_user: Merchant = Depends(get_current_user_or_raise)
):
    db_merchant = db.query(Merchant).filter(Merchant.id == merchant_id).first()
    if db_merchant is None:
        raise HTTPException(status_code=404, detail="Merchant not found")
    
    db.delete(db_merchant)
    db.commit()
    return None