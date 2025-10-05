Feature: Subida y organización de archivos en Dropbox mediante chatbot

  Scenario: Subir un archivo temporal
    Given el usuario inicia el flujo del chatbot
    When el usuario selecciona un archivo y lo envía
    Then el sistema guarda el archivo en almacenamiento temporal
    And el chatbot confirma la recepción del archivo

  Scenario: Recolección de datos para renombrado
    Given el usuario ha subido un archivo temporal
    When el chatbot pregunta por tipo de documento, cliente y fecha
    And el usuario responde a todas las preguntas
    Then el sistema genera un nombre de archivo nuevo con esos datos
    And el chatbot muestra el nombre sugerido al usuario

  Scenario: Sugerencia de ruta en Dropbox
    Given el usuario ha respondido a las preguntas
    When el sistema genera la ruta sugerida en Dropbox
    Then el chatbot muestra la ruta sugerida al usuario

  Scenario: Confirmación de subida
    Given el chatbot muestra el nombre y la ruta sugerida
    When el usuario confirma la subida
    Then el sistema sube el archivo a la ruta indicada en Dropbox
    And el chatbot confirma que el archivo fue subido exitosamente

  Scenario: Cancelación de subida
    Given el chatbot muestra el nombre y la ruta sugerida
    When el usuario cancela la subida
    Then el sistema no sube el archivo a Dropbox
    And el chatbot confirma que la acción fue cancelada

  Background:
  Given el usuario ha iniciado sesión en Dropbox

  
