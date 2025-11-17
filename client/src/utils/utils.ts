// const d = new Date("2025-11-12T21:30:00");

// let hours = d.getHours(); // 21
// const minutes = d.getMinutes();

// const ampm = hours >= 12 ? "PM" : "AM";
// hours = hours % 12 || 12;

// const time12 = `${hours}:${minutes.toString().padStart(2, "0")} ${ampm}`;
// // "9:30 PM"

export const formatTime12Hr = (time: string) => {
  const d = new Date(time);
  let hours = d.getHours(); // 21
  const minutes = d.getMinutes();
  const ampm = hours >= 12 ? "PM" : "AM";
  hours = hours % 12 || 12;
  return `${hours}:${minutes.toString().padStart(2, "0")} ${ampm}`;
};

export const showDates = () => {
  const today = new Date();
  const dates = [];
  for (let i = 0; i < 7; i++) {
    dates.push(new Date(today.setDate(today.getDate() + i)));
  }
  return dates;
};

export const formatDate = (date: string) => {
  return new Date(date).toLocaleDateString("en-US", {
    weekday: "short",
    year: "numeric",
    month: "short",
    day: "numeric",
  });
};

export const formatDateParts = (date: string) => {
  const parts = new Intl.DateTimeFormat("en-US", {
    weekday: "short",
    year: "numeric",
    month: "short",
    day: "numeric",
  }).formatToParts(new Date(date));

  const map: any = {};
  parts.forEach((p) => (map[p.type] = p.value));
  return map;
};
