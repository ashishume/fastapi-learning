import {
  createBooking,
  createBookingLock,
  getBookingSeats,
  getSeats,
} from "../api";
import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import type { BookingSeat, LockedSeat, Seat } from "../api/models";
import { useToast } from "../context/ToastContext";
import { useAuth } from "../context/AuthContext";

const Seats = () => {
  const { theater_id, showing_id } = useParams();
  const { success, error } = useToast();
  const { user } = useAuth();

  const SEAT_PRICE = 100;
  const [seats, setSeats] = useState<Seat[]>([]);
  const [bookedSeats, setBookedSeats] = useState<BookingSeat[]>([]);
  const [lockedSeats, setLockedSeats] = useState<LockedSeat[]>([]);
  const [selectedSeats, setSelectedSeats] = useState<Seat[]>([]);
  useEffect(() => {
    async function load() {
      const bookingSeats = await getBookingSeats(showing_id || "");
      setBookedSeats(bookingSeats.booked_seats);
      setLockedSeats(bookingSeats.locked_seats);

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

      // Populate selectedSeats with seats locked by the current user
      const userLockedSeatIds = bookingSeats.locked_seats
        .filter((lockedSeat) => lockedSeat.user_id === user?.id)
        .map((lockedSeat) => lockedSeat.seat_id);

      const userLockedSeats = seats.filter((seat: Seat) =>
        userLockedSeatIds.includes(seat.id)
      );
      setSelectedSeats(userLockedSeats);
    }
    load();
  }, [theater_id, user?.id]);

  const handleSeatClick = async (seat: Seat) => {
    const isUserLocked = lockedSeats.some(
      (lockedSeat) =>
        lockedSeat.seat_id === seat.id && lockedSeat.user_id === user?.id
    );
    const isSelected = selectedSeats.some(
      (s) => s.seat_number === seat.seat_number
    );

    // If seat is locked by user or selected, unlock it
    if (isSelected || isUserLocked) {
      setSelectedSeats(
        selectedSeats.filter((s) => s.seat_number !== seat.seat_number)
      );
      await createBookingLock({
        showing_id: showing_id || "",
        seat_id: seat.id,
        lock_seat: false,
      });
      // Refresh booked seats to remove the unlocked seat
      const bookingSeats = await getBookingSeats(showing_id || "");
      setBookedSeats(bookingSeats.booked_seats);
      setLockedSeats(bookingSeats.locked_seats);
    } else {
      // Lock the seat
      await createBookingLock({
        showing_id: showing_id || "",
        seat_id: seat.id,
        lock_seat: true,
      });
      setSelectedSeats([...selectedSeats, seat]);
      // Refresh booked seats to include the newly locked seat
      const bookingSeats = await getBookingSeats(showing_id || "");
      setBookedSeats(bookingSeats.booked_seats);
      setLockedSeats(bookingSeats.locked_seats);
    }
  };

  const submitBooking = async () => {
    const bookingStatus = await createBooking({
      showing_id: showing_id || "",
      seats_ids: selectedSeats.map((seat) => seat.id),
      total_price: selectedSeats.reduce((acc, _) => acc + SEAT_PRICE, 0),
    });

    if (bookingStatus.status === "confirmed") {
      // alert("Booking successful");
      success("Booking successful");
      setSelectedSeats([]);

      const bookingSeats = await getBookingSeats(showing_id || "");
      await setBookedSeats(bookingSeats.booked_seats);
      await setLockedSeats(bookingSeats.locked_seats);
    } else {
      error(bookingStatus.message);
    }
  };

  return (
    <div>
      <div className={`flex gap-4 w-full`}>
        {Object.keys(seats).map((row: any) => (
          <div key={row} className="flex flex-col gap-1">
            {(seats[row] as any).map((seat: Seat) => {
              const isSelected = selectedSeats.some(
                (s) => s.seat_number === seat.seat_number
              );
              const isBooked = bookedSeats.some(
                (bookedSeat) => bookedSeat.seat_id === seat.id
              );

              const isUserLocked = lockedSeats.some(
                (lockedSeat) =>
                  lockedSeat.seat_id === seat.id &&
                  lockedSeat.user_id === user?.id
              );

              const isOtherUserLocked = lockedSeats.some(
                (lockedSeat) =>
                  lockedSeat.seat_id === seat.id &&
                  lockedSeat.user_id !== user?.id
              );

              /**
               * booked : no user interaction
               * selected : user can click to select/unselect
               * user locked : user can click to unlock/lock<--> interaction enabled
               * other user locked : no user interaction
               */

              const getClassNames = () => {
                if (isBooked) {
                  return "!bg-red-200 text-gray-500 disabled:cursor-not-allowed pointer-events-none";
                }
                if (isSelected) {
                  return "!bg-blue-200 text-white";
                }
                if (isUserLocked) {
                  return "!bg-blue-200 text-white";
                }
                if (isOtherUserLocked) {
                  return "!bg-gray-500 text-white pointer-events-none";
                }
                return;
              };

              return (
                <div key={`${seat.seat_number}`}>
                  <div
                    onClick={() => handleSeatClick(seat)}
                    key={`${seat.seat_number}`}
                    className={`w-12 h-12 bg-gray-200 cursor-pointer rounded-xl flex items-center justify-center gap-2 m-1 
                      ${getClassNames()}`}
                  >
                    {`${seat.seat_number}`}
                  </div>
                </div>
              );
            })}
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
