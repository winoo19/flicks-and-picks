import Header from "./Header.jsx";
import Footer from "./Footer.jsx";
import {Outlet} from "react-router-dom"
import { useState } from "react";

export default function App() {
    const [isLogged, setIsLogged] = useState(false);
    const [filmList, setFilmList] = useState([]);
    const [userId, setUserId] = useState(null);
    return <>
        <Header isLogged={isLogged} setIsLogged={setIsLogged} setFilmList={setFilmList} userId={userId} setUserId={setUserId}/>
        <Outlet context={ [isLogged , filmList, setFilmList] }/>
        <Footer />
    </>
} 