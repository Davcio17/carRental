import React, { useState, useEffect, useCallback } from 'react';
import { catalogApi, bookingApi } from './api';
import './App.css';

function App() {
    const [cars, setCars] = useState([]);
    const [view, setView] = useState('list');
    const [selectedCar, setSelectedCar] = useState(null);

    const [newCarForm, setNewCarForm] = useState({
        brand: '', model: '', year: '', version: '', capacity: '',
        power: '', fuel: '', vin: '', price_per_day: '', regNumber: ''
    });

    const [bookingForm, setBookingForm] = useState({
        customer_name: '', rental_date: Date.now() ,return_date: Date.now(), phone: 0
    });

    const fetchCars = useCallback(async () => {
        try {
            const res = await catalogApi.get('/cars');
            setCars(res.data);
        } catch (err) {
            console.error("Błąd pobierania danych:", err);
        }
    }, []);

    useEffect(() => {
        fetchCars();
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, []);

    const handleRent = async (e) => {
        e.preventDefault();
        try {
            await bookingApi.post('/rentals', {
                car_id: selectedCar.id,
                customer_name: bookingForm.customer_name,
                phone: bookingForm.phone,
                price: 0,
                rental_date: new Date(bookingForm.rental_date).toISOString(),
                return_date: new Date(bookingForm.return_date).toISOString()
            });
            console.log(selectedCar.id)
            console.log(bookingForm)
            alert(`Zarezerwowano auto!`);
            setSelectedCar(null);
            fetchCars();
        } catch (err) {
            alert("Błąd podczas rezerwacji."+err);
        }
    };

    const handleAddCar = async (e) => {
        e.preventDefault();
        try {
            const payload = {
                ...newCarForm,
                year: parseInt(newCarForm.year),
                power: parseInt(newCarForm.power),
                price_per_day: parseFloat(newCarForm.price_per_day)
            };
            await catalogApi.post('/cars', payload);
            alert("Auto dodane!");
            fetchCars();
            setView('list');
        } catch (err) {
            alert("Błąd dodawania auta."+err);
        }
    };

    return (
        <div className="App">
            <nav className="navbar">
                <h1 onClick={() => {setView('list'); setSelectedCar(null);}} style={{cursor: 'pointer'}}>
                    CarRentAll
                </h1>
                <button className="btn-add" onClick={() => setView('add-car')}>+ Dodaj nowe auto</button>
            </nav>

            <div className="container">
                {view === 'add-car' && (
                    <div className="form-card">
                        <h3>Dodaj samochód do floty</h3>
                        <form onSubmit={handleAddCar}>
                            <input placeholder="Marka" required onChange={e => setNewCarForm({...newCarForm, brand: e.target.value})} />
                            <input placeholder="Model" required onChange={e => setNewCarForm({...newCarForm, model: e.target.value})} />
                            <input type="number" placeholder="Rok produkcji" required onChange={e => setNewCarForm({...newCarForm, year: e.target.value})} />
                            <input placeholder="Wersja" required onChange={e => setNewCarForm({...newCarForm, version: e.target.value})} />
                            <input placeholder="Pojemność silnika" required onChange={e => setNewCarForm({...newCarForm, capacity: e.target.value})}/>
                            <input type="number" placeholder="Moc silnika" required onChange={e => setNewCarForm({...newCarForm, power: e.target.value})} />
                            <input placeholder="Rodzaj paliwa" required onChange={e => setNewCarForm({...newCarForm, fuel: e.target.value})} />
                            <input placeholder="VIN" required onChange={e => setNewCarForm({...newCarForm, vin: e.target.value})} />
                            <input type="number" step="0.01" placeholder="Cena za dobę" required onChange={e => setNewCarForm({...newCarForm, price_per_day: e.target.value})} />
                            <input placeholder="Numer rejestracyjny" required onChange={e => setNewCarForm({...newCarForm, regNumber: e.target.value})} />
                            <button type="submit" className="btn-confirm">Zapisz auto</button>
                        </form>
                    </div>
                )}

                {view === 'list' && !selectedCar && (
                    <div className="car-grid">
                        {cars.map(car => (
                            <div key={car.id} className="car-card">
                                <h4>{car.brand} {car.model}</h4>
                                <p>Rok: {car.year} | {car.fuel}</p>
                                <p className="price">{car.price_per_day} PLN / doba</p>
                                {car.available ? (
                                    <button className="btn-rent" onClick={() => setSelectedCar(car)}>Wypożycz</button>
                                ) : (
                                    <button disabled className="btn-disabled">Niedostępne</button>
                                )}
                            </div>
                        ))}
                    </div>
                )}

                {selectedCar && (
                    <div className="form-card">
                        <h3>Wypożyczasz: {selectedCar.brand} {selectedCar.model}</h3>
                        <form onSubmit={handleRent}>
                            <input placeholder="Imię i nazwisko" required onChange={e => setBookingForm({...bookingForm, customer_name: e.target.value})} />
                            <label>Data wypożyczenia:</label>
                            <input type="date" required onChange={e => setBookingForm({...bookingForm, rental_date: e.target.value})} />
                            <label>Data zwrotu: </label>
                            <input type="date" required onChange={e => setBookingForm({...bookingForm, return_date: e.target.value})} />
                            <input type="tel" placeholder="Numer telefonu" required onChange={e => setBookingForm({...bookingForm, phone: e.target.value})} />
                            <div className="form-actions">
                                <button type="submit" className="btn-confirm">Zarezerwuj</button>
                                <button type="button" className="btn-cancel" onClick={() => setSelectedCar(null)}>Anuluj</button>
                            </div>
                        </form>
                    </div>
                )}
            </div>
        </div>
    );
}

export default App;