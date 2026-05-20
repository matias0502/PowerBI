import os
import requests
from bs4 import BeautifulSoup
from datetime import datetime

def extraer_titulares():
    print("🚀 [CI/CD] Iniciando Extractor de Titulares en la Nube...")
    url = "https://www.marca.com/"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    try:
        print(f"📡 Conectando con {url}...")
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            print("✅ Conexión exitosa. Procesando el HTML...")
            soup = BeautifulSoup(response.text, 'html.parser')
            
            titulares = soup.select('header h2, .ue-c-cover-content__headline, h2.ue-c-cover-content__headline-custom')
            
            # Nombre del archivo que vamos a crear
            nombre_archivo = "titulares.txt"
            
            # Abrimos el archivo en modo escritura ("w") con codificación utf-8
            with open(nombre_archivo, "w", encoding="utf-8") as archivo:
                cabecera = f"📰 TITULARES DESTACADOS DE HOY ({datetime.now().strftime('%d/%m/%Y %H:%M')})"
                
                # Escribimos en el archivo y también imprimimos en consola
                archivo.write(cabecera + "\n")
                archivo.write("=" * 60 + "\n")
                
                print(f"\n{cabecera}")
                print("=" * 60)
                
                contador = 0
                for t in titulares:
                    texto = t.get_text().strip()
                    if texto and len(texto) > 10:
                        contador += 1
                        linea = f"{contador}. 🔥 {texto}"
                        
                        # Escribimos la línea en el archivo
                        archivo.write(linea + "\n")
                        print(linea)
                    
                    if contador >= 15:
                        break
                        
                if contador == 0:
                    mensaje_error = "⚠️ No se pudieron extraer titulares estructurados. Es posible que el diseño web haya cambiado."
                    archivo.write(mensaje_error + "\n")
                    print(mensaje_error)
                
                archivo.write("=" * 60 + "\n")
                print("=" * 60)
                print(f"📁 Se ha creado el archivo: {nombre_archivo}")
                
        else:
            print(f"❌ Error al acceder a la web. Código de estado: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Ocurrió un error durante el scraping: {e}")

if __name__ == "__main__":
    extraer_titulares()
