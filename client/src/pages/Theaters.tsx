import { useNavigate, useParams } from "react-router-dom";
import type { Showing, Theater } from "../api/models";
import { useEffect, useState } from "react";
import { getShowings, getTheaters } from "../api";
import { formatDateParts, formatTime12Hr, showDates } from "../utils/utils";

const Theaters = () => {
  const { movie_id } = useParams();
  const [theaters, setTheaters] = useState<Theater[]>([]);
  const [showings, setShowings] = useState<any>(null);
  const navigate = useNavigate();
  const [selectedDate, setSelectedDate] = useState<Date | null>(showDates()[0]);
  useEffect(() => {
    async function load() {
      const theaters = await getTheaters();
      let movieShowings = {} as any;
      await Promise.all(
        theaters.map(async (theater: Theater) => {
          const showings = await getShowings(theater.id, movie_id || "");
          movieShowings[theater.id] = showings;
        })
      );
      setTheaters(theaters);
      setShowings(movieShowings);
    }
    load();
  }, [movie_id]);
  return (
    <div className="max-w-7xl mx-auto">
      <div className="pb-8">
        <h1 className="text-2xl font-bold">Shows</h1>
        <div className="border-b border-gray-200 pb-4"></div>
        <div className="text-sm text-gray-500 flex gap-4 text-center hover:text-black transition-colors duration-300 cursor-pointer">
          {showDates().map((date) => (
            <div
              key={date.toISOString()}
              onClick={() => setSelectedDate(date)}
              className={`text-sm text-gray-500 px-2 py-2 ${
                selectedDate?.toDateString() === date.toDateString()
                  ? "bg-blue-500 text-white rounded-xl p-2"
                  : ""
              }`}
            >
              <div>{formatDateParts(date.toISOString()).weekday}</div>
              <div className="text-2xl font-bold">
                {formatDateParts(date.toISOString()).day}
              </div>
              <div>{formatDateParts(date.toISOString()).month}</div>
            </div>
          ))}
        </div>
      </div>
      <div className="flex flex-col">
        {theaters.map((theater) => (
          <div
            key={theater.id}
            className="border-b border-gray-200 py-4 px-2 transition-colors duration-300 cursor-pointer"
          >
            <h2 className="text-xl font-bold">{theater.name}</h2>
            <p className="text-sm text-gray-500">{theater.location}</p>
            <p className="text-sm text-gray-500">{theater.city}</p>
            <div className="flex gap-2 mt-4">
              {showings[theater.id].map((showing: Showing) => (
                <div
                  onClick={() => navigate(`/showings/${showing.id}/seats`)}
                  key={showing.id}
                  className="border border-gray-200 rounded-xl shadow-sm bg-white overflow-hidden hover:shadow-md transition flex gap-2 p-4 flex-col"
                >
                  <h3 className="text-lg font-bold">{showing.movie?.title}</h3>
                  <p className="text-sm text-gray-500">
                    {formatTime12Hr(showing.show_start_datetime)}
                  </p>
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default Theaters;
