import React, { useState } from 'react';
import styles from './styles.module.css';
import { LinkComponent, Icons } from '../index';

const Purchase = ({ image, name, cooking_time, id, handleRemoveFromCart, is_in_shopping_cart, updateOrders, setPortions }) => {
  const [localPortions, setLocalPortions] = useState(1);

  if (!is_in_shopping_cart) {
    return null;
  }

  const handlePortionChange = (event) => {
    const value = Math.max(1, Math.min(99, parseInt(event.target.value, 10)));
    setLocalPortions(value);
    setPortions(id, value);
  };

  const increasePortion = () => {
    const newValue = Math.min(localPortions + 1, 99);
    setLocalPortions(newValue);
    setPortions(id, newValue);
  };

  const decreasePortion = () => {
    const newValue = Math.max(localPortions - 1, 1);
    setLocalPortions(newValue);
    setPortions(id, newValue);
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
            value={localPortions}
            onChange={handlePortionChange}
            className={styles.portionInput}
          />
          <button onClick={increasePortion} className={styles.portionButton}>+</button>
        </div>
      </div>
      <a
        href="#"
        className={styles.purchaseDelete}
        onClick={() => handleRemoveFromCart({ id, toAdd: false, callback: updateOrders })}
      >
        Удалить
      </a>
    </li>
  );
};

export default Purchase;
