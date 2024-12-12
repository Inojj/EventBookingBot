import React, { useState, useEffect } from "react";
import axios from "../axiosSetup"; // Используем настроенный axios
import { useNavigate, useParams } from "react-router-dom";

function EventFormPage() {
  const { eventGuid } = useParams();
  const navigate = useNavigate();
  const [event, setEvent] = useState({
    name: "",
    text: "",
    max_seats: 0,
    price: 0,
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    if (eventGuid) {
      fetchEvent(eventGuid);
    }
  }, [eventGuid]);

  const fetchEvent = async (guid) => {
    setLoading(true);
    try {
      const response = await axios.get(`/events/${guid}`);
      setEvent(response.data);
    } catch (error) {
      console.error("Ошибка при загрузке мероприятия:", error);
      setError("Не удалось загрузить данные мероприятия.");
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      if (eventGuid) {
        // Обновление существующего мероприятия
        await axios.patch(`/events/${eventGuid}`, event);
      } else {
        // Создание нового мероприятия
        await axios.post("/events", event);
      }
      navigate("/events");
    } catch (error) {
      console.error("Ошибка при сохранении мероприятия:", error);
      setError("Не удалось сохранить мероприятие.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <h1>{eventGuid ? "Редактировать мероприятие" : "Создать мероприятие"}</h1>
      {error && <p style={{ color: "red" }}>{error}</p>}
      <form onSubmit={handleSubmit}>
        <label>Название:</label>
        <input
          type="text"
          value={event.name}
          onChange={(e) => setEvent({ ...event, name: e.target.value })}
          required
          disabled={loading}
        />
        <label>Описание:</label>
        <textarea
          value={event.text}
          onChange={(e) => setEvent({ ...event, text: e.target.value })}
          disabled={loading}
        />
        <label>Максимум мест:</label>
        <input
          type="number"
          value={event.max_seats}
          onChange={(e) => setEvent({ ...event, max_seats: +e.target.value })}
          required
          disabled={loading}
        />
        <label>Цена за место:</label>
        <input
          type="number"
          value={event.price}
          onChange={(e) => setEvent({ ...event, price: +e.target.value })}
          required
          disabled={loading}
        />
        <button type="submit" disabled={loading}>
          {loading ? "Сохранение..." : "Сохранить"}
        </button>
      </form>
    </div>
  );
}

export default EventFormPage;
