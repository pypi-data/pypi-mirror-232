# JellyDog
A Python web scraper to get stock data from JellyCat.com
To use JellyDog simply do this:  
```
import JellyDog
url = "https://www.jellycat.com/us/toastie-vivacious-aubergine-tov3au/" #Use Online stock page url
stock = JellyDog.check(url)
```
The Stock variable would be a dictionary variable with following schemetic:  
```
stock = {'model1' : ['name1', 'stock count', 'url'], 'model2' : ['name2', 'stock count', 'url']}
```
```Model``` is the ID of a specific model and size where you can find under the name of the name of each JellyCat name  
In this example, the ID number is ```TOV3AU```  
  
So If you run the code above, you should expect ```stock``` look like this:  
```
{'tov3au': ['Toastie Vivacious Aubergine', 4184]}
```
## What's next 
- Currently a webpage is being developed so everyone can easily get the up to date stock number for jellycat models  
  
- Futher __Email__/__Discord__/__Telegram__ bot maybe created to notice user about specific model restocking by request
