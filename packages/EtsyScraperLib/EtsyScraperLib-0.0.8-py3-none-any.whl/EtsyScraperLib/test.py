from store import Store
from product import Product

nacho = Product('https://www.etsy.com/uk/listing/1461160418/oh-hi-doggy-the-room-sticker?click_key=ff9f09632776eaa571423525c2ad5f3863e9b8f3%3A1461160418&click_sum=329eccd8&ref=shop_home_active_2&frs=1')
nacho.connect()

nacho.get_all_data()
nacho.generate_json()