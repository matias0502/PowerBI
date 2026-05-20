import csv
import json
import os
import re
from datetime import datetime
import requests
from bs4 import BeautifulSoup

def scrape_druni_perfumes():
    # URL de perfumes de hombre ordenados por más vendidos (bestsellers)
    url = "https://www.druni.es/perfumes/hombre?order=bestsellers"
    
    # Cabeceras (Headers) para simular un navegador real y mitigar bloqueos básicos
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept-Language": "es-ES,es;q=0.9,en;q=0.8",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Referer": "https://www.google.com/"
    }
    
    print(f"[-] Conectando a Druni: {url}")
    try:
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code != 200:
            print(f"[!] Error al acceder a la web. Código de estado: {response.status_code}")
            return
    except Exception as e:
        print(f"[!] Ocurrió un error en la petición HTTP: {e}")
        return

    soup = BeautifulSoup(response.text, 'html.parser')
    perfumes = []
    
    # Método 1: Buscar mediante las clases habituales del HTML de la tienda
    items = soup.find_all(['li', 'div'], class_=re.compile(r'product-item|product_item|item-product'))
    
    if not items:
        # Intento alternativo usando selectores CSS comunes
        items = soup.select('.product-item') or soup.select('[data-container="product-grid"]')
        
    print(f"[-] Elementos de productos encontrados en HTML: {len(items)}")
    
    for idx, item in enumerate(items, start=1):
        try:
            # 1. Extraer Marca
            brand_elem = item.find(class_=re.compile(r'brand|marca|product-item-brand'))
            brand = brand_elem.text.strip() if brand_elem else "Desconocida"
            
            # 2. Extraer Nombre del perfume
            name_elem = item.find(['a', 'span', 'strong'], class_=re.compile(r'name|nombre|product-item-link|title'))
            name = name_elem.text.strip() if name_elem else ""
            
            # Limpiar nombre si repite la marca al principio
            if name and brand != "Desconocida" and name.upper().startswith(brand.upper()):
                name = name[len(brand):].strip(" .-:/")
                
            # 3. Extraer Precio
            price_elem = item.find(class_=re.compile(r'price|precio|final-price'))
            price = price_elem.text.strip() if price_elem else "No disponible"
            
            # 4. Enlace del producto
            link_elem = item.find('a', href=True)
            link = link_elem['href'] if link_elem else url
            
            if name or brand != "Desconocida":
                perfumes.append({
                    "Posicion": idx,
                    "Marca": brand,
                    "Nombre": name,
                    "Precio": price,
                    "Enlace": link,
                    "Fecha_Extraccion": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                })
        except Exception as e:
            continue
            
    # Método 2 (Respaldo): Si el HTML estructurado falló por cambios dinámicos, extrae datos desde JSON-LD interno
    if not perfumes:
        print("[-] Buscando datos estructurados en scripts ocultos...")
        scripts = soup.find_all('script', type='application/ld+json')
        for script in scripts:
            try:
                data = json.loads(script.string)
                if isinstance(data, dict) and data.get("@type") == "ItemList":
                    for idx, element in enumerate(data.get("itemListElement", []), start=1):
                        prod = element.get("item", {})
                        perfumes.append({
                            "Posicion": idx,
                            "Marca": prod.get("brand", {}).get("name", "Desconocida") if isinstance(prod.get("brand"), dict) else prod.get("brand", "Desconocida"),
                            "Nombre": prod.get("name", "Desconocida"),
                            "Precio": prod.get("offers", {}).get("price", "No disponible") if isinstance(prod.get("offers"), dict) else "No disponible",
                            "Enlace": prod.get("url", url),
                            "Fecha_Extraccion": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        })
                    break
            except Exception:
                continue

    # Guardar los resultados en formato CSV
    if perfumes:
        print(f"[+] Éxito. Se han recopilado {len(perfumes)} perfumes.")
        csv_filename = "perfumes_hombre_mas_vendidos.csv"
        
        with open(csv_filename, 'w', newline='', encoding='utf-8') as output_file:
            dict_writer = csv.DictWriter(output_file, fieldnames=perfumes[0].keys())
            dict_writer.writeheader()
            dict_writer.writerows(perfumes)
            
        print(f"[+] Archivo '{csv_filename}' generado con éxito.")
    else:
        print("[!] No se han podido extraer datos en esta ejecución. Es posible que la web use bloqueos avanzados por IP.")

if __name__ == "__main__":
    scrape_druni_perfumes()
