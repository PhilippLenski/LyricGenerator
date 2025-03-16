import { useEffect, useState } from "react";
import axios from "axios";
import { FaDownload, FaTrash } from "react-icons/fa"; // 📌 Icons für Laden & Entfernen

const App = () => {
    const [street, setStreet] = useState("");
    const [houseNumber, setHouseNumber] = useState("");
    const [city, setCity] = useState("");
    const [country, setCountry] = useState("");
    const [poem, setPoem] = useState("");
    const [addresses, setAddresses] = useState([]);
    const [loading, setLoading] = useState(false); // 🔹 Blockiert Buttons während einer Aktion

    // 📌 Adressen von der API abrufen (wird beim Laden und nach Änderungen aufgerufen)
    const fetchAddresses = async () => {
        try {
            const response = await axios.get("http://localhost:8000/addresses/");
            setAddresses(response.data);
        } catch (error) {
            console.error("Fehler beim Abrufen der Adressen!", error);
        }
    };

    // 📌 API beim ersten Laden abrufen
    useEffect(() => {
        fetchAddresses();
    }, []);

    // 📌 Adresse speichern (und Gedicht generieren)
    const handleSaveAddress = async () => {
        if (!street || !houseNumber || !city || !country) {
            alert("Bitte alle Felder ausfüllen!");
            return;
        }

        setLoading(true);
        try {
            const response = await axios.post("http://localhost:8000/address/", {
                street,
                house_number: houseNumber,
                city,
                country,
            });

            setPoem(response.data.poem); // Gedicht setzen
            alert("Adresse erfolgreich gespeichert!");
            fetchAddresses(); // Tabelle aktualisieren
        } catch (error) {
            alert(error.response?.data?.detail || "Fehler beim Speichern der Adresse!");
        }
        setLoading(false);
    };

    // 📌 Adresse & Gedicht in Eingabefelder laden
    const handleLoadAddress = async (address) => {
        setStreet(address.street);
        setHouseNumber(address.house_number);
        setCity(address.city);
        setCountry(address.country);

        try {
            const response = await axios.get(`http://localhost:8000/address/${address.city}`);
            setPoem(response.data.poem);
        } catch (error) {
            alert("Fehler beim Laden des Gedichts!");
        }
    };

    // 📌 Gedicht für eine Stadt neu generieren (PUT-Request)
    const handleRegeneratePoem = async () => {
        if (!city) {
            alert("Bitte gib eine Stadt ein!");
            return;
        }

        setLoading(true);
        try {
            const response = await axios.put(`http://localhost:8000/address/${city}`);
            setPoem(response.data.updated_poem);
            fetchAddresses(); // Tabelle aktualisieren
        } catch (error) {
            alert("Fehler beim Neugenerieren des Gedichts!");
        }
        setLoading(false);
    };

    // 📌 Adresse löschen
    const handleDeleteAddress = async (city) => {
        if (!window.confirm(`Soll die Adresse für ${city} wirklich gelöscht werden?`)) return;

        setLoading(true);
        try {
            await axios.delete(`http://localhost:8000/address/${city}`);
            fetchAddresses(); // Tabelle aktualisieren
        } catch (error) {
            alert("Fehler beim Löschen der Adresse!");
        }
        setLoading(false);
    };

    return (
        <div className="flex flex-col items-center justify-center min-h-screen bg-gray-100 p-6">
            <h1 className="text-3xl font-bold mb-6">Städtereim-Generator</h1>

            {/* 📌 Grid-System für Layout: Eingabe links, Tabelle rechts */}
            <div className="grid grid-cols-2 gap-8 w-full max-w-6xl">
                
                {/* 📌 Linke Seite: Eingabeformular + Gedicht */}
                <div className="bg-white shadow-md rounded-lg p-6">
                    <h2 className="text-xl font-semibold mb-4">Adresse eingeben</h2>

                    {/* 📌 Adress-Eingabeform genau wie gewünscht angeordnet */}
                    <div className="grid grid-cols-2 gap-2">
                        <input
                            type="text"
                            placeholder="Straße"
                            value={street}
                            onChange={(e) => setStreet(e.target.value)}
                            className="border p-2 rounded"
                        />
                        <input
                            type="text"
                            placeholder="Hausnummer"
                            value={houseNumber}
                            onChange={(e) => setHouseNumber(e.target.value)}
                            className="border p-2 rounded"
                        />
                    </div>
                    <div className="grid grid-cols-2 gap-2">
                    <input
                        type="text"
                        placeholder="Wohnort"
                        value={city}
                        onChange={(e) => setCity(e.target.value)}
                        className="border p-2 rounded w-full mt-2"
                    />
                    <input
                        type="text"
                        placeholder="Land"
                        value={country}
                        onChange={(e) => setCountry(e.target.value)}
                        className="border p-2 rounded w-full mt-2"
                    />
                    </div>
                    <div className="grid grid-cols-1 gap-1">
                    <button
                        onClick={handleSaveAddress}
                        className={`w-full p-2 mt-4 rounded text-white ${
                            loading ? "bg-gray-400 cursor-not-allowed" : "bg-blue-500 hover:bg-blue-600"
                        }`}
                        disabled={loading}
                    >
                        {loading ? "Speichern..." : "Adresse speichern"}
                    </button>
                    </div>
                    <div className="grid grid-cols-1 gap-1">    
                    <h2 className="text-xl font-semibold mt-6">Gedicht</h2>
                    <textarea
                        value={poem}
                        readOnly
                        className="w-full border p-2 mt-2 h-32 bg-gray-100 rounded"
                    ></textarea>
                    </div>
                    <div className="grid grid-cols-1 gap-1">    
                    <button
                        onClick={handleRegeneratePoem}
                        className={`w-full p-2 mt-2 rounded text-white ${
                            loading ? "bg-gray-400 cursor-not-allowed" : "bg-green-500 hover:bg-green-600"
                        }`}
                        disabled={loading}
                    >
                        {loading ? "Generiert..." : "Neu generieren"}
                    </button>
                    </div>
                </div>

                {/* 📌 Rechte Seite: Tabelle mit Adressen */}
                <div className="bg-white shadow-md rounded-lg p-6">
                    <h2 className="text-xl font-semibold mb-4">Gespeicherte Adressen</h2>
                    <table className="w-full border-collapse border border-gray-300">
                        <thead>
                            <tr className="bg-gray-200">
                                <th className="border p-2">Wohnort</th>
                                <th className="border p-2">Laden</th>
                                <th className="border p-2">Entfernen</th>
                            </tr>
                        </thead>
                        <tbody>
                            {addresses.map((address) => (
                                <tr key={address.id} className="text-center">
                                    <td className="border p-2">{address.city}</td>
                                    <td className="border p-2">
                                        <button onClick={() => handleLoadAddress(address)} className="text-blue-500 hover:text-blue-700">
                                            <FaDownload size={18} />
                                        </button>
                                    </td>
                                    <td className="border p-2">
                                        <button onClick={() => handleDeleteAddress(address.city)} className="text-red-500 hover:text-red-700">
                                            <FaTrash size={18} />
                                        </button>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    );
};

export default App;
