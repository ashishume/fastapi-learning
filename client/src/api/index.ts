import axios from "axios";
const AUTH_BASE_URL = import.meta.env.VITE_AUTH_API_URL;
const BOOKING_BASE_URL = import.meta.env.VITE_BOOKING_API_URL;

const authApi = axios.create({
  baseURL: AUTH_BASE_URL,
  withCredentials: true, // Enable sending cookies with requests
});

const bookingApi = axios.create({
  baseURL: BOOKING_BASE_URL,
  withCredentials: true, // Enable sending cookies with requests
});

// Add response interceptor to handle authentication errors globally
const setupInterceptor = (logoutCallback: () => void) => {
  const interceptor = (error: any) => {
    if (error.response?.status === 401) {
      // Token expired or invalid - clear user state
      logoutCallback();
    }
    return Promise.reject(error);
  };

  authApi.interceptors.response.use((response) => response, interceptor);
  bookingApi.interceptors.response.use((response) => response, interceptor);
};

const login = async (email: string, password: string) => {
  const response = await authApi.post("/auth/login", { email, password });
  return response.data;
};

const signup = async (email: string, password: string) => {
  const response = await authApi.post("/auth/signup", { email, password });
  return response.data;
};

const getMovies = async () => {
  const response = await bookingApi.get("/movies");
  return response.data;
};

const getMovieById = async (movie_id: string) => {
  const response = await bookingApi.get(`/movies/${movie_id}`);
  return response.data;
};

const getTheaters = async () => {
  const response = await bookingApi.get(`/theaters`);
  return response.data;
};

const getShowings = async (theater_id: string, movie_id: string) => {
  const response = await bookingApi.get(`/showings/${theater_id}/${movie_id}`);
  return response.data;
};

const getSeats = async (showing_id: string) => {
  const response = await bookingApi.get(`/seats/${showing_id}`);
  return response.data;
};

// const getBooking = async (seats_id: string) => {
//   const response = await bookingApi.get(`/seats/${seats_id}/bookings`);
//   return response.data;
// };

const createBooking = async (
  seats: {
    showing_id: string;
    seat_number: string;
    row: string;
    column: string;
    seat_type: string;
  }[]
) => {
  const response = await bookingApi.post(`/bookings`, { seats });
  return response.data;
};
export {
  authApi,
  bookingApi,
  setupInterceptor,
  login,
  signup,
  getMovies,
  getMovieById,
  getTheaters,
  getSeats,
  getShowings,
  createBooking,
};
