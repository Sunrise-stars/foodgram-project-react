import React, { useState, useEffect } from 'react';
import styles from './style.module.css';

const Search = ({ setSearchQuery }) => {
  const [query, setQuery] = useState('');

  useEffect(() => {
    setSearchQuery(query);
  }, [query, setSearchQuery]);

  const handleChange = (event) => {
    setQuery(event.target.value);
  };

  const handleSubmit = (event) => {
    event.preventDefault();
  };

  return (
    <div className={styles.searchContainer}>
      <form onSubmit={handleSubmit} className={styles.searchForm}>
        <input
          type="text"
          placeholder="Поиск рецептов..."
          value={query}
          onChange={handleChange}
          className={styles.searchInput}
        />
        <button type="submit" className={styles.searchButton}>Поиск</button>
      </form>
    </div>
  );
};

export default Search;
