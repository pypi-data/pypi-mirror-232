# Latest Indonesia EarthQuake
This package will get the latest earthquake from BMKG | Meteorological, Climatological, and Geophysical Agency

## HOW IT WORKS?
This package will scrape from [BMKG](https://bmkg.go.id) to get latest quake happened in Indonesia

This package will use BeautifulSoup4 and Request to produce output in the form of JSON that is ready to be used in web or mobile application.

## HOW TO USE
```
import gempa_terkini

if __name__== '__main__':
    print('Aplikasi utama')
    result=gempa_terkini.ekstraksi_data()
    gempa_terkini.tamilkan_data(result)
```



# Author
Restu Bagas Pangestu