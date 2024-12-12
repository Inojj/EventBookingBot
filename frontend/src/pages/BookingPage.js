import React, { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import axios from "../axiosSetup"; // Используем настроенный axios

const BookingPage = () => {
  const { guid } = useParams(); // Получение GUID из URL
  const [booking, setBooking] = useState(null); // Данные о бронировании
  const [error, setError] = useState(""); // Ошибки

  useEffect(() => {
    const fetchBooking = async () => {
      try {
        // Получение данных о бронировании
        const response = await axios.get(`/bookings/${guid}`);
        const bookingData = response.data;

        setBooking(bookingData);

        // Если бронирование подтверждено, но ещё не истекло, помечаем как истёкшее
        if (bookingData.verified && !bookingData.expired) {
          await axios.patch(`/bookings/${guid}`, {
            expired: true, // Обновляем только поле expired
          });
        }
      } catch (err) {
        setError("Не удалось загрузить данные бронирования.");
      }
    };

    fetchBooking();
  }, [guid]);

  if (error) {
    return <div>{error}</div>;
  }

  if (!booking) {
    return <div>Загрузка...</div>;
  }

  // Если бронирование не подтверждено
  if (!booking.verified) {
    return (
      <div>
        <h1>Бронирование не подтверждено</h1>
        <p>Ваше бронирование не было оплачено или подтверждено.</p>
        <p>Не Оплачено {booking.count_seats} мест.</p>
        <p>Телефон {booking.user_phone}</p>
        <p>Никнейм {booking.user_nickname}</p>
      </div>
    );
  }

  // Если QR-код не был сканирован
  if (booking.verified && !booking.expired) {
    return (
      <div>
        <h1>QR-код не сканировался</h1>
        <p>Оплачено {booking.count_seats} мест.</p>
        <p>Телефон {booking.user_phone}</p>
        <p>Никнейм {booking.user_nickname}</p>
      </div>
    );
  }

  // Если QR-код был сканирован
  return (
    <div>
      <h1>QR-код сканировался</h1>
      <p>Бронирование на {booking.count_seats} мест завершено.</p>
    </div>
  );
};

export default BookingPage;
