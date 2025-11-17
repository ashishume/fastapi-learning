export interface Booking {
  id: string;
  movie_id: string;
  theater_id: string;
  showing_id: string;
  seats_id: string;
  total_price: number;
  status: string;
  booking_number: string;
  created_at: string;
  updated_at: string;
  movie: Movie;
  theater: Theater;
  showing: Showing;
  seats: Seat;
}

export interface Movie {
  id: string;
  title: string;
  description?: string;
  duration_minutes: number;
  genre: string;
  director?: string;
  release_date?: string;
  rating: number;
  language?: string;
  is_imax?: boolean;
  poster_url: string;
  trailer_url?: string;
  cast?: string[];
  created_at?: string;
  updated_at?: string;
}

export interface Theater {
  id: string;
  name: string;
  location: string;
  description?: string;
  address?: string;
  city: string;
  created_at?: string;
  updated_at?: string;
}

export interface Showing {
  id: string;
  movie_id: string;
  theater_id: string;
  show_start_datetime: string;
  show_end_datetime: string;
  available_seats?: number;
  is_active?: boolean;
  created_at?: string;
  updated_at?: string;
  movie?: {
    id: string;
    title: string;
    duration_minutes: number;
    genre: string;
    rating: number;
    poster_url: string;
  };
  theater?: {
    id: string;
    name: string;
    location: string;
    city: string;
  };
}

export interface Seat {
  id: string;
  theater_id: string;
  showing_id: string;
  seat_number: string;
  row: string;
  column: string;
  seat_type: string;
  created_at: string;
  updated_at: string;
  theater?: {
    id: string;
    name: string;
    location: string;
    city: string;
  };
  showing?: {
    id: string;
    movie_id: string;
    theater_id: string;
    show_start_datetime: string;
    show_end_datetime: string;
  };
}
