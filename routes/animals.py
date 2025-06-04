from flask import request, jsonify
from database.database import get_db_connection, get_cursor
from routes.owners import get_owner_by_id


## Hilfsfunktionen für die Entitäten
def get_animal_by_id(animal_id):
    con = get_db_connection()
    cur = get_cursor(con)
    cur.execute('SELECT * FROM Animals WHERE id = %s', (animal_id,))
    animal = cur.fetchone()
    con.close()
    return animal

def register_animal_routes(app):
    ## GET-Route implementieren, d.h. Daten abrufen bzw. alle Tiere anzeigen
    @app.route("/api/animals", methods=['GET'])
    def show_animals():
        """
        Liste aller Tiere
        ---
        responses:
            200:
                description: JSON-Liste aller Tiere
                examples:
                    application/json:
                    -
                        id: 1
                        name: Dog
                        age: 3
                        genus: mammals
                        owner_id: 2
                    -
                        id: 2
                        name: Cat
                        age: 2
                        genus: mammals
                        owner_id: 3
        """
        # Daten abrufen von der DB
        con = get_db_connection() # Verbindung mit der DB
        cur = get_cursor(con)
        cur.execute('SELECT * FROM Animals')
        animals = cur.fetchall()
        con.close()
        return jsonify([dict(animal) for animal in animals]), 200

    ## GET-Route implementieren, um Daten von einem Tier anzuzeigen
    @app.route("/api/animals/<int:animal_id>", methods=['GET'])
    def show_animal(animal_id):
        """
        Anzeigen eines Tieres
        ---
        parameters:
        -
            name: animal_id
            in: path
            type: integer
            required: true
            description: Die ID des anzuzeigenden Tieres
        responses:
            200:
                description: JSON-Objekt von einem Tier
                examples:
                    application/json:
                        id: 1
                        name: Dog
                        age: 3
                        genus: mammals
                        owner_id: 2
            404:
                description: Tier wurde nicht gefunden
                examples:
                    application/json:
                        message: Tier mit der ID 7 existiert nicht
        """
        animal = get_animal_by_id(animal_id)
        if animal is None:
            return jsonify({"message": f"Tier mit der ID {animal_id} existiert nicht"}), 404
        return jsonify(animal), 200
    
    ## POST-Route implementieren, d.h. neue Tier hinzufügen
    @app.route("/api/animals", methods=['POST'])
    def add_animal():
        """
        Neues Tier hinzufügen
        ---
        consumes: [application/json]
        parameters:
        -
            in: body
            name: tier
            required: true
            description: name muss angegeben werden
            schema:
                type: object
                required: [name]
                properties:
                    name:
                        type: string
                        example: Elephant
                    age:
                        type: integer
                        example: 10
                    genus:
                        type: string
                        example: mammals
                    owner_id:
                        type: integer
                        example: 2
        responses:
            201:
                description: Tier hinzugefügt
                examples:
                    application/json:
                        message: Tier wurde erfolgreich hinzugefügt
            400:
                description: Keine oder fehlerhafte Daten
                examples:
                    application/json:
                        message: Keine oder fehlerhafte Daten übertragen
        """
        new_animal = request.get_json() # {"name": "turtle", "age:": 100, "genus": "reptile"}
        if not new_animal or 'name' not in new_animal:
            return jsonify({"message": "Keine oder fehlerhafte Daten übertragen"}), 400
        con = get_db_connection() # Schritt 1: DB-Verbindung
        cur = get_cursor(con) # Schritt 2: Cursor-Objekt definieren
        # Schritt 3: Befehl ausführen
        cur.execute('INSERT INTO Animals (name, age, genus, owner_id) VALUES (%s,%s,%s, %s)', 
                    (new_animal['name'],
                    new_animal['age'],
                    new_animal['genus'],
                    new_animal['owner_id'])
                    ) # An dieser Stelle SQL-Befehl zum Hinzufügen des neuen Objektes
        con.commit() # Schritt 4: Persistieren der Veränderungen
        con.close() # Schritt 5: Verbindung zur DB wieder schließen
        return jsonify({"message": "Tier wurde erfolgreich hinzugefügt"}), 201

    ## DELETE-Route, um ein Tier aus der Liste zu löschen
    @app.route("/api/animals/<int:animal_id>", methods=['DELETE'])
    def delete_animal(animal_id):
        """
        Ein Tier löschen
        ---
        parameters:
        -
            name: animal_id
            in: path
            type: integer
            required: true
            description: Die ID des zu löschenden Tieres
        responses:
            200:
                description: Tier wurde gelöscht
                examples:
                    application/json:
                        message: Tier wurde erfolgreich gelöscht
            404:
                description: Tier wurde nicht gefunden
                examples:
                    application/json:
                        message: Tier mit der ID 7 existiert nicht
        """
        con = get_db_connection() 
        cur = get_cursor(con)
        # Überprüfe, ob das Tier mit der angegebenen ID überhaupt existiert
        cur.execute('SELECT * FROM Animals WHERE id = %s', (animal_id,))
        animal = cur.fetchone()
        if animal is None:
            return jsonify({"message": f"Tier mit der ID {animal_id} existiert nicht"}), 404
        cur.execute('DELETE FROM Animals WHERE id = %s', (animal_id,) )
        ## Achtung: Nutz bitte die %s-Funktion, um SQL-Injection zu verhindern, sonst sähe es so aus:
        # cur.execute(f'DELETE FROM Animals WHERE id = {animal_id}') # 4 OR 1=! --
        con.commit()
        con.close()
        return jsonify({"message": "Tier wurde erfolgreich gelöscht"}), 200

    ## PUT-Route -> Ersetze alle Eigenschaften eines Tieres, d.h. hier schicken wir alle Eigenschaften im Body als JSON mit
    @app.route("/api/animals/<int:animal_id>", methods=['PUT'])
    def put_animal(animal_id):
        """
        Ganzes Tier ersetzen
        ---
        parameters:
        -
            name: animal_id
            in: path
            type: integer
            required: true
            description: Die ID des Tiers, das ersetzt werden soll
        -
            in: body
            name: tier
            required: true
            description: name muss angegeben werden
            schema: 
                type: object
                required: [name]
                properties:
                    name:
                        type: string
                        example: elephant
                    age:
                        type: integer
                        example: 20
                    genus:
                        type: string
                        example: mammals
                    owner_id:
                        type: integer
                        example: 2
        responses:
            200:
                description: Tier wurde aktualisiert
                examples:
                    application/json:
                        message: Tier wurde komplett aktualisiert
            404:
                description: Tier wurde nicht gefunden
                examples:
                    application/json:
                        message: Tier mit der ID 7 existiert nicht
        """
        updated_animal = request.get_json() 
        if not updated_animal or 'name' not in updated_animal:
            return jsonify({"message": "Fehlende Daten"}), 400
        con = get_db_connection() 
        cur = get_cursor(con) 
        cur.execute('SELECT * FROM Animals WHERE id = %s', (animal_id,))
        animal = cur.fetchone()
        if animal is None:
            return jsonify({"message": f"Tier mit der ID {animal_id} existiert nicht"}), 404
        cur.execute('UPDATE Animals SET name = %s, age = %s, genus = %s, owner_id = %s WHERE id = %s', (updated_animal['name'], updated_animal['age'], updated_animal['genus'], updated_animal['owner_id'], animal_id))
        con.commit()
        con.close()
        return jsonify({"message": "Tier wurde komplett aktualisiert"}), 200


    ## PATCH-Route -> Ersetze spezifisch einzelne Eigenschaften, d.h. hier schicken wir nur die zu ändernden Eigenschaften im Body als JSON mit
    @app.route("/api/animals/<int:animal_id>", methods=["PATCH"])
    def patch_animal(animal_id):
        """
        Tier teilweise ändern (z.B. nur das Alter)
        ---
        parameters:
        -
            name: animal_id
            in: path
            type: integer
            required: true
            description: Die ID des Tiers, das aktualisiert werden soll
        -
            in: body
            name: tier
            required: true
            description: Es muss mindestens einer der Werte angegeben werden
            schema: 
                type: object
                required: anyOf
                properties:
                    name:
                        type: string
                        example: elephant
                    age:
                        type: integer
                        example: 20
                    genus:
                        type: string
                        example: mammals
                    owner_id:
                        type: integer
                        example: 3
        responses:
            200:
                description: Tier wurde geupdated
                examples:
                    application/json:
                        message: Tier wurde geupdated
            404:
                description: Tier wurde nicht gefunden
                examples:
                    application/json:
                        message: Tier mit der ID 7 existiert nicht
        """
        updated_animal = request.get_json() # name, age, genus
        if not updated_animal:
            return jsonify({"message": "Fehlende Daten"}), 400
        con = get_db_connection()
        cur = get_cursor(con)
        cur.execute('SELECT * FROM Animals WHERE id = %s', (animal_id,))
        animal = cur.fetchone()
        if animal is None:
            return jsonify({"message": f"Tier mit der ID {animal_id} existiert nicht"}), 404
        # Leere Liste, wo wir die Felder mitgeben, die wir speziell updaten wollen
        update_fields = [] # Notizzettel, wo wir alle Spalten reinschreiben, die der Client updaten möchte, z.B. nur name: elephant Joel, age = 24
        # Leere Liste, wo wir die Werte der Felder mitgeben, die wir updaten wollen
        update_values = [] # Notizzettel, wo wir die entsprechenden Werte reinschreiben von den Spalten, die wir aktualisieren wollen

        for field in ['name', 'age', 'genus', 'owner_id']: # Iteriere über alle möglichen, vorhandenen Spalte der Tabelle
            if field in updated_animal:
                update_fields.append(f'{field} = %s') # name = %s, age = %s
                update_values.append(updated_animal[field]) # elephant Joel, 24
        
        if update_fields:
            update_values.append(animal_id)
            query = f'UPDATE Animals SET {", ".join(update_fields)} WHERE id = %s' # UPDATE Animals SET name = %s, age = %s WHERE id = %s
            cur.execute(query, update_values)
            con.commit()
        con.close()
        return jsonify({"message": "Tier wurde geupdated"}), 200
    
    # Anzeigen, welcher Owner zum Tier gehört
    # GET /api/animals/<int:animal_id>/owner
    @app.route("/api/animals/<int:animal_id>/owner", methods=["GET"])
    def get_owner_of_animal(animal_id):
        """
        Zeigt den Besitzer eines Tieres an
        ---
        parameters:
        - 
            name: animal_id
            in: path
            type: integer
            required: true
            description: Die ID des Tieres
        responses:
            200:
                description: Besitzer-Daten oder ggf. eine Info, dass kein Besitzer zugeordnet ist
                examples:
                    application/json:
                        animal: dog
                        owner:
                            email: schmidty@mail.de
                            id: 2
                            name: Anna Schmidt
                            phone: 01896 128842
            404:
                description: Tier oder Besitzer mit der eingetragenen ID wurde nicht gefunden
                examples:
                    application/json:
                        message: Tier mit der ID 7 existiert nicht
        """
        animal = get_animal_by_id(animal_id)
        if animal is None:
            return jsonify({"message": f"Tier mit der ID {animal_id} existiert nicht"}), 404
        if animal["owner_id"] is None:
            return jsonify({"message": "Tier hat keinen Besitzer und kann adoptiert werden"}), 200
        owner_id = animal["owner_id"]
        owner = get_owner_by_id(owner_id)
        if owner is None:
            return jsonify({"message": f"Besitzer mit der ID {owner_id} nicht gefunden"}), 404
        
        return jsonify({
            "animal": animal["name"],
            "owner": owner
        }), 200
    
    ## TODO: JOIN 
    @app.route("/api/animals/<int:animal_id>/owner/join", methods=["GET"])
    def get_owner_of_animal_by_join(animal_id):
        """
        Zeigt den Owner eines Tieres an (Mit JOIN)
        ---
        parameters:
            - name: animal_id
              in: path
              type: integer
              required: true
              description: Die ID des Tieres
        responses:
            200:
                description: Besitzer-Daten oder ggf. eine Info, dass kein Besitzer zugeordnet ist
                examples:
                    application/json:
                        animal: dog
                        owner:
                            email: schmidty@mail.de
                            id: 2
                            name: Anna Schmidt
                            phone: 01896 128842
            404:
                description: Tier oder Besitzer mit der eingetragenen ID wurde nicht gefunden
                examples:
                    application/json:
                        message: Tier mit der ID 7 existiert nicht
        """
        con = get_db_connection()
        cur = get_cursor(con)
        cur.execute('''
                SELECT 
                    a.name AS animal_name,
                    o.id AS owner_id,
                    o.name AS owner_name,
                    o.email AS owner_email,
                    o.phone AS owner_phone
                FROM Animals a JOIN Owners o ON a.owner_id = o.id
                WHERE a.id = %s
                ''', (animal_id,))
        result = cur.fetchone()
        con.close()

        if result:
            return jsonify({
                "animal": result["animal_name"],
                "owner": {
                    "id": result["owner_id"],
                    "name": result["owner_name"],
                    "email": result["owner_email"],
                    "phone": result["owner_phone"]
                }
            }), 200
        else:
            animal = get_animal_by_id(animal_id)
            if animal is None:
                return jsonify({"message": f"Tier mit der ID {animal_id} existiert nicht"}), 404
            return jsonify({"message": "Tier hat keinen Besitzer"}), 200

        
    # POST /api/animals/<int:animal_id>/release
    # Tier wird wieder freigegeben, d.h. der Besitzer bzw. die owner_id wird auf Null esetzt
    @app.route("/api/animals/<int:animal_id>/release", methods=["POST"])
    def release_animal(animal_id):
        """
        Ein Tier freilassen (Besitzer entfernen)
        ---
        parameters:
        -
            name: animal_id
            in: path
            type: integer
            required: true
            description: Die ID des freizulassenden Tieres
        responses:
            200:
                description: Tier wurde freigelassen
                examples:
                    application/json:
                        message: Elephant wird nicht mehr besessen von Max Mustermann
            400:
                description: Tier hat keinen Besitzer
                examples:
                    application/json:
                        message: Tier mit der ID 7 hat keinen Besitzer
            404:
                description: Tier wurde nicht gefunden
                examples:
                    application/json:
                        message: Tier mit der ID 7 existiert nicht
        """
        animal = get_animal_by_id(animal_id)
        if animal is None:
            return jsonify({"message": f"Tier mit der ID {animal_id} existiert nicht"}), 404
        if animal["owner_id"] is None:
            return jsonify({"message": f"Tier mit der ID {animal_id} hat keinen Besitzer"}), 400

        old_owner = get_owner_by_id(animal["owner_id"])
        con = get_db_connection()
        cur = get_cursor(con)
        cur.execute('UPDATE Animals SET owner_id = NULL WHERE id = %s', (animal_id,))
        con.commit()
        con.close()

        return jsonify({"message": f"{animal["name"]} wird nicht mehr besessen von {old_owner["name"]}"}), 200