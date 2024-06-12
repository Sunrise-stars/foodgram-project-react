import React, { useState } from 'react';
import styles from './styles.module.css';
import cn from 'classnames';
import { LinkComponent, Icons } from '../index';

const Purchase = ({ image, name, cooking_time, id, handleRemoveFromCart, is_in_shopping_cart, updateOrders }) => {
  const [portions, setPortions] = useState(1); // Состояние для хранения количества порций

  if (!is_in_shopping_cart) {
    return null;
  }

  const handlePortionChange = (event) => {
    setPortions(event.target.value);
  };

  const increasePortion = () => {
    setPortions((prevPortions) => Math.min(prevPortions + 1, 99));
  };

  const decreasePortion = () => {
    setPortions((prevPortions) => Math.max(prevPortions - 1, 1));
  };

  return (
    <li className={styles.purchase}>
      <div className={styles.purchaseContent}>
        <div
          alt={name}
          className={styles.purchaseImage}
          style={{
            backgroundImage: `url(${image})`
          }}
        />
        <h3 className={styles.purchaseTitle}>
          <LinkComponent className={styles.recipeLink} title={name} href={`/recipes/${id}`} />
        </h3>
        <p className={styles.purchaseText}>
          <Icons.ClockIcon />{cooking_time} мин.
        </p>
        <div className={styles.portionSelector}>
          <button onClick={decreasePortion} className={styles.portionButton}>-</button>
          <input
            type="number"
            id={`portion-${id}`}
            min="1"
            value={portions}
            onChange={handlePortionChange}
            className={styles.portionInput}
          />
          <button onClick={increasePortion} className={styles.portionButton}>+</button>
        </div>
      </div>
      <a
        href="#"
        className={styles.purchaseDelete}
        onClick={_ => handleRemoveFromCart({ id, toAdd: false, callback: updateOrders })}
      >
        Удалить
      </a>
    </li>
  );
};

export default Purchase;
