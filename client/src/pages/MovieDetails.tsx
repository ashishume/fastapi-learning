import { useNavigate, useParams } from "react-router-dom";
import { useEffect, useState } from "react";
import { getMovieById } from "../api";
import type { Movie } from "../api/models";

export default function MovieDetails() {
  const { movie_id } = useParams();
  const [movie, setMovie] = useState<Movie | null>(null);
  const navigate = useNavigate();
  useEffect(() => {
    async function load() {
      // Replace this with your API endpoint
      const res = await getMovieById(movie_id || "");
      console.log(res);
      setMovie(res);
    }
    load();
  }, [movie_id]);

  if (!movie) {
    return (
      <div className="p-6 text-center text-gray-600">
        Loading movie details...
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto p-6">
      <div className="border rounded-xl bg-white shadow-sm overflow-hidden">
        {/* Poster */}
        <img
          src={movie.poster_url || ""}
          alt={movie.title}
          className="w-full h-64 object-cover"
        />

        <div className="p-6 space-y-4">
          {/* Movie Title */}
          <h1 className="text-2xl font-semibold">{movie.title}</h1>

          {/* Basic Info */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <Detail label="Booking Number" value={movie.description || ""} />
            <Detail label="Status" value={movie.genre || ""} />
            <Detail label="Total Price" value={`₹${movie.rating}`} />
            <Detail
              label="Show Time"
              value={new Date(movie.release_date || "").toLocaleString()}
            />
          </div>

          {/* Seat Info */}
          <div className="mt-4 border-t pt-4">
            <h2 className="text-lg font-semibold">Seat Information</h2>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 mt-2">
              <Detail label="Language" value={movie.language || ""} />
              <Detail label="Type" value={movie.is_imax ? "IMAX" : "Normal"} />
              <Detail label="Row" value={movie.director || ""} />
              <Detail label="Cast" value={movie.cast?.join(", ") || ""} />
            </div>
          </div>

          {/* Theater Info */}
          <div className="mt-4 border-t pt-4">
            <h2 className="text-lg font-semibold">Theater</h2>
            <p className="text-gray-700 mt-2">
              {movie.director}, {movie.genre}
            </p>
            <p className="text-sm text-gray-500">{movie.release_date}</p>
          </div>

          <button
            onClick={() => navigate(`/movies/${movie_id}/theaters`)}
            className="w-full mt-6 py-2 rounded-md bg-black text-white"
          >
            Book Tickets
          </button>
        </div>
      </div>
    </div>
  );
}

function Detail({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <p className="text-sm text-gray-500">{label}</p>
      <p className="font-medium">{value}</p>
    </div>
  );
}
