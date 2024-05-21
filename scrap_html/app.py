import requests
import json
from requests_html import HTMLSession 
import time
from scrap_html.pross import pross_data

class search():
    def search(key_word ):
        
        while True :    
            print("search...")        
            #print('enter search')
            
            
            url = "https://api.ouedkniss.com/graphql"

            payload = json.dumps({
            "operationName": "SearchQuery",
            "variables": {
                "mediaSize": "MEDIUM",
                "q": key_word,
                "filter": {
                "categorySlug": None,
                "origin": None,
                "connected": False,
                "delivery": None,
                "regionIds": [],
                "cityIds": [],
                "priceRange": [
                    None,
                    None
                ],
                "exchange": False,
                "hasPictures": False,
                "hasPrice": False,
                "priceUnit": None,
                "fields": [],
                "page": 1 ,
                "count": 48
                }
            },
            "query": "query SearchQuery($q: String, $filter: SearchFilterInput, $mediaSize: MediaSize = MEDIUM) {\n  search(q: $q, filter: $filter) {\n    announcements {\n      data {\n        ...AnnouncementContent\n        smallDescription {\n          valueText\n          __typename\n        }\n        noAdsense\n        __typename\n      }\n      paginatorInfo {\n        lastPage\n        hasMorePages\n        __typename\n      }\n      __typename\n    }\n    active {\n      category {\n        id\n        name\n        slug\n        icon\n        delivery\n        priceUnits\n        children {\n          id\n          name\n          slug\n          __typename\n        }\n        specifications {\n          isRequired\n          specification {\n            id\n            codename\n            label\n            type\n            class\n            datasets {\n              codename\n              label\n              __typename\n            }\n            dependsOn {\n              id\n              codename\n              __typename\n            }\n            subSpecifications {\n              id\n              codename\n              label\n              type\n              __typename\n            }\n            allSubSpecificationCodenames\n            __typename\n          }\n          __typename\n        }\n        parentTree {\n          id\n          name\n          slug\n          icon\n          children {\n            id\n            name\n            slug\n            icon\n            __typename\n          }\n          __typename\n        }\n        parent {\n          id\n          name\n          icon\n          __typename\n        }\n        __typename\n      }\n      count\n      __typename\n    }\n    suggested {\n      category {\n        id\n        name\n        slug\n        __typename\n      }\n      count\n      __typename\n    }\n    __typename\n  }\n}\n\nfragment AnnouncementContent on Announcement {\n  id\n  title\n  slug\n  createdAt: refreshedAt\n  isFromStore\n  isCommentEnabled\n  userReaction {\n    isBookmarked\n    isLiked\n    __typename\n  }\n  hasDelivery\n  deliveryType\n  likeCount\n  description\n  status\n  cities {\n    id\n    name\n    slug\n    region {\n      id\n      name\n      slug\n      __typename\n    }\n    __typename\n  }\n  store {\n    id\n    name\n    slug\n    imageUrl\n    __typename\n  }\n  defaultMedia(size: $mediaSize) {\n    mediaUrl\n    __typename\n  }\n  price\n  pricePreview\n  priceUnit\n  oldPrice\n  priceType\n  exchangeType\n  __typename\n}\n"
            })
            headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:91.0) Gecko/20100101 Firefox/91.0',
            'Accept': '*/*',
            'Accept-Language': 'fr',
            'Referer': 'https://www.ouedkniss.com/',
            'content-type': 'application/json',
            'Locale': 'fr',
            'X-Referer': 'https://www.ouedkniss.com/s/1?keywords=raccent',
            'X-App-Version': '"1.4.17"',
            'X-Track-ID': 'eac6360d-c5ff-431d-8ef2-7fc2b32f32bc',
            'X-Track-Timestamp': '1663618748',
            'Authorization': '',
            'Origin': 'https://www.ouedkniss.com',
            'Connection': 'keep-alive',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-site',
            'Pragma': 'no-cache',
            'Cache-Control': 'no-cache',
            'TE': 'trailers'
            }

            response = requests.request("POST", url, headers=headers, data=payload)
            cats= response.json()
            title_vente =cats["data"]["search"]["announcements"]["data"]
            #for loop======
            time.sleep(5)
            result = {}
            for i in range(0,len(title_vente)):
                print(title_vente[i])
                try:
                    #print('hllo into for')
                    title=title_vente[i]["title"]
                    loc2=title_vente[i]["createdAt"]
                    descp=title_vente[i]["description"]
                    loc=title_vente[i]["cities"][0]["name"]
                    loc1=title_vente[i]["cities"][0]["region"]["name"]
                    link=title_vente[i]["defaultMedia"]["mediaUrl"]
                    prix=title_vente[i]["price"]
                    unit=title_vente[i]["priceUnit"]
                    type_price=title_vente[i]["priceType"]
                    exchangeType=title_vente[i]["exchangeType"]
                    km_srch=title_vente[i]["smallDescription"][0]["valueText"][0] #====km
                    type_srch=title_vente[i]["smallDescription"][1]["valueText"][0] # l et les chevaux
                    boit_car=title_vente[i]["smallDescription"][2]["valueText"][0] # boit des vettess
                    color_car=title_vente[i]["smallDescription"][3]["valueText"][0] #color 
                    cart_gris=title_vente[i]["smallDescription"][4]["valueText"][0] #cart gris
                    #=========================
                    link=='' 
                    result[i] =[]
                    result[i].append(str(title))
                    result[i].append(str(descp))
                    result[i].append(f'''{str(link)}''')
                    result[i].append(str(loc))
                    result[i].append(str(loc1))
                    result[i].append(str(prix))
                    result[i].append(str(unit))
                    result[i].append(str(type_price))
                    result[i].append(str(exchangeType))
                    result[i].append(str(km_srch))
                    result[i].append(str(type_srch))
                    result[i].append(str(boit_car))
                    result[i].append(str(color_car))
                    result[i].append(str(cart_gris))
                    result[i].append(str(loc2))

                    #print(loc)
                except Exception :
                    pass   

            s = json.dumps(result)
            print(s)
            with open("data.json" , "w") as f:
                f.write(s)
            break
        results = pross_data()
        return results
#search.search('audi')