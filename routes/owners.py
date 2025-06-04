from database.database import get_db_connection, get_cursor
from flask import jsonify, request

def get_owner_by_id(owner_id):
    con = get_db_connection()
    cur = get_cursor(con)
    cur.execute('SELECT * FROM Owners WHERE id = ?', (owner_id,))
    owner = cur.fetchone()
    con.close()
    return owner

def get_animal_by_id(animal_id):
    con = get_db_connection()
    cur = get_cursor(con)
    cur.execute('SELECT * FROM Animals WHERE id = ?', (animal_id,))
    animal = cur.fetchone()
    con.close()
    return animal


def register_owner_routes(app):
    ## GET-Route implementieren, d.h. Daten abrufen bzw. alle Owner anzeigen
    @app.route("/api/owners", methods=['GET'])
    def show_owners():
        """
        Liste aller Besitzer
        ---
        responses:
            200:
                description: JSON-Liste aller Besitzer
                examples:
                    application/json:
                    -
                        id: 1
                        name: Max Mustermann
                        email: max_mustermann@email.de
                        phone: 01234 56789
                    -
                        id: 2
                        name: Anna Schmidt
                        email: anna_schmidt@email.de
                        phone: 0987 65432
        """
        # Daten abrufen von der DB
        con = get_db_connection() # Verbindung mit der DB
        cur = con.cursor()
        owners = cur.execute('SELECT * FROM Owners').fetchall()
        con.close()
        return jsonify([dict(owner) for owner in owners]), 200




    ## GET-Route implementieren, um Daten von einem Owner anzuzeigen
    @app.route("/api/owners/<int:owner_id>", methods=['GET'])
    def show_owner(owner_id):
        """
        Anzeigen eines Besitzers
        ---
        parameters:
            - name: owner_id
              in: path
              type: integer
              required: true
              description: Die ID des anzuzeigenden Besitzers
        responses:
            200:
                description: JSON-Objekt von einem Besitzer
                examples:
                    application/json:
                        id: 1
                        name: Max Mustermann
                        email: max_mustermann@email.de 
                        phone: 01234 56789
            404:
                description: Besitzer wurde nicht gefunden
                examples:
                    application/json:
                        message: Besitzer mit der ID 5 existiert nicht
        """
        con = get_db_connection()
        cur = con.cursor()
        owner = cur.execute('SELECT * FROM Owners WHERE id = ?', (owner_id,)).fetchone()
        if owner is None:
            return jsonify({"message": f"Besitzer mit der ID {owner_id} existiert nicht"}), 404
        con.commit()
        con.close()
        return jsonify(dict(owner)), 200



    @app.route("/api/owners", methods=['POST'])
    def add_owner():
        """
        Neuen Besitzer hinzufügen
        ---
        consumes: [application/json]
        parameters:
        -
            in: body
            name: Besitzer
            required: true
            description: name muss angegeben werden
            schema:
                type: object
                required: [name]
                properties:
                    name:
                        type: string
                        example: Max Mustermann
                    email:
                        type: string
                        example: max@email.com
                    phone:
                        type: string
                        example: 0123 456789
        responses:
            201:
                description: Besitzer wurde erfolgreich hinzugefügt
                examples:
                    application/json:
                        message: Besitzer wurde erfolgreich hinzugefügt
            400:
                description: Keine oder fehlerhafte Daten übertragen
                examples:
                    application/json:
                        message: Keine oder fehlerhafte Daten übertragen
        """
        new_owner = request.get_json()
        if not new_owner or 'name' not in new_owner:
            return jsonify({"message": "Keine oder fehlerhafte Daten übertragen"}), 400
        con = get_db_connection() # Schritt 1: DB-Verbindung
        cur = con.cursor() # Schritt 2: Cursor-Objekt definieren
        # Schritt 3: Befehl ausführen
        cur.execute('INSERT INTO Owners (name, email, phone) VALUES (?,?,?)', 
                    (new_owner['name'],
                    new_owner['email'],
                    new_owner['phone'])
                    ) # An dieser Stelle SQL-Befehl zum Hinzufügen des neuen Objektes
        con.commit() # Schritt 4: Persistieren der Veränderungen
        con.close() # Schritt 5: Verbindung zur DB wieder schließen
        return jsonify({"message": "Besitzer wurde erfolgreich hinzugefügt"}), 201



    @app.route("/api/owners/<int:owner_id>", methods=['DELETE'])
    def delete_owner(owner_id):
        """
        Einen Besitzer löschen
        ---
        parameters:
        -
            name: owner_id
            in: path
            type: integer
            required: true
            description: Die ID des zu löschenden Besitzers
        responses:
            200:
                description: Besitzer wurde gelöscht
                examples:
                    application/json:
                        message: Besitzer wurde erfolgreich gelöscht
            404:
                description: Besitzer wurde nicht gefunden
                examples:
                    application/json:
                        message: Besitzer mit der ID 5 existiert nicht
        """
        con = get_db_connection() 
        cur = con.cursor()
        # Überprüfe, ob das Tier mit der angegebenen ID überhaupt existiert
        owner = cur.execute('SELECT * FROM Owners WHERE id = ?', (owner_id,)).fetchone() # 4 OR 1=! --
        if owner is None:
            return jsonify({"message": "Besitzer mit dieser ID existiert nicht"}), 404
        cur.execute('DELETE FROM Owners WHERE id = ?', (owner_id,) )
        con.commit()
        con.close()
        return jsonify({"message": "Besitzer wurde erfolgreich gelöscht"}), 200

    ## Baue eine Funktion, zum Updaten

    ## PUT-Route -> Ersetze alle Eigenschaften eines Besitzers, d.h. hier schicken wir alle Eigenschaften im Body als JSON mit
    @app.route("/api/owners/<int:owner_id>", methods=['PUT'])
    def put_owner(owner_id):
        """
        Besitzer aktualisieren im Ganzen
        ---
        parameters:
        -
            name: owner_id
            in: path
            type: integer
            required: true
            description: Die ID des Besitzers, der ersetzt werden soll
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
                        example: max mustermann
                    email:
                        type: string
                        example: max@mail.de
                    phone:
                        type: string
                        example: 0123 456789
        responses:
            200:
                description: Besitzer wurde aktualisiert
                examples:
                    application/json:
                        message: Besitzer wurde komplett aktualisiert
            404:
                description: Besitzer wurde nicht gefunden
                examples:
                    application/json:
                        message: Besitzer mit der ID 7 existiert nicht
        """
        updated_owner = request.get_json() # Speichere dir das Objekt im Body aus dem Request des Clients
        if not updated_owner or 'name' not in updated_owner:
            return jsonify({"message": "Fehlende Daten"}), 400
        con = get_db_connection() # Schritt 1
        cur = con.cursor() # Schritt 2
        # Schritt 3
        owner = cur.execute('SELECT * FROM Owners WHERE id = ?', (owner_id,)).fetchone()
        if owner is None:
            return jsonify({"message": f"Besitzer mit der ID {owner_id} existiert nicht"}), 404
        # Update jetzt den Besitzer mit der übergebenen ID und mit den übergebenen Daten
        cur.execute('UPDATE Owners SET name = ?, email = ?, phone = ? WHERE id = ?', (updated_owner['name'], updated_owner['email'], updated_owner['phone'], owner_id))
        con.commit()
        con.close()
        return jsonify({"message": "Besitzer wurde komplett aktualisiert"}), 200


    ## PATCH-Route -> Ersetze spezifisch einzelne Eigenschaften, d.h. hier schicken wir nur die zu ändernden Eigenschaften im Body als JSON mit
    ## Owners
    @app.route("/api/owners/<int:owner_id>", methods=["PATCH"])
    def patch_owner(owner_id):
        """
        Besitzer teilweise ändern (z.B. nur die Email)
        ---
        parameters:
        -
            name: owner_id
            in: path
            type: integer
            required: true
            description: Die ID des Besitzers, der aktualisiert werden soll
        -
            in: body
            name: besitzer
            required: true
            description: Es muss mindestens einer der Werte angegeben werden
            schema: 
                type: object
                required: anyOf
                properties:
                    id:
                        type: integer
                        example: 3
                    name:
                        type: string
                        example: lisa schmidt
                    email:
                        type: string
                        example: lisaschmidt@mail.de
                    phone:
                        type: string
                        example: 012-2345
        responses:
            200:
                description: Besitzer wurde geupdated
                examples:
                    application/json:
                        message: Besitzer wurde geupdated
            404:
                description: Besitzer wurde nicht gefunden
                examples:
                    application/json:
                        message: Besitzer mit der ID 7 existiert nicht
        """
        updated_owner = request.get_json()
        if not updated_owner:
            return jsonify({"message": "Fehlende Daten"}), 400
        con = get_db_connection()
        cur = con.cursor()
        owner = cur.execute('SELECT * FROM Owners WHERE id = ?', (owner_id,)).fetchone()
        if owner is None:
            return jsonify({"message": f"Besitzer mit der ID {owner_id} existiert nicht"}), 404
        # Leere Liste, wo wir die Felder mitgeben, die wir speziell updaten wollen
        update_fields = [] # Notizzettel, wo wir alle Spalten reinschreiben, die der Client updaten möchte, z.B. nur name: elephant Joel, age = 24
        # Leere Liste, wo wir die Werte der Felder mitgeben, die wir updaten wollen
        update_values = [] # Notizzettel, wo wir die entsprechenden Werte reinschreiben von den Spalten, die wir aktualisieren wollen

        for field in ['name', 'email', 'phone']: # Iteriere über alle möglichen, vorhandenen Spalte der Tabelle
            if field in updated_owner:
                update_fields.append(f'{field} = ?') # name = ?, age = ?
                update_values.append(updated_owner[field]) # elephant Joel, 24
        
        if update_fields:
            update_values.append(owner_id)
            query = f'UPDATE Owners SET {", ".join(update_fields)} WHERE id = ?'
            cur.execute(query, update_values)
            con.commit()
        con.close()
        return jsonify({"message": "Besitzer wurde geupdated"}), 200

    # POST /api/owners/<int:owner_id>/adopt/<int:animal_id>
    # Route, damit ein Besitzer ein Tier adoptieren kann
    @app.route("/api/owners/<int:owner_id>/adopt/<int:animal_id>", methods=["POST"])
    def adopt_animal(owner_id, animal_id):
        owner = get_owner_by_id(owner_id)
        if owner is None:
            return jsonify({"message": "Besitzer wurde nicht gefunden"}), 404
        animal = get_animal_by_id(animal_id)
        if animal is None:
            return jsonify({"message": "Tier wurde nicht gefunden"}), 404
        if animal["owner_id"] is not None:
            current_owner = get_owner_by_id(animal["owner_id"])
            return jsonify({"message": f"Tier gehört bereits {current_owner}"}), 400
        # Falls das alles nicht zutrifft, kann die Adoption stattfinden
        con = get_db_connection()
        cur = con.cursor()
        cur.execute('UPDATE Animals SET owner_id = ? WHERE id = ?', (owner_id, animal_id))
        con.commit()
        con.close()

        return jsonify({"message": f"{owner["name"]} hat {animal["name"]} adoptiert"}), 200
        
