import { Card, Title, Pagination, CardList, Container, Main, CheckboxGroup, Search } from '../../components';
import styles from './styles.module.css';  // Убедитесь, что путь верный
import { useRecipes } from '../../utils/index.js';
import { useEffect, useState } from 'react';
import api from '../../api';
import MetaTags from 'react-meta-tags';

const HomePage = ({ updateOrders }) => {
  const {
    recipes,
    setRecipes,
    recipesCount,
    setRecipesCount,
    recipesPage,
    setRecipesPage,
    tagsValue,
    setTagsValue,
    handleTagsChange,
    handleLike,
    handleAddToCart
  } = useRecipes();

  const [searchQuery, setSearchQuery] = useState('');

  const getRecipes = ({ page = 1, tags }) => {
    api
      .getRecipes({ page, tags })
      .then(res => {
        const { results, count } = res;
        setRecipes(results);
        setRecipesCount(count);
      });
  };

  useEffect(() => {
    getRecipes({ page: recipesPage, tags: tagsValue });
  }, [recipesPage, tagsValue]);

  useEffect(() => {
    api.getTags()
      .then(tags => {
        setTagsValue(tags.map(tag => ({ ...tag, value: true })));
      });
  }, []);

  const filteredRecipes = recipes
    .map(recipe => ({
      ...recipe,
      highlighted: recipe.name.toLowerCase().includes(searchQuery.toLowerCase())
    }))
    .sort((a, b) => b.highlighted - a.highlighted);

  return (
    <Main>
      <Container>
        <MetaTags>
          <title>Рецепты</title>
          <meta name="description" content="Продуктовый помощник - Рецепты" />
          <meta property="og:title" content="Рецепты" />
        </MetaTags>
        <div className={styles.title}>
          <Title title='Рецепты' />
          <CheckboxGroup
            values={tagsValue}
            handleChange={value => {
              setRecipesPage(1);
              handleTagsChange(value);
            }}
          />
          <Search setSearchQuery={setSearchQuery} />
        </div>
        <CardList>
          {filteredRecipes.map(card => (
            <Card
              {...card}
              key={card.id}
              updateOrders={updateOrders}
              handleLike={handleLike}
              handleAddToCart={handleAddToCart}
              searchQuery={searchQuery}
            />
          ))}
        </CardList>
        <Pagination
          count={recipesCount}
          limit={6}
          page={recipesPage}
          onPageChange={page => setRecipesPage(page)}
        />
      </Container>
    </Main>
  );
};

export default HomePage;
