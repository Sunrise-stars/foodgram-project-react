import React, { useState, useEffect } from 'react';
import { PurchaseList, Title, Container, Main, Button } from '../../components';
import styles from './styles.module.css';
import { useRecipes } from '../../utils/index.js';
import api from '../../api';
import MetaTags from 'react-meta-tags';

const Cart = ({ updateOrders, orders }) => {
  const {
    recipes,
    setRecipes,
    handleAddToCart
  } = useRecipes();
  const [portions, setPortions] = useState({});

  // Функция для установки количества порций для каждого рецепта
  const setPortionsForRecipe = (id, value) => {
    setPortions((prevPortions) => ({
      ...prevPortions,
      [id]: value
    }));
  };

  // Функция для получения рецептов, добавленных в корзину
  const getRecipes = () => {
    api
      .getRecipes({
        page: 1,
        limit: 999,
        is_in_shopping_cart: Number(true)
      })
      .then(res => {
        const { results } = res;
        setRecipes(results);
      });
  };

  // Получаем рецепты при загрузке компонента
  useEffect(() => {
    getRecipes();
  }, []);

  // Функция для скачивания документа, учитывающего количество порций
  const downloadDocument = () => {
    const queryString = new URLSearchParams(portions).toString();
    console.log("Portions data:", queryString);
    api.downloadFile(queryString);
  };

  return (
    <Main>
      <Container className={styles.container}>
        <MetaTags>
          <title>Список покупок</title>
          <meta name="description" content="Продуктовый помощник - Список покупок" />
          <meta property="og:title" content="Список покупок" />
        </MetaTags>
        <div className={styles.cart}>
          <Title title='Список покупок' />
          <PurchaseList
            orders={recipes}
            handleRemoveFromCart={handleAddToCart}
            updateOrders={updateOrders}
            setPortions={setPortionsForRecipe}
          />
          {orders > 0 && <Button
            modifier='style_dark-blue'
            clickHandler={downloadDocument}
          >Скачать список</Button>}
        </div>
      </Container>
    </Main>
  );
};

export default Cart;
