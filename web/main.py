from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse

from database import session
from models import Link, Booking

app = FastAPI()


def get_user_seats(user_id):
    booking = session.query(Booking).filter_by(user_id=user_id, payment_confirmed=True).first()
    return booking.seats if booking else 0


def expire_link(link):
    link.expired = True
    session.commit()


@app.get("/confirm/{token}", response_class=HTMLResponse)
def confirm_link(token: str):
    link = session.query(Link).filter_by(token=token).first()
    if link and not link.expired:
        seats = get_user_seats(link.user_id)
        expire_link(link)
        return f"<h1>Вы приобрели {seats} мест(а).</h1>"
    else:
        raise HTTPException(status_code=404, detail="Ссылка недействительна или уже была использована.")
