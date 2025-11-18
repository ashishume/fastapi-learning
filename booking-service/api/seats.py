import datetime
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from schemas.seats import SeatCreate, SeatCreateResponse, SeatResponse, TheaterBrief
from database import get_db
from models.seats import Seat
from models.theaters import Theater
from models.showings import Showing
from typing import List
router=APIRouter()


@router.post("/",status_code=status.HTTP_201_CREATED,summary="Create a new seat",response_model=SeatCreateResponse)
def create_seat(seat: SeatCreate, db: Session = Depends(get_db)) -> SeatCreateResponse:
    try:
        new_seat = Seat(
            # theater_id=seat.theater_id,
            showing_id=seat.showing_id,
            seat_number=seat.seat_number,
            row=seat.row,
            column=seat.column,
            seat_type=seat.seat_type,
        )
        db.add(new_seat)
        db.commit()
        db.refresh(new_seat)
        return SeatCreateResponse.model_validate(new_seat)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail=f"Error creating seat: {e}")


@router.get("/",status_code=status.HTTP_200_OK,summary="Get all seats",response_model=List[SeatResponse])
def get_all_seats(db: Session = Depends(get_db)) -> List[SeatResponse]:
    try:
        seats = db.query(Seat).options(
            joinedload(Seat.showing).load_only(
                Showing.id,
                Showing.movie_id,
                Showing.theater_id,
                Showing.show_start_datetime,
                Showing.show_end_datetime
            ),
            joinedload(Seat.showing).joinedload(Showing.theater).load_only(
                Theater.id,
                Theater.name,
                Theater.location,
                Theater.city
            ),
        ).filter(Seat.showing.has(Showing.expires_at > datetime.datetime.utcnow())).all()
        
        # Build response with theater details from showing
        result = []
        for seat in seats:
            seat_dict = SeatResponse.model_validate(seat).model_dump()
            # Extract theater from showing relationship if available
            if seat.showing and seat.showing.theater:
                seat_dict['theater'] = TheaterBrief.model_validate(seat.showing.theater).model_dump()
            result.append(SeatResponse(**seat_dict))
        
        return result
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail=f"Error getting seats: {e}")



@router.delete("/{seat_id}",status_code=status.HTTP_204_NO_CONTENT,summary="Delete a seat",response_model=None)
def delete_seat(seat_id: UUID, db: Session = Depends(get_db)) -> None:
        try:
            seat = db.query(Seat).filter(Seat.id == seat_id).first()
            if seat is None:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Seat not found")
            db.delete(seat)
            db.commit()
            return None
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail=f"Error deleting seat: {e}")