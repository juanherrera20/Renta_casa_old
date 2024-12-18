1. Crea y activa un entorno virtual:

    - En Windows:

        ```bash
        python -m venv env
        venv\Scripts\activate
        ```

    - En macOS/Linux:

        ```bash
        python3 -m venv env
        source venv/bin/activate
        ```

2. Instala las dependencias:

    ```bash
    pip install -r requirements.txt
    ```

3. Configura las variables de entorno (por ejemplo, en un archivo `.venv`):

    - `DEBUG=True`
    - `SECRET_KEY=<tu_clave_secreta>`
    - `DATABASE_URL=<url_de_tu_base_de_datos>`

4. Realiza las migraciones de la base de datos:

    ```bash
    python manage.py makemigrations
    python manage.py migrate
    ```

5. Ejecuta el servidor de desarrollo:

Dentro de la carpeta desarrollo, donde se encuentre el archivo manage.py se ejecuta lo siguiente:

    ```bash
    python manage.py runserver
    ```
