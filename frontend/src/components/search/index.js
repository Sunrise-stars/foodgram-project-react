import React, { useState, useEffect } from 'react';
import { useHistory } from 'react-router-dom';
import api from '../../api';
import styles from './style.module.css';

const Search = () => {
  const [searchQuery, setSearchQuery] = useState('');
  const [suggestions, setSuggestions] = useState([]);
  const history = useHistory();

  useEffect(() => {
    if (searchQuery.length > 0) {
      api.searchRecipes(searchQuery)
        .then(data => {
          setSuggestions(data.results);
        })
        .catch(err => {
          console.error(err);
        });
    } else {
      setSuggestions([]);
    }
  }, [searchQuery]);

  const handleSearchChange = (event) => {
    setSearchQuery(event.target.value);
  };

  const handleSearchSubmit = (event) => {
    event.preventDefault();
    history.push(`/search?query=${searchQuery}`);
  };

  const handleSuggestionClick = (recipeId) => {
    history.push(`/recipes/${recipeId}`);
  };

  return (
    <div className={styles.searchContainer}>
      <form onSubmit={handleSearchSubmit} className={styles.searchForm}>
        <input
          type="text"
          placeholder="Поиск рецептов..."
          value={searchQuery}
          onChange={handleSearchChange}
          className={styles.searchInput}
        />
        <button type="submit" className={styles.searchButton}>Поиск</button>
      </form>
      {suggestions.length > 0 && (
        <ul className={styles.suggestionsList}>
          {suggestions.map(suggestion => (
            <li
              key={suggestion.id}
              className={styles.suggestionItem}
              onClick={() => handleSuggestionClick(suggestion.id)}
            >
              {suggestion.name}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
};

export default Search;
