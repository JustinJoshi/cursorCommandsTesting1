from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select, col

from backend.database import get_session
from backend.models import Listing, ListingCreate, ListingRead

router = APIRouter(prefix="/api/listings", tags=["listings"])


@router.get("", response_model=list[ListingRead])
def get_listings(
    year: Optional[int] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    model: Optional[str] = None,
    deal_rating: Optional[str] = None,
    sort_by: str = Query(default="captured_at", pattern="^(price|year|captured_at|deal_rating)$"),
    sort_order: str = Query(default="desc", pattern="^(asc|desc)$"),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    session: Session = Depends(get_session),
):
    statement = select(Listing)

    if year is not None:
        statement = statement.where(Listing.year == year)
    if min_price is not None:
        statement = statement.where(Listing.price >= min_price)
    if max_price is not None:
        statement = statement.where(Listing.price <= max_price)
    if model is not None:
        statement = statement.where(Listing.model == model)
    if deal_rating is not None:
        statement = statement.where(Listing.deal_rating == deal_rating)

    sort_column = getattr(Listing, sort_by)
    if sort_order == "desc":
        statement = statement.order_by(col(sort_column).desc())
    else:
        statement = statement.order_by(col(sort_column).asc())

    statement = statement.offset(offset).limit(limit)
    listings = session.exec(statement).all()
    return listings


@router.get("/{listing_id}", response_model=ListingRead)
def get_listing(listing_id: int, session: Session = Depends(get_session)):
    listing = session.get(Listing, listing_id)
    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")
    return listing


@router.post("", response_model=ListingRead, status_code=201)
def create_listing(listing: ListingCreate, session: Session = Depends(get_session)):
    db_listing = Listing.model_validate(listing)
    session.add(db_listing)
    session.commit()
    session.refresh(db_listing)
    return db_listing


@router.delete("/{listing_id}", status_code=204)
def delete_listing(listing_id: int, session: Session = Depends(get_session)):
    listing = session.get(Listing, listing_id)
    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")
    session.delete(listing)
    session.commit()
