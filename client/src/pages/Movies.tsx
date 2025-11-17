import { useEffect, useState } from "react";
import { getMovies } from "../api";
import type { Movie } from "../api/models";
import { useNavigate } from "react-router-dom";

const Movies = () => {
  const [movies, setMovies] = useState<Movie[]>([]);
  const navigate = useNavigate();
  useEffect(() => {
    getMovies()
      .then((response) => {
        setMovies(response);
      })
      .catch((error) => {
        console.error(error);
      });
  }, []);

  return (
    <div className="max-w-7xl mx-auto">
      <h1 className="text-2xl font-bold mb-4">Movies</h1>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {movies.map((movie) => (
          <div
            key={movie.id}
            className="border rounded-xl shadow-sm bg-white overflow-hidden hover:shadow-md transition"
          >
            <img
              src={movie.poster_url}
              alt={movie.title}
              className="w-full h-48 object-cover"
            />

            <div className="p-4 space-y-2">
              <h2 className="text-lg font-semibold">{movie.title}</h2>

              <p className="text-sm text-gray-600">
                {movie.genre} • {movie.director}
              </p>

              <p className="text-sm text-gray-700">
                <span className="font-medium">Show:</span>{" "}
                {new Date(movie.release_date || "").toLocaleString()}
              </p>

              <p className="text-sm text-gray-700">
                <span className="font-medium">Seat:</span> {movie.rating}
              </p>

              <p className="text-sm text-gray-700">
                <span className="font-medium">Status:</span> {movie.language}
              </p>

              <p className="text-sm font-semibold">₹{movie.rating}</p>

              <button
                onClick={() => navigate(`/movies/${movie.id}/details`)}
                className="mt-3 w-full py-2 rounded-md bg-black text-white text-sm"
              >
                View Details
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default Movies;
