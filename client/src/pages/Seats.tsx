import { createBooking, getSeats } from "../api";
import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import type { Seat } from "../api/models";

const Seats = () => {
  const { showing_id } = useParams();
  const [seats, setSeats] = useState<Seat[]>([]);
  const [selectedSeats, setSelectedSeats] = useState<
    { row: string; column: string }[]
  >([]);
  useEffect(() => {
    async function load() {
      const seats = await getSeats(showing_id || "");

      const seatNumbers = seats.map((seat: Seat) => seat.seat_number);
      setSeats(seatNumbers);
    }
    load();
  }, [showing_id]);

  const seatColumns = ["A", "B", "C", "D", "E", "F", "G", "H", "I"];
  const seatRows = [
    "1",
    "2",
    "3",
    "4",
    "5",
    "6",
    "7",
    "8",
    "9",
    "10",
    "11",
    "12",
    "13",
    "14",
    "15",
    "16",
    "17",
    "18",
    "19",
    "20",
    "21",
  ];

  const seatTypes = {
    REGULAR: "regular",
    PREMIUM: "premium",
    VIP: "vip",
    RECLINER: "recliner",
  };

  const seatsLayout = {
    [seatTypes.REGULAR]: {
      "1": "regular",
      "2": "regular",
      "3": "regular",
      "4": "regular",
      "5": "regular",
      "6": "regular",
      "7": "regular",
    },
    [seatTypes.VIP]: {
      "1": "regular",
      "2": "regular",
      "3": "regular",
      "4": "regular",
      "5": "regular",
      "6": "regular",
      "7": "regular",
    },
    [seatTypes.RECLINER]: {
      "1": "regular",
      "2": "regular",
      "3": "regular",
      "4": "regular",
      "5": "regular",
      "6": "regular",
      "7": "regular",
    },
    [seatTypes.PREMIUM]: {
      "1": "regular",
      "2": "regular",
      "3": "regular",
      "4": "regular",
      "5": "regular",
      "6": "regular",
      "7": "regular",
    },
  };

  const handleSeatClick = (row: string, column: string) => {
    if (
      selectedSeats.some((seat) => seat.row === row && seat.column === column)
    ) {
      setSelectedSeats(
        selectedSeats.filter(
          (seat) => !(seat.row === row && seat.column === column)
        )
      );
    } else {
      setSelectedSeats([...selectedSeats, { row: row, column: column }]);
    }
  };

  const submitBooking = async () => {
    const bookingStatus = await createBooking(
      selectedSeats.map((seat) => ({
        showing_id: showing_id || "",
        seat_number: `${seat.row}${seat.column}`,
        row: seat.row,
        column: seat.column,
        seat_type: seatTypes.REGULAR,
      }))
    );
    if (bookingStatus.status === "success") {
      // navigate("/bookings");

      alert("Booking successful");
    } else {
      alert("Booking failed");
    }
  };

  return (
    <div>
      <div className="grid grid-cols-26 gap-4 w-full">
        {seatRows.map((row, i) => (
          <div key={row} className="flex flex-col gap-1">
            {seatColumns.map((column, j) => (
              <>
                <div
                  onClick={() => handleSeatClick(row, column)}
                  key={`${row}-${column}`}
                  className={`w-12 h-12 bg-gray-200 rounded-xl flex items-center justify-center gap-2 m-1 cursor-pointer ${
                    selectedSeats.some(
                      (seat) => seat.row == row && seat.column == column
                    )
                      ? "bg-blue-500! text-white"
                      : ""
                  }`}
                >
                  {row}
                </div>
              </>
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
