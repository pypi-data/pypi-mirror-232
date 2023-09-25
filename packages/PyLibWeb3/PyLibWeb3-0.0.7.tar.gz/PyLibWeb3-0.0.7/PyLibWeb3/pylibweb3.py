import requests

def require(*urls):
    for url in urls:
        try:
            response = requests.get(url)
            if response.status_code == 200:
                python_code = response.text

                # Ejecutar el código Python obtenido
                exec(python_code)

                # Imprimir las variables
                if version and version_required and library_name:
                    print(f"Nombre de la biblioteca: {library_name}")
                    print(f"Versión requerida: {version_required}")
                    print(f"Versión de la biblioteca: {version}")
                else:
                    print("El código no definió todas las variables necesarias.")

            else:
                print(f"No se pudo obtener el código Python de la URL: {url}")

        except Exception as e:
            print(f"Error al obtener el código Python de la URL: {url} - {str(e)}")

# Ejemplo de uso

