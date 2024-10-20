// Have you run it twice? Use `MATCH (n) WHERE (n:Person OR n:Movie) DETACH DELETE n` to start over.

//atributos necesarios del dataset:
//-id, -name, -description, -ingestion_date, -ingestion_info, -type
//dataset->storedIn->Zone

//atributos necesarios de Zone:
//-id_zone, -name

//atributos necesarios de cada Documento de la coleccion:
//-id_document
//documento->belongsToColecction->dataset

//atributos necesarios de cada Fields:
//-id_field, -name, -type
// i)fields->belongsToDoc->documento
// ii)documento->belongsToField->field

//## Ver agregar atributos de measures ##

//Carga de Pelicula1 con los atributos necesarios
//#Supongamos que está actualmente
// almacenado en la trusted

// CREATE (raw_zone:Zone { name:"raw_zone" })
// CREATE (trusted_zone:Zone { name:"trusted_zone" })
// CREATE (refined_zone:Zone { name:"refined_zone" })

// CREATE (ColeccionPeliculas_id1:Dataset:Collection
// {
//   name: "Colección Películas",
//   description: "Colección que contiene información sobre 3 películas",
//   ingestion_date: "2024-10-11",
//   ingestion_info: "(Acá iría la url/uri/referencia de donde se generó o como llegó a la ingestion zone) Colección de archivos JSONs generada manualmente",
//   type: "json file"
//   })
//   WITH ColeccionPeliculas_id1, trusted_zone
//   CREATE (ColeccionPeliculas_id1)-[:STOREDIN]->(trusted_zone)
  
// // Hecho solo para Pelicula1
//   CREATE (Pelicula1:Documents {
//     id_document: "Inception"
//     })
//     CREATE (ColeccionPeliculas_id1)<-[:BELONGSTOCOLLECTION]-(Pelicula1)
//     WITH ColeccionPeliculas_id1, Pelicula1
    
// // Crear nodo :Fields para "title" y relacionarlo con Pelicula1
//     CREATE (FieldTitle:Fields { name: "title", type: "String" })
//     CREATE (FieldTitle)-[:BELONGSTODOCUMENT]->(Pelicula1)
//     WITH ColeccionPeliculas_id1, Pelicula1
    
// // Como some_info es de tipo Document además de crear el :Fields
// //tenemos que crear el :Documents según entiendo del modelo
//     CREATE (FieldSomeInfo:Fields { id_field:"field-some_info", name: "some_info", type: "Document" })
//     CREATE (DocumentoSomeInfo:Documents { id_document: "document-some_info" })
//     CREATE (FieldSomeInfo)-[:BELONGSTODOCUMENT]->(Pelicula1)
//     CREATE (FieldSomeInfo)-[:BELONGSTODOCUMENT]->(DocumentoSomeInfo)
//     WITH ColeccionPeliculas_id1, Pelicula1, DocumentoSomeInfo
    
// // Ahora si agregamos los Fields del documento embebido
//     CREATE (FieldReleaseDate:Fields { name: "release_date", type: "String" })
//     CREATE (FieldReleaseDate)-[:BELONGSTODOCUMENT]->(DocumentoSomeInfo)
//     CREATE (FieldAdult:Fields { name: "adult", type: "Boolean" })
//     CREATE (FieldAdult)-[:BELONGSTODOCUMENT]->(DocumentoSomeInfo)
//     CREATE (FieldImdbId:Fields { name: "imdb_id", type: "String" })
//     CREATE (FieldImdbId)-[:BELONGSTODOCUMENT]->(DocumentoSomeInfo)
    
//     WITH ColeccionPeliculas_id1, Pelicula1
    
// // Se crea genres (CREO QUE HAY QUE HACER LO MISMO QUE PARA some_info)
//     CREATE (FieldGenres:Fields { name: "genres", type: "Array" })
//     CREATE (FieldGenres)-[:BELONGSTODOCUMENT]->(Pelicula1)



// //Medidas de calidad

// MERGE (f:Fields {id_field: "id_field", name: "name", type: "type"})
// MERGE (m:Measure {id_measure: 'id_measure', measure: 'measure_value', date: 'date_value'})
// MERGE (f)-[:FieldValueMeasure]->(m)

// MERGE (f:Fields {id_field: "id_field", name: "name", type: "type"})
// MERGE (m:Measure {id_measure: 'id_measure', measure: 'measure_value', date: 'date_value'})
// MERGE (f)-[:FieldMeasure]->(m)



// Insertar schema

// Create a Collection node to represent the JSON schema
MERGE (c:Collection {name: "JsonSchemaCollection"})

// Insert the top-level Field for `id`
MERGE (idField:Field {name: "id", type: "integer"})
MERGE (idField)-[:belongsToSchema]->(c)

// Insert the top-level Field for `contacto`
MERGE (contactoField:Field {name: "contacto", type: "object"})
MERGE (contactoField)-[:belongsToSchema]->(c)

// Insert nested fields inside `contacto`
MERGE (cityField:Field {name: "city", type: "string"})
MERGE (cityField)-[:belongsToField]->(contactoField)

MERGE (streetField:Field {name: "street", type: "string"})
MERGE (streetField)-[:belongsToField]->(contactoField)

MERGE (emailField:Field {name: "email", type: "string"})
MERGE (emailField)-[:belongsToField]->(contactoField)

RETURN c, idField, contactoField, cityField, streetField, emailField
