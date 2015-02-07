================================
Generación de fichero modelo 347
================================

El módulo AEAT 340 permite crear la presentación del modelo 347 (Declaración
Anual de Operaciones con Terceros) y la exportación a formato AEAT.

Añade la casilla "Incluir 347" en la pestaña de contabilidad del tercero
para indicar si se debe incluir en el 347. Esta casilla se marca
automáticamente cuando el país del CIF es 'ES' y se desmarca en caso
contrario.

También permite indicar en las líneas de factura si se debe incluir en el
347 y que clave es. En las facturas nuevas se rellena la clave de las
líneas automáticamente, pero hay que recalcularla en las que se crearon
antes de instalar este módulo. Para ello se pueden marcar varias facturas y
ejecutar la acción "Reasignar registros AEAT 347" y marcar casilla Incluir
347 y seleccionar la clave correspondiente, por ejemplo "A - Adquisiciones
de bienes y servicios superiores al límite (1)" para facturas y abonos de
proveedor o la clave "B - Entregas de bienes y servicios superiores al
límite (1)" para facturas y abonos de cliente. Luego hay que ejecutar la
acción "Recalcular registros AEAT 347" para recalcular los importes de cada
línea de factura que deben consignarse en el modelo 347.

El informe 347 se crea desde el menú Contabilidad/Informes/Informe AEAT 347
indicando el ejercicio fiscal y rellenando los datos del informe. El botón
"Calcular" calcula los importes de cada cliente/proveedor a declarar que se
muestran en la pestaña "Registros de terceros". Es importante que todos los
terceros a incluir tengan el CIF anotado. En la pestaña "Registros de
propiedad" se pueden añadir a mano los registros de alquileres de propiedad.

Posteriormente se puede procesar el informe 347 y nos crearà el fichero 347
listo para ser descargado de Tryton y ser enviado a hacienda por vía
telemática.

Basado en la Orden EHA/3012/2008, de 20 de Octubre, por el que se aprueban los
diseños físicos y lógicos del 347.

De acuerdo con la normativa de la Hacienda Española, están obligados a presentar
el modelo 347:

* Todas aquellas personas físicas o jurídicas que no esten acogidas al regimen
  de módulos en el IRPF, de naturaleza pública o privada que desarrollen
  actividades empresariales o profesionales, siempre y cuando hayan
  realizado operaciones que, en su conjunto, respecto de otra persona
  o Entidad, cualquiera que sea su naturaleza o carácter, hayan superado
  la cifra de 3.005,06€ durante el año natural al que se refiere la
  declaración. Para el cálculo de la cifra de 3.005,06 € se computan de
  forma separada las entregas de biene y servicios y las adquisiciones
  de los mismos.
* En el caso de Sociedades Irregulares, Sociedades Civiles y Comunidad de Bienes
  no acogidas el regimen de módulos en el IRPF, deben incluir las facturas sin
  incluir la cuantía del IRPF.
* En el caso de facturas de proveedor con IRPF, no deben ser presentadas en este
  modelo. Se presentan en el modelo 190. Desactivar en la ficha del proveedor
  la opción de "Incluir en el informe 347".

De acuerdo con la normativa no están obligados a presentar el modelo 347:

* Quienes realicen en España actividades empresariales o profesionales sin
  tener en territorio español la sede de su actividad, un establecimiento
  permanente o su domicilio fiscal.
* Las personas físicas y entidades en régimen de atribución de rentas en
  el IRPF, por las actividades que tributen en dicho impuesto por el
  régimen de estimación objetiva y, simultáneamente, en el IVA por los
  régimenes especiales simplificados o de la agricultura, ganadería
  y pesca o recargo de equivalencia, salvo las operaciones que estén
  excluidas de la aplicación de los expresados regímenes.
* Los obligados tributarios que no hayan realizado operaciones que en su
  conjunto superen la cifra de 3.005,06€
* Los obligados tributarios que hayan realizado exclusivamente operaciones
  no declarables.
* Los obligados tributarios que deban informar sobre las operaciones
  incluidas en los libros registro de IVA (modelo 340) salvo que realicen
  operaciones que expresamente deban incluirse en el modelo 347.

http://www.boe.es/boe/dias/2008/10/23/pdfs/A42154-42190.pdf
