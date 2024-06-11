// SearchResults/index.js
import React, { useState, useEffect, useContext } from 'react';
import { useLocation } from 'react-router-dom';
import api from '../../api';
import styles from './style.module.css';
import Card from '../../components/card'; // Обновленный путь
import { AuthContext } from '../../contexts';
import Pagination from '../../components/pagination';

const SearchResults = () => {
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(true);
  const [currentPage, setCurrentPage] = useState(1);
  const [resultsPerPage] = useState(6); // Количество рецептов на странице
  const location = useLocation();
  const authContext = useContext(AuthContext);

  useEffect(() => {
    const query = new URLSearchParams(location.search).get('query');
    if (query) {
      api.searchRecipes(query)
        .then((data) => {
          setResults(data.results);
          setLoading(false);
        })
        .catch((err) => {
          console.error(err);
          setLoading(false);
        });
    }
  }, [location.search]);

  // Получаем текущие рецепты для отображения на странице
  const indexOfLastResult = currentPage * resultsPerPage;
  const indexOfFirstResult = indexOfLastResult - resultsPerPage;
  const currentResults = results.slice(indexOfFirstResult, indexOfLastResult);

  // Изменение страницы
  const paginate = (pageNumber) => setCurrentPage(pageNumber);

  return (
    <div className={styles.results}>
      {loading ? (
        <p>Loading...</p>
      ) : (
        currentResults.length > 0 ? (
          <>
            <div className={styles.cardGrid}>
              {currentResults.map((recipe) => (
                <Card
                  key={recipe.id}
                  id={recipe.id}
                  name={recipe.name}
                  image={recipe.image}
                  is_favorited={recipe.is_favorited}
                  is_in_shopping_cart={recipe.is_in_shopping_cart}
                  tags={recipe.tags}
                  cooking_time={recipe.cooking_time}
                  author={recipe.author}
                  handleLike={(data) => {
                    api.toggleFavorite(data.id, data.toLike)
                      .then(() => {
                        setResults((prevResults) =>
                          prevResults.map((r) =>
                            r.id === data.id
                              ? { ...r, is_favorited: !!data.toLike }
                              : r
                          )
                        );
                      })
                      .catch((err) => console.error(err));
                  }}
                  handleAddToCart={(data) => {
                    api.toggleCart(data.id, data.toAdd)
                      .then(() => {
                        setResults((prevResults) =>
                          prevResults.map((r) =>
                            r.id === data.id
                              ? { ...r, is_in_shopping_cart: !!data.toAdd }
                              : r
                          )
                        );
                        if (data.callback) data.callback();
                      })
                      .catch((err) => console.error(err));
                  }}
                  updateOrders={() => {}}
                />
              ))}
            </div>
            <Pagination
              resultsPerPage={resultsPerPage}
              totalResults={results.length}
              paginate={paginate}
            />
          </>
        ) : (
          <p>No results found</p>
        )
      )}
    </div>
  );
};

export default SearchResults;
