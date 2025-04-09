tours = [
    {"id": 1, "name": "Тур до Карпат", "description": "3 дні в горах", "price": 2500},
    {"id": 2, "name": "Вікенд у Львові", "description": "2 дні у старовинному місті", "price": 1800},
    {"id": 3, "name": "Київ історичний", "description": "Оглядові екскурсії", "price": 1500}
]

def get_catalog():
    return tours

def get_item_by_id(item_id):
    for item in tours:
        if item["id"] == item_id:
            return item
    return None
