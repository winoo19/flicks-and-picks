import Header from "./Header.jsx";
import Footer from "./Footer.jsx";
import { Outlet } from "react-router-dom"
import { useState } from "react";

export default function App() {
    const [filmList, setFilmList] = useState([]);

    return <>
        <Header setFilmList={setFilmList} />
        <Outlet context={[filmList, setFilmList]} />
        <Footer />
    </>
}