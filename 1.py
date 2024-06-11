import matplotlib.pyplot as plt
import networkx as nx

# Создаем граф
G = nx.DiGraph()

# Добавляем узлы и связи
G.add_edges_from([
    ("Пользователи", "Рецепты", {'relationship': 'Создает'}),
    ("Пользователи", "Избранное", {'relationship': 'Имеет в избранном'}),
    ("Пользователи", "Список покупок", {'relationship': 'Создает список покупок'}),
    ("Рецепты", "Ингредиенты рецепта", {'relationship': 'Содержит ингредиенты'}),
    ("Рецепты", "Теги рецепта", {'relationship': 'Имеет теги'}),
    ("Ингредиенты", "Ингредиенты рецепта", {'relationship': 'Используется в рецептах'}),
    ("Ингредиенты рецепта", "Рецепты", {'relationship': 'Принадлежит рецепту'}),
    ("Ингредиенты рецепта", "Ингредиенты", {'relationship': 'Состоит из ингредиента'}),
    ("Теги", "Теги рецепта", {'relationship': 'Присваивается рецептам'}),
    ("Теги рецепта", "Рецепты", {'relationship': 'Присваивается рецепту'}),
    ("Теги рецепта", "Теги", {'relationship': 'Имеет тег'}),
    ("Избранное", "Пользователи", {'relationship': 'Принадлежит пользователю'}),
    ("Избранное", "Рецепты", {'relationship': 'Содержит рецепт'}),
    ("Список покупок", "Пользователи", {'relationship': 'Принадлежит пользователю'})
])

pos = nx.spring_layout(G)

plt.figure(figsize=(12, 8))

# Рисуем узлы
nx.draw_networkx_nodes(G, pos, node_size=3000, node_color='skyblue')

# Рисуем ребра
nx.draw_networkx_edges(G, pos, arrowstyle='-|>', arrowsize=20, edge_color='black')

# Рисуем метки узлов
nx.draw_networkx_labels(G, pos, font_size=12, font_color='black', font_weight='bold')

# Рисуем метки ребер
edge_labels = {(u, v): d['relationship'] for u, v, d in G.edges(data=True)}
nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=10, font_color='red')

plt.title('ER-диаграмма Базы Данных', fontsize=16)
plt.axis('off')

# Сохраняем график
plt.savefig("ER_Diagram.png")
plt.show()
