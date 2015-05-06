AEAT 347
========

Para poder calcular el informe AEAT 347 (operaciones con terceros de más de 3000 eur o en efectivo)
hay que instalar el módulo aeat_347. Desde el menú "Contabilidad/Informes/Informe AEAT 347" se puede crear
un nuevo informe y darle al botón Calcular.

Si al calcular no encuentra todavía ningún registro de tercero porqué hay que hacer reasignaciones
y recálculos en las facturas 2014 y 2015.

Este módulo además añade la casilla "Incluir 347" en la pestaña de contabilidad del tercero para indicar
si se debe incluir en el 347, y en las líneas de factura también se indica si se debe incluir en el 347
y que clave es. En las facturas nuevas se rellena automáticamente la clave de las líneas, pero hay que
recalcularla en las que se crearon antes de instalar este módulo.

Hay que ir a las factura de cliente, pestaña Todas y filtrar las del 2014 (luego lo mismo con las del 2015).
Seleccionar todas con Ctrl+A (si hay más de 1000 hay que hacerlo de 1000 en 1000) y ejecutar la acción
"Reasignar registros AEAT 347" y marcar casilla Incluir 347 y seleccionar la clave "B - Entregas de bienes
y servicios superiores al límite (1)". Luego hay que volver a marcar todas las facturas y ejecutar la acción
"Recalcular registros AEAT 347". Así nos recalcularà los importes de cada factura que deben consignarse
en el modelo 347.

Luego se repite el mismo proceso para las facturas de abono de cliente. I después con las de proveedor
y abono de proveedor, pero seleccionando la clave "A - Adquisiciones de bienes y servicios superiores
al límite (1)".

Tener en cuenta que estos pasos marcarán todas las facturas y abonos de cliente y proveedor de 2014
y 2015 para ser consignadas en el 347 mediante las 2 claves estándares. Si alguna factura es de
cliente/proveedor estranjero (CIF que no empieza con ES), o si es una subvención o adquisión de adm.
pública hay que poner otra clave o no consignar en el 347. Se pueden corregir haciendo los dos pasos
anteriores, reasignar y luego recalcular los registros AEAT 347 para ponerles las claves correctas
o consignar o no en el 347.

Una vez hecho esto ya se puede crear el informe 347 desde el menú Contabilidad/Informes/Informe AEAT 347,
indicando el ejercicio fiscal y rellenando los datos del informe. Pulsamos el botón "Calcular" y en la
pestaña "Registros de terceros" aparece el resumen de los cálculos, con los importes de cada cliente/proveedor
a declarar. Es importante que todos los terceros a incluir tengan el CIF anotado. En la pestaña "Registros
de propiedad" se pueden añadir a mano los registros de alquileres de propiedad.

Posteriormente se puede procesar el informe 347 y nos crearà el fichero 347 listo para ser descargado de
Tryton y ser enviado a hacienda por vía telemática.
