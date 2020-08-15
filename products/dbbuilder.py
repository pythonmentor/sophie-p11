import requests
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from products.models import ProductDb, CategoryDb


class ProductSelector:
    def __init__(self):
        self.url = 'https://fr.openfoodfacts.org/cgi/search.pl'
        self.params = {
            'lc': 'fr',
            'cc': 'fr',
            'nutriment_0': 'fat',
            'nutriment_compare_0': 'gte',
            'nutriment_value_O': 0,
            'nutriment_1': 'saturated-fat',
            'nutriment_compare_1': 'gte',
            'nutriment_value_0': 0,
            'nutriment_2': 'sugars',
            'nutriment_compare_2': 'gte',
            'nutriment_value_2': 0,
            'nutriment_3': 'salt',
            'nutriment_compare_3': 'gte',
            'nutriment_value_3': 0,
            'sort_b': 'unique_scans_n',
            'json': 1,
            'page_size': 1000,
            'action': 'process',
            'page': 1,
            'fields': 'product_name,url,categories,image_front_url,nutrition_grades,code,nutriments'
        }

    def select_products(self):
        response = requests.get(self.url, params=self.params)
        data = response.json()
        selected_products = data['products']

        for product in selected_products:
            if 'product_name' not in product or product['product_name'] == '' \
                    or 'image_front_url' not in product or product['image_front_url'] == ''\
                    or 'nutrition_grades' not in product or product['nutrition_grades'] == '' \
                    or 'code' not in product or product['code'] == '' \
                    or len(product['categories']) <= 3:
                continue
            else:
                self._save_in_db(product)

    def _save_in_db(self, product):
        product_name = product['product_name'].lower()

        try:
            ProductDb.objects.get(name=product_name)
        except ObjectDoesNotExist:
            try:
                p = ProductDb.objects.create(name=product_name, url=product['url'],
                                             image=product['image_front_url'], nutriscore=product['nutrition_grades'],
                                             barcode=product['code'], fat=product['nutriments']['fat'],
                                             saturated_fat=product['nutriments']['saturated-fat'],
                                             sugar=product['nutriments']['sugars'], salt=product['nutriments']['salt'])

                prod_categories = product['categories'].split(',')
                for prod_category in prod_categories:
                    category = CategoryDb.objects.get_or_create(name=prod_category)[0]
                    #print(category.id, category.name, category.url)
                    p.categories.add(category.id)

            except (ValidationError, AttributeError):
                pass


"""class ProductSelector:

    def __init__(self):
        self.url = 'https://fr.openfoodfacts.org/cgi/search.pl'
        self.params = {
            'nutriment_0': 'fat',
            'nutriment_compare_0': 'gte',
            'nutriment_value_O': 0,
            'nutriment_1': 'saturated-fat',
            'nutriment_compare_1': 'gte',
            'nutriment_value_0': 0,
            'nutriment_2': 'sugars',
            'nutriment_compare_2': 'gte',
            'nutriment_value_2': 0,
            'nutriment_3': 'salt',
            'nutriment_compare_3': 'gte',
            'nutriment_value_3': 0,
            'sort_b': 'unique_scans_n',
            'json': 1,
            'page_size': 1000,
            'action': 'process',
            'page': 1,
            'fields': 'product_name,url,categories,image_front_url,nutrition_grades,code,nutriments'
        }

    def select_products(self):
        response = requests.get(self.url, params=self.params)
        data = response.json()
        selected_products = data['products']
        selection = []

        for product in selected_products:
            if 'product_name' not in product or product['product_name'] == '' \
                    or 'image_front_url' not in product or product['image_front_url'] == ''\
                    or 'nutrition_grades' not in product or product['nutrition_grades'] == '' \
                    or 'code' not in product or product['code'] == '' \
                    or 'categories' not in product or len(product['categories']) <= 3:
                continue
            else:
                selection.append(product)
                self._save_in_db(product)

    def _save_in_db(self, product):
        try:
            ProductDb.objects.get(name=product['product_name'])
        except ObjectDoesNotExist:
            ProductDb.objects.create(name=product['product_name'], url=product['url'], categories=product['categories'],
                                     image=product['image_front_url'], nutriscore=product['nutrition_grades'],
                                     barcode=product['code'], fat=product['nutriments']['fat'],
                                     saturated_fat=product['nutriments']['saturated-fat'],
                                     sugar=product['nutriments']['sugars'], salt=product['nutriments']['salt'])


selector = ProductSelector()"""

####################################################################
"""   SCRIPT TO INITIALIZE THE DB THROUGH OPEN FOOD FACTS' API   """
####################################################################


"""def select_categories(limit_cat):
    Selecting the categories according the number entered by the user (management command: populatedb.py) 
    if CategoryDb.objects.all().count() != 0:
        return

    response = requests.get('https://fr.openfoodfacts.org/categories.json')
    data = response.json()
    categories = data['tags']
    selected_cat = categories[:limit_cat]
    for category in selected_cat:
        CategoryDb.objects.create(url=category['url'], name=category['name'])
        print('\nLa catégorie "' + category['name'] + '" vient d\'être ajoutée dans la base de données'
                                                      ' avec les produits suivants :')
        select_products(category)


def select_products(category):
    Selecting 20 products per categories according to criteria defined in params and creating the db
    selected_prod = []
    page = 1

    while len(selected_prod) < 20:
        r_products = requests.get('https://world.openfoodfacts.org/cgi/search.pl', params={
            'tagtype_0': 'categories',
            'tag_contains_0': 'contains',
            'tag_0': category['id'],
            'tagtype_1': 'countries',
            'tag_contains_1': 'contains',
            'tag_1': 'france',
            'nutriment_0': 'fat',
            'nutriment_compare_0': 'gte',
            'nutriment_value_O': 0,
            'nutriment_1': 'saturated-fat',
            'nutriment_compare_1': 'gte',
            'nutriment_value_0': 0,
            'nutriment_2': 'sugars',
            'nutriment_compare_2': 'gte',
            'nutriment_value_2': 0,
            'nutriment_3': 'salt',
            'nutriment_compare_3': 'gte',
            'nutriment_value_3': 0,
            'json': 1,
            'sort_by': 'unique_scans_n',
            'page_size': 50,
            'action': 'process',
            'page': page

        })
        response = r_products.json()
        products = response['products']
        for product in products:
            if 'product_name' not in product or product['product_name'] == '':
                continue
            try:
                ProductDb.objects.get(name__iexact=product['product_name'])
            except ObjectDoesNotExist:
                if 'url' in product and product['url'] != '' \
                        and 'nutrition_grades' in product and product['nutrition_grades'] != '':
                    selected_prod.append(product)
                    print(product['product_name'])
                    categorydb = CategoryDb.objects.get(url=category['url'])
                    ProductDb.objects.create(name=product['product_name'], url=product['url'],
                                             image=product['image_front_url'], nutriscore=product['nutrition_grades'],
                                             category=categorydb, fat=product['nutriments']['fat'],
                                             saturated_fat=product['nutriments']['saturated-fat'],
                                             sugar=product['nutriments']['sugars'], salt=product['nutriments']['salt'])
                if len(selected_prod) == 20:
                    break
        page += 1"""
