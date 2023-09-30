from product import Product
#from product import Product

a_store = Product('https://www.etsy.com/uk/listing/1559236134/scream-collage-vintage-style-t?click_key=4b9cd8a239f73a00a5eff4506a00d963020dcaab%3A1559236134&click_sum=84376f49&ref=shop_home_feat_1&pro=1')
a_store.connect()

a_store.get_all_data()
print(a_store.generate_json())