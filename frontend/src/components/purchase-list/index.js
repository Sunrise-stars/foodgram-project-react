import styles from './styles.module.css';
import cn from 'classnames';
import { Purchase } from '../index';

const PurchaseList = ({ orders, handleRemoveFromCart, updateOrders, setPortions }) => (
  <ul className={styles.list}>
    {orders.map((order) => (
      <Purchase
        key={order.id}
        {...order}
        handleRemoveFromCart={handleRemoveFromCart}
        updateOrders={updateOrders}
        setPortions={setPortions}
      />
    ))}
  </ul>
);

export default PurchaseList;