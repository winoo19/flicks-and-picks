import { Fragment, useState, useEffect } from 'react'
import { useOutletContext } from "react-router-dom";
import './index.css'
import Divider from '@mui/material/Divider';
import FilmPreview from './FilmPreview';

const INITIAL_PAGE = 1;
const LAST_PAGE = 20;

function ListPage({ filmList, currentPage, setCurrentPage, isLogged }) {
  return <>
    <div className="container">
      {/* <h1>Nuestras películas</h1> */}
      {/* <PageFilter currentPage={currentPage} setCurrentPage={setCurrentPage} /> */}
      <FilmList filmList={filmList} isLogged={isLogged} />
    </div>
  </>
}

function PageFilter({ currentPage, setCurrentPage }) {

  function changePage(page) {
    page = Math.max(1, page);
    page = Math.min(page, 20);
    setCurrentPage(page);
  }

  return <>
    <div className="buttons">
      <button onClick={() => changePage(currentPage - 1)} disabled={currentPage == INITIAL_PAGE}>&lt;</button>
      <input type="number" value={currentPage} onChange={(e) => changePage(e.target.value)} />
      <button onClick={() => changePage(currentPage + 1)} disabled={currentPage == LAST_PAGE}>&gt;</button>
    </div>
  </>
}

function FilmList({ filmList, isLogged }) {
  return (
    <div>
      {filmList.map((film, index) => (
        <Fragment key={film.id}>
          <FilmPreview film={film} isLogged={isLogged} />
          {index < filmList.length - 1 && <Divider variant="middle" />}
        </Fragment>
      ))}
    </div>
  );
}

function App() {
  const [currentPage, setCurrentPage] = useState(1);
  const [isLogged, filmList, setFilmList] = useOutletContext();

  useEffect(() => {
    const fetchFilms = async () => {
      const body = JSON.stringify({
        "film_name": null,
        "director_name": null,
        "actor_name": null,
        "genre": null,
        "description": null,
        "min_release": null,
        "max_release": null,
        "min_rating": null,
        "max_rating": null
      });
      try {
        // const response = await fetch("../films.json");
        const response = await fetch("http://127.0.0.1:8000/films/", {
          method: "post",
          headers: {
            "Content-Type": "application/json"
          },
          credentials: "include",
          body: body
        });
        console.log(response);
        if (!response.ok) {
          throw new Error("Couldn't load film list");
        }
        const data = await response.json();
        setFilmList(data.films);
      } catch (error) {
        console.error("Error loading films...", error);
      }
    };
    fetchFilms();
  }, []);


  return (
    <ListPage filmList={filmList} currentPage={currentPage} setCurrentPage={setCurrentPage} isLogged={isLogged} />
  )
}

export default App
