import axios from 'axios';

// Базовый URL API, взятый из переменных окружения или по умолчанию
const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:9000';

/**
 * Получение списка мероприятий
 * @returns {Promise<Array>} Список мероприятий
 */
export const getEvents = async () => {
  const response = await axios.get(`${API_URL}/events`);
  return response.data;
};

/**
 * Создание нового мероприятия
 * @param {Object} event Данные нового мероприятия
 * @returns {Promise<Object>} Созданное мероприятие
 */
export const createEvent = async (event) => {
  const response = await axios.post(`${API_URL}/events`, event);
  return response.data;
};

/**
 * Получение данных о мероприятии
 * @param {string} guid GUID мероприятия
 * @returns {Promise<Object>} Данные мероприятия
 */
export const getEvent = async (guid) => {
  const response = await axios.get(`${API_URL}/events/${guid}`);
  return response.data;
};

/**
 * Обновление мероприятия
 * @param {string} guid GUID мероприятия
 * @param {Object} updatedEvent Обновленные данные мероприятия
 * @returns {Promise<Object>} Обновленное мероприятие
 */
export const updateEvent = async (guid, updatedEvent) => {
  const response = await axios.patch(`${API_URL}/events/${guid}`, updatedEvent);
  return response.data;
};

/**
 * Удаление мероприятия
 * @param {string} guid GUID мероприятия
 * @returns {Promise<void>}
 */
export const deleteEvent = async (guid) => {
  await axios.delete(`${API_URL}/events/${guid}`);
};

/**
 * Получение списка бронирований для мероприятия
 * @param {string} eventGuid GUID мероприятия
 * @returns {Promise<Array>} Список бронирований
 */
export const getBookings = async (eventGuid) => {
  try {
    const params = eventGuid ? { event_guid: eventGuid } : {};
    const response = await axios.get(`${API_URL}/bookings/`, { params });
    return response.data;
  } catch (error) {
    console.error("Ошибка при получении бронирований:", error);
    throw error;
  }
};

export const getPaymentFile = async (bookingGuid) => {
  try {
    const response = await axios.get(`${API_URL}/bookings/${bookingGuid}/payment-file`, { responseType: 'blob' });
    return response.data;
  } catch (error) {
    console.error("Ошибка при получении файла подтверждения оплаты:", error);
    throw error;
  }
};

export const updateBookingStatus = async (bookingGuid, verified) => {
  try {
    const response = await axios.patch(`${API_URL}/bookings/${bookingGuid}`, { verified });
    return response.data;
  } catch (error) {
    console.error("Ошибка при обновлении статуса бронирования:", error);
    throw error;
  }
};

/**
 * Подтверждение бронирования
 * @param {string} bookingGuid GUID бронирования
 * @returns {Promise<Object>} Обновленное бронирование
 */
export const verifyBooking = async (bookingGuid) => {
  const response = await axios.post(`${API_URL}/bookings/${bookingGuid}/verify`);
  return response.data;
};

/**
 * Получение списка отсутствующих для мероприятия
 * @param {string} eventGuid GUID мероприятия
 * @returns {Promise<Array>} Список отсутствующих участников
 */
export const getAbsentees = async (eventGuid) => {
  const response = await axios.get(`${API_URL}/events/${eventGuid}/absentees`);
  return response.data;
};

/**
 * Экспорт бронирований мероприятия в CSV
 * @param {string} eventGuid GUID мероприятия
 * @returns {Promise<void>} Скачивание файла CSV
 */
export const exportBookings = async (eventGuid) => {
  const response = await axios.get(`${API_URL}/events/${eventGuid}/export`, {
    responseType: 'blob',
  });

  // Создаем ссылку для скачивания
  const url = window.URL.createObjectURL(new Blob([response.data]));
  const link = document.createElement('a');
  link.href = url;
  link.setAttribute('download', `bookings_${eventGuid}.csv`);
  document.body.appendChild(link);
  link.click();
};

/**
 * Скачивание файла подтверждения оплаты
 * @param {string} bookingGuid GUID бронирования
 * @returns {Promise<void>} Скачивание файла
 */
export const downloadFile = async (bookingGuid) => {
  const response = await axios.get(`${API_URL}/bookings/${bookingGuid}/download`, {
    responseType: 'blob',
  });

  // Создаем ссылку для скачивания
  const url = window.URL.createObjectURL(new Blob([response.data]));
  const link = document.createElement('a');
  link.href = url;
  link.setAttribute('download', `payment_${bookingGuid}.pdf`);
  document.body.appendChild(link);
  link.click();
};
