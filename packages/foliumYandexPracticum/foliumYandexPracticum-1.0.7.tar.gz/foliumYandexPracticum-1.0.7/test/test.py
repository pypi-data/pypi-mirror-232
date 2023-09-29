import foliumYandexPracticum as folium

m = folium.Map(
        location=[55.7522, 37.6156],
        min_zoom=0, 
        max_zoom=18,  
        zoom_start=16,
        control_scale=True,
)
m.save("map.html")