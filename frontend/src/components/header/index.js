import React from 'react';
import styles from './style.module.css';
import { Nav, AccountMenu } from '../index.js';
import Container from '../container';
import Search from '../search/index'; // Импортируем компонент поиска

const Header = ({ loggedIn, onSignOut, orders }) => {
  return (
    <header className={styles.header}>
      <Container>
        <div className={styles.headerContent}>
          <Nav loggedIn={loggedIn} orders={orders} />
          <div className={styles.searchAndAccount}>
            <Search /> {/* Добавляем компонент поиска */}
            <AccountMenu onSignOut={onSignOut} />
          </div>
        </div>
      </Container>
    </header>
  );
};

export default Header;
