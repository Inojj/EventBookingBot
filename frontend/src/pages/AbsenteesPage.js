import React, { useEffect, useState } from 'react';
import { getAbsentees } from '../api';
import { useParams } from 'react-router-dom';

function AbsenteesPage() {
  const { eventGuid } = useParams();
  const [absentees, setAbsentees] = useState([]);

  useEffect(() => {
    fetchAbsentees();
  }, []);

  const fetchAbsentees = async () => {
    const data = await getAbsentees(eventGuid);
    setAbsentees(data);
  };

  return (
    <div>
      <h1>Отсутствующие</h1>
      <table>
        <thead>
          <tr>
            <th>Имя</th>
            <th>Телефон</th>
            <th>Места</th>
            <th>Сумма</th>
          </tr>
        </thead>
        <tbody>
          {absentees.map((absentee) => (
            <tr key={absentee.guid}>
              <td>{absentee.user_nickname}</td>
              <td>{absentee.user_phone}</td>
              <td>{absentee.count_seats}</td>
              <td>{absentee.total_cash}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default AbsenteesPage;
