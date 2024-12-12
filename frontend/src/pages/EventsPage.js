import React, { useEffect, useState } from "react";
import axios from "../axiosSetup"; // Используем настроенный axios
import { useNavigate } from "react-router-dom";

function EventsPage() {
  const [events, setEvents] = useState([]);
  const navigate = useNavigate();

  useEffect(() => {
    fetchEvents();
  }, []);

  const fetchEvents = async () => {
  try {
    const response = await axios.get("/events");
    setEvents(response.data);
  } catch (error) {
    console.error("Ошибка при загрузке мероприятий:", error);

    // Проверяем статус ошибки
    if (error.response && error.response.status === 401) {
      alert("Вы не авторизованы. Пожалуйста, войдите в систему.");
      navigate("/login"); // Перенаправляем на страницу входа
    } else {
      alert("Не удалось загрузить мероприятия.");
    }
  }
};

  const handleDelete = async (guid) => {
    if (window.confirm("Вы уверены, что хотите удалить мероприятие?")) {
      try {
        await axios.delete(`/events/${guid}`);
        fetchEvents(); // Обновляем список после удаления
      } catch (error) {
        console.error("Ошибка при удалении мероприятия:", error);
        alert("Не удалось удалить мероприятие.");
      }
    }
  };

  return (
    <div>
      <h1>Список мероприятий</h1>
      <button onClick={() => navigate("/events/new")}>Создать новое мероприятие</button>
      <table>
        <thead>
          <tr>
            <th>Название</th>
            <th>Места</th>
            <th>Цена</th>
            <th>Действия</th>
          </tr>
        </thead>
        <tbody>
          {events.map((event) => (
            <tr key={event.guid}>
              <td>{event.name}</td>
              <td>{event.max_seats}</td>
              <td>{event.price}</td>
              <td>
                <button onClick={() => navigate(`/events/${event.guid}/edit`)}>Редактировать</button>
                <button onClick={() => handleDelete(event.guid)}>Удалить</button>
                <button onClick={() => navigate(`/events/${event.guid}/bookings`)}>Бронирования</button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default EventsPage;
