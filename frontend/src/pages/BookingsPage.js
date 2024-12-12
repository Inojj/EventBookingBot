import React, { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import axios from "../axiosSetup"; // Используем настроенный axios

const BookingsPage = () => {
  const { eventGuid } = useParams();
  const [bookings, setBookings] = useState([]);
  const [eventDetails, setEventDetails] = useState(null); // Детали мероприятия
  const [error, setError] = useState("");

  useEffect(() => {
    const fetchBookingsAndEvent = async () => {
      try {
        // Получение бронирований
        const bookingsResponse = await axios.get(`/bookings/?event_guid=${eventGuid}`);
        setBookings(bookingsResponse.data);

        // Получение деталей мероприятия
        const eventResponse = await axios.get(`/events/${eventGuid}`);
        setEventDetails(eventResponse.data);
      } catch (err) {
        setError("Не удалось загрузить данные.");
      }
    };

    fetchBookingsAndEvent();
  }, [eventGuid]);

  const downloadPaymentFile = async (bookingGuid) => {
    try {
      const response = await axios.get(`/bookings/${bookingGuid}/payment-file`, {
        responseType: "blob",
      });

      const contentDisposition = response.headers["content-disposition"];
      let fileName = "payment_confirmation";

      if (contentDisposition) {
      // Попытка извлечь имя файла в формате filename*=utf-8''
        const utf8Match = contentDisposition.match(/filename\*=(?:UTF-8'')?(.+)/i);
        if (utf8Match && utf8Match[1]) {
            fileName = decodeURIComponent(utf8Match[1]); // Декодируем URL-encoded строку
        } else {
        // Попытка извлечь имя файла в формате filename=""
            const match = contentDisposition.match(/filename="?([^"]+)"?/);
            if (match && match[1]) {
                fileName = match[1];
            }
        }
    }

      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement("a");
      link.href = url;
      link.setAttribute("download", fileName);
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (err) {
      console.error("Ошибка при скачивании файла:", err);
      alert("Не удалось скачать файл.");
    }
  };

  const exportToCSV = () => {
    const csvRows = [
      ["GUID", "Телефон", "Никнейм", "Места", "Подтверждено", "Срок истёк"],
      ...bookings.map((booking) => [
        booking.guid,
        booking.user_phone,
        booking.user_nickname || "—",
        booking.count_seats,
        booking.verified ? "Да" : "Нет",
        booking.expired ? "Да" : "Нет",
      ]),
    ];

    const csvContent =
      "data:text/csv;charset=utf-8," +
      csvRows.map((row) => row.join(",")).join("\n");

    const encodedUri = encodeURI(csvContent);
    const link = document.createElement("a");
    link.setAttribute("href", encodedUri);
    link.setAttribute("download", "bookings.csv");
    document.body.appendChild(link);
    link.click();
    link.remove();
  };

  const verifyBooking = async (bookingGuid) => {
    try {
      await axios.patch(`/bookings/${bookingGuid}`, {
        verified: true,
      });
      alert("Оплата подтверждена.");
      setBookings((prev) =>
        prev.map((booking) =>
          booking.guid === bookingGuid ? { ...booking, verified: true } : booking
        )
      );
    } catch (err) {
      console.error("Ошибка при подтверждении оплаты:", err);
      alert("Не удалось подтвердить оплату.");
    }
  };

  if (error) {
    return <div>{error}</div>;
  }

  if (!eventDetails || !bookings.length) {
    return <div>Загрузка данных...</div>;
  }

  // Рассчёт оставшихся мест
  const totalBooked = bookings.reduce(
    (acc, booking) => acc + booking.count_seats,
    0
  );
  const remainingSeats = eventDetails.max_seats - totalBooked;

  return (
    <div>
      <h1>Список бронирований</h1>
      <p>
        Всего мест: {eventDetails.max_seats}, Занято: {totalBooked}, Свободно:{" "}
        {remainingSeats}
      </p>
      <button onClick={exportToCSV}>Экспорт в CSV</button>
      <table>
        <thead>
          <tr>
            <th>GUID</th>
            <th>Телефон</th>
            <th>Никнейм</th>
            <th>Места</th>
            <th>Подтверждено</th>
            <th>Срок истёк</th>
            <th>Действия</th>
          </tr>
        </thead>
        <tbody>
          {bookings.map((booking) => (
            <tr key={booking.guid}>
              <td>{booking.guid}</td>
              <td>{booking.user_phone}</td>
              <td>{booking.user_nickname || "—"}</td>
              <td>{booking.count_seats}</td>
              <td>{booking.verified ? "Да" : "Нет"}</td>
              <td>{booking.expired ? "Да" : "Нет"}</td>
              <td>
                <button onClick={() => downloadPaymentFile(booking.guid)}>
                  Скачать файл
                </button>
                {!booking.verified && (
                  <button onClick={() => verifyBooking(booking.guid)}>
                    Подтвердить оплату
                  </button>
                )}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default BookingsPage;
