import { useEffect, useState } from "react";
import axios from "axios";
import { FaDownload, FaTrash, FaRoad, FaHome, FaCity, FaGlobe, FaExternalLinkAlt,FaSpinner  } from "react-icons/fa";

const App = () => {
    const [street, setStreet] = useState("");
    const [houseNumber, setHouseNumber] = useState("");
    const [city, setCity] = useState("");
    const [country, setCountry] = useState("");
    const [poem, setPoem] = useState("");
    const [wikiLink, setWikiLink] = useState(""); 
    const [addresses, setAddresses] = useState([]);
    const [loading, setLoading] = useState(false);
    const [models, setModels] = useState([]);
    const [activeModel, setActiveModel] = useState(null);
    const [switchingModel, setSwitchingModel] = useState(false);

    const fetchAddresses = async () => {
        try {
            const response = await axios.get("http://localhost:8000/addresses/");
            setAddresses(response.data);
        } catch (error) {
            console.error("Fehler beim Abrufen der Adressen!", error);
        }
    };

    const fetchModels = async () => {
        try {
            const response = await axios.get("http://localhost:8000/models/");
            setModels(response.data);
            if (response.data.length > 0) {
                setActiveModel(response.data[0].name); 
            }
        } catch (error) {
            console.error("Fehler beim Abrufen der Modelle!", error);
        }
    };

    useEffect(() => {
        fetchAddresses();
        fetchModels();
    }, []);

    const handleModelSwitch = async (newModel) => {
        if (activeModel === newModel || switchingModel) return;
        
        setSwitchingModel(true);
        try {
            await axios.post("http://localhost:8000/switch_model/", { model_name: newModel });
            setActiveModel(newModel);
        } catch (error) {
            console.error("Fehler beim Wechseln des Modells!", error);
        } finally {
            setSwitchingModel(false); 
        }

    };

 
    const fetchWikipediaLink = async (city) => {
        try {
            const response = await axios.get(`http://localhost:8000/wikipedia/${city}`);
            if (response.data.link) {
                setWikiLink(response.data.link);
            } else {
                setWikiLink("");
            }
        } catch (error) {
            console.error("Fehler beim Abrufen des Wikipedia-Links!", error);
            setWikiLink("");
        }
    };

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

            setPoem(response.data.poem);
            fetchWikipediaLink(city); 
            alert("Adresse erfolgreich gespeichert!");
            fetchAddresses();
        } catch (error) {
            alert(error.response?.data?.detail || "Fehler beim Speichern der Adresse!");
        }
        setLoading(false);
    };

    const handleLoadAddress = async (address) => {
        setStreet(address.street);
        setHouseNumber(address.house_number);
        setCity(address.city);
        setCountry(address.country);

        try {
            const response = await axios.get(`http://localhost:8000/address/${address.city}`);
            setPoem(response.data.poem);
            fetchWikipediaLink(address.city);  
        } catch (error) {
            alert("Fehler beim Laden des Gedichts!");
        }
    };

    const handleDeleteAddress = async (id) => {
        try {
            await axios.delete(`http://localhost:8000/address/${id}`);
            setAddresses(addresses.filter(address => address.id !== id));
        } catch (error) {
            alert("Fehler beim Löschen der Adresse!");
        }
    };

    const handleRegeneratePoem = async () => {
        if (!city) return;
        setLoading(true);
        try {
            const response = await axios.put(`http://localhost:8000/address/${city}`);
            setPoem(response.data.updated_poem);
        } catch (error) {
            alert("Fehler beim erneuten Generieren des Gedichts!");
        }
        setLoading(false);
    };

    return (
        <div className="flex flex-col items-center justify-center min-h-screen bg-gray-900 text-white p-6"
             style={{ backgroundImage: "url('https://source.unsplash.com/1600x900/?city,night')", backgroundSize: 'cover', backgroundPosition: 'center' }}>
            
            {switchingModel && (
                <div className="absolute inset-0 flex items-center justify-center bg-gray-900 bg-opacity-70 z-50">
                    <div className="flex flex-col items-center">
                        <FaSpinner className="animate-spin text-white text-4xl" />
                        <span className="mt-2 text-white text-lg">Wechsle Modell...</span>
                    </div>
                </div>
            )}
            <h1 className="text-4xl font-bold mb-6 bg-gray-800 p-3 rounded-lg shadow-md">Städtereim-Generator 4.0</h1>

            <div className="flex items-center mb-6 bg-gray-800 p-2 rounded-full shadow-md">
                {models.map((model) => (
                    <button
                        key={model.name}
                        className={`px-4 py-2 mx-2 rounded-full transition-all duration-300 ${
                            activeModel === model.name ? "bg-green-500 text-white" : "bg-blue-500 text-black  hover:bg-blue-600 "
                        }`}
                        onClick={() => handleModelSwitch(model.name)}
                        disabled={switchingModel}
                    >
                        {model.name}
                    </button>
                ))}
            </div>
            <div className="grid grid-cols-2 gap-8 w-full max-w-6xl">
                <div className="bg-gray-800 shadow-lg rounded-lg p-6 backdrop-blur-lg bg-opacity-80">
                    <h2 className="text-xl font-semibold mb-4">Adresse eingeben</h2>
                    <div className="grid grid-cols-2 gap-2">
                        <div className="flex items-center bg-gray-700 p-2 rounded">
                            <FaRoad className="text-white mr-2" />
                            <input type="text" placeholder="Straße" value={street} onChange={(e) => setStreet(e.target.value)} className="bg-transparent outline-none w-full text-white" />
                        </div>
                        <div className="flex items-center bg-gray-700 p-2 rounded">
                            <FaHome className="text-white mr-2" />
                            <input type="text" placeholder="Hausnummer" value={houseNumber} onChange={(e) => setHouseNumber(e.target.value)} className="bg-transparent outline-none w-full text-white" />
                        </div>
                    </div>
                    <div className="grid grid-cols-2 gap-2 mt-2">
                        <div className="flex items-center bg-gray-700 p-2 rounded">
                            <FaCity className="text-white mr-2" />
                            <input type="text" placeholder="Wohnort" value={city} onChange={(e) => setCity(e.target.value)} className="bg-transparent outline-none w-full text-white" />
                        </div>
                        <div className="flex items-center bg-gray-700 p-2 rounded">
                            <FaGlobe className="text-white mr-2" />
                            <input type="text" placeholder="Land" value={country} onChange={(e) => setCountry(e.target.value)} className="bg-transparent outline-none w-full text-white" />
                        </div>
                    </div>
                    <button onClick={handleSaveAddress} disabled={loading} className={`w-full p-2 mt-4 rounded ${loading ? "bg-gray-500" : "bg-blue-500 hover:bg-blue-600"} bg-blue-500 hover:bg-blue-600 text-white shadow-md`}>
                        Adresse speichern
                    </button>
                    <h2 className="text-xl font-semibold mt-6">Gedicht</h2>
                    <textarea value={poem} readOnly className="w-full border p-2 mt-2 h-32 bg-gray-700 rounded text-white"></textarea>
                    <button onClick={handleRegeneratePoem} disabled={loading} className={`w-full p-2 mt-4 rounded ${loading ? "bg-gray-500" : "bg-green-500 hover:bg-green-600"} text-white shadow-md flex items-center justify-center`}>
                        <FaSpinner className="mr-2" /> {loading ? "Generiert..." : "Neu generieren"}
                    </button>    
                    {wikiLink && (
                        <a href={wikiLink} target="_blank" rel="noopener noreferrer" className="block text-blue-400 hover:text-blue-500 mt-4 flex items-center">
                            <FaExternalLinkAlt className="mr-2" /> Wikipedia: {city}
                        </a>
                    )}
                </div>

                <div className="bg-gray-800 shadow-lg rounded-lg p-6 backdrop-blur-lg bg-opacity-80">
                    <h2 className="text-xl font-semibold mb-4">Gespeicherte Adressen</h2>
                    <table className="w-full border-collapse border border-gray-600">
                        <thead>
                            <tr className="bg-gray-700">
                                <th className="border p-2">Straße</th>
                                <th className="border p-2">Hausnr.</th>
                                <th className="border p-2">Wohnort</th>
                                <th className="border p-2">Land</th>
                                <th className="border p-2">Laden</th>
                                <th className="border p-2">Entfernen</th>
                            </tr>
                        </thead>
                        <tbody>
                            {addresses.map((address) => (
                                <tr key={address.id} className="text-center">
                                    <td className="border p-2">{address.street}</td>
                                    <td className="border p-2">{address.house_number}</td>
                                    <td className="border p-2">{address.city}</td>
                                    <td className="border p-2">{address.country}</td>
                                    <td className="border p-2">
                                        <button onClick={() => handleLoadAddress(address)} className="text-blue-400 hover:text-blue-500">
                                            <FaDownload size={18} />
                                        </button>
                                    </td>
                                    <td className="border p-2">
                                        <button onClick={() => handleDeleteAddress(address.id)} className="text-red-400 hover:text-red-500">
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
