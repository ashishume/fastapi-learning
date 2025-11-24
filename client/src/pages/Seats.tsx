import { createBooking, getBookingSeats, getSeats } from "../api";
import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import type { BookingSeat, Seat } from "../api/models";
import { useToast } from "../context/ToastContext";

const Seats = () => {
  const { theater_id, showing_id } = useParams();
  const { success, error } = useToast();

  const SEAT_PRICE = 100;
  const [seats, setSeats] = useState<Seat[]>([]);
  const [bookedSeats, setBookedSeats] = useState<BookingSeat[]>([]);
  const [selectedSeats, setSelectedSeats] = useState<Seat[]>([]);
  useEffect(() => {
    async function load() {
      const bookingSeats = await getBookingSeats(showing_id || "");
      setBookedSeats(bookingSeats);
      const seats = await getSeats(theater_id || "");
      let result: any = {};
      seats.forEach((seat: Seat) => {
        if (!result[seat.row]) {
          result[seat.row] = [];
          result[seat.row].push(seat);
        } else {
          result[seat.row].push(seat);
        }
      });

      setSeats(result);
    }
    load();
  }, [theater_id]);

  const seatTypes = {
    REGULAR: "regular",
    PREMIUM: "premium",
    VIP: "vip",
    RECLINER: "recliner",
  };

  const handleSeatClick = (seat: Seat) => {
    if (selectedSeats.some((s) => s.seat_number === seat.seat_number)) {
      setSelectedSeats(
        selectedSeats.filter((s) => s.seat_number !== seat.seat_number)
      );
    } else {
      setSelectedSeats([...selectedSeats, seat]);
    }
  };

  const submitBooking = async () => {
    const bookingStatus = await createBooking({
      showing_id: showing_id || "",
      seats_ids: selectedSeats.map((seat) => seat.id),
      total_price: selectedSeats.reduce((acc, seat) => acc + SEAT_PRICE, 0),
    });

    if (bookingStatus.status === "confirmed") {
      // alert("Booking successful");
      success("Booking successful");
      setSelectedSeats([]);

      const bookingSeats = await getBookingSeats(showing_id || "");
      setBookedSeats(bookingSeats);
    } else {
      error(bookingStatus.message);
    }
  };

  return (
    <div>
      <div className={`flex gap-4 w-full`}>
        {Object.keys(seats).map((row: any) => (
          <div key={row} className="flex flex-col gap-1">
            {(seats[row] as any).map((seat: Seat) => (
              <div key={`${seat.seat_number}`}>
                <div
                  onClick={() => handleSeatClick(seat)}
                  key={`${seat.seat_number}`}
                  className={`w-12 h-12 bg-gray-200 cursor-pointer rounded-xl flex items-center justify-center gap-2 m-1 
                    ${
                      selectedSeats.some(
                        (s) => s.seat_number === seat.seat_number
                      )
                        ? "bg-blue-500! text-white"
                        : ""
                    }  ${
                    bookedSeats.some((s) => s.seat_id === seat.id)
                      ? "bg-red-200! text-gray-500 disabled:cursor-not-allowed"
                      : ""
                  }`}
                >
                  {`${seat.seat_number}`}
                </div>
              </div>
            ))}
          </div>
        ))}
      </div>
      <button
        onClick={submitBooking}
        className="bg-blue-500 text-white px-4 py-2 rounded-md"
      >
        Submit Booking
      </button>
    </div>
  );
};

export default Seats;
