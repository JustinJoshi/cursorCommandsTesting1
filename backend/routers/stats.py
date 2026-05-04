from fastapi import APIRouter, Depends
from sqlmodel import Session, select, func, col

from backend.database import get_session
from backend.models import Listing

router = APIRouter(prefix="/api/stats", tags=["stats"])


@router.get("")
def get_stats(session: Session = Depends(get_session)):
    total = session.exec(select(func.count(Listing.id))).one()
    avg_price = session.exec(select(func.avg(Listing.price))).one()
    min_price = session.exec(select(func.min(Listing.price))).one()
    max_price = session.exec(select(func.max(Listing.price))).one()

    years_stmt = (
        select(Listing.year, func.count(Listing.id), func.avg(Listing.price))
        .group_by(Listing.year)
        .order_by(col(Listing.year).desc())
    )
    by_year = session.exec(years_stmt).all()

    models_stmt = (
        select(Listing.model, func.count(Listing.id), func.avg(Listing.price))
        .group_by(Listing.model)
        .order_by(func.count(Listing.id).desc())
    )
    by_model = session.exec(models_stmt).all()

    ratings_stmt = (
        select(Listing.deal_rating, func.count(Listing.id))
        .where(Listing.deal_rating.is_not(None))  # type: ignore
        .group_by(Listing.deal_rating)
    )
    by_rating = session.exec(ratings_stmt).all()

    return {
        "total_listings": total or 0,
        "avg_price": round(avg_price, 2) if avg_price else 0,
        "min_price": min_price or 0,
        "max_price": max_price or 0,
        "by_year": [
            {"year": row[0], "count": row[1], "avg_price": round(row[2], 2) if row[2] else 0}
            for row in by_year
        ],
        "by_model": [
            {"model": row[0], "count": row[1], "avg_price": round(row[2], 2) if row[2] else 0}
            for row in by_model
        ],
        "by_rating": [
            {"rating": row[0], "count": row[1]}
            for row in by_rating
        ],
    }


@router.get("/deals")
def get_best_deals(
    limit: int = 10,
    session: Session = Depends(get_session),
):
    """Get best deals - listings with greatest difference between price and estimated market value."""
    statement = (
        select(Listing)
        .where(Listing.estimated_market_value.is_not(None))  # type: ignore
        .where(Listing.deal_rating.in_(["great", "good"]))  # type: ignore
        .order_by((Listing.estimated_market_value - Listing.price).desc())
        .limit(limit)
    )
    deals = session.exec(statement).all()

    return [
        {
            "id": d.id,
            "title": d.title,
            "price": d.price,
            "year": d.year,
            "model": d.model,
            "estimated_market_value": d.estimated_market_value,
            "savings": round((d.estimated_market_value or 0) - d.price, 2),
            "deal_rating": d.deal_rating,
            "ai_summary": d.ai_summary,
        }
        for d in deals
    ]
