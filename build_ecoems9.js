// Generador de ecoems-9.json desde la Guía CENEVAL 2023
const fs = require('fs');

// Clave oficial (transcrita de las 4 fotos de la hoja de respuestas)
const KEY = {
  1:'C',2:'C',3:'B',4:'B',5:'C',6:'A',7:'C',8:'A',9:'B',10:'A',11:'B',12:'D',13:'C',14:'D',15:'C',16:'D',
  17:'D',18:'C',19:'B',20:'B',21:'B',22:'A',23:'D',24:'A',25:'B',26:'C',27:'D',28:'A',
  29:'B',30:'C',31:'B',32:'B',33:'C',34:'C',35:'D',36:'C',37:'C',38:'C',39:'C',40:'B',
  41:'B',42:'C',43:'A',44:'C',45:'A',46:'B',47:'A',48:'A',49:'D',50:'D',51:'B',52:'B',
  53:'B',54:'B',55:'A',56:'B',57:'B',58:'D',59:'A',60:'B',61:'B',62:'B',63:'D',64:'C',
  65:'A',66:'B',67:'A',68:'A',69:'D',70:'B',71:'D',72:'C',73:'D',74:'C',75:'B',76:'D',77:'B',78:'D',79:'B',80:'C',
  81:'B',82:'D',83:'D',84:'B',85:'D',86:'B',87:'C',88:'D',89:'A',90:'C',91:'B',92:'A',
  93:'C',94:'C',95:'B',96:'C',97:'D',98:'C',99:'A',100:'C',101:'B',102:'A',103:'A',104:'D',
  105:'C',106:'A',107:'A',108:'C',109:'B',110:'A',111:'C',112:'A',113:'C',114:'B',115:'A',116:'B',
  117:'D',118:'D',119:'D',120:'B',121:'C',122:'B',123:'A',124:'C',125:'D',126:'C',127:'C',128:'B'
};

// imágenes:  letter = opciones son figuras (composite A-D dentro de la imagen)
//            fig    = figura en el enunciado, opciones de texto
const LETTER_IMG = new Set([69,70,71,72,73,74,76,95]);
const FIG_IMG = new Set([67,98]);
const LET = {A:'A',B:'B',C:'C',D:'D'};
// Figuras ya convertidas a SVG (theme-adaptive). El resto sigue en PNG temporal.
const SVG_DONE = new Set([67, 98]);
const img = (id)=>`/imagenes_ecoems-9/q${id}.${SVG_DONE.has(id)?'svg':'png'}`;

const ctxOfelia = `Lee con atención el texto y contesta las preguntas 1 a 4.

Hay gente con la que la vida se ensaña, gente que no tiene una mala racha sino una continua sucesión de tormentas. Casi siempre esa gente se vuelve lacrimosa. Cuando alguien la encuentra, se pone a contar sus desgracias, hasta que otra de sus desgracias acaba siendo que nadie quiere encontrársela.

Esto último no le pasó nunca a la tía Ofelia, porque a la tía Ofelia la vida la cercó varias veces con su arbitrariedad y sus infortunios, pero ella jamás abrumó a nadie con la historia de sus pesares. Dicen que fueron muchos, pero ni siquiera se sabe cuántos, y menos las causas, porque ella se encargó de borrarlos cada mañana del recuerdo ajeno.

Era una mujer de brazos fuertes y expresión juguetona, tenía una risa clara y contagiosa que supo soltar siempre en el momento adecuado. En cambio, nadie la vio llorar jamás.

A veces le dolían el aire y la tierra que pisaba, el sol del amanecer, la cuenca de los ojos. Le dolían como un vértigo el recuerdo, y como la peor amenaza, el futuro. Despertaba a media noche con la certidumbre de que se partiría en dos, segura de que el dolor se la comería de golpe. Pero apenas había luz para todos, ella se levantaba, se ponía la risa, se acomodaba el brillo en las pestañas, y salía a encontrar a los demás como si los pesares la hicieran flotar.

Nadie se atrevió a compadecerla nunca. Era tan extravagante su fortaleza, que la gente empezó a buscarla para pedirle ayuda. ¿Cuál era su secreto? ¿Quién amparaba sus aflicciones? ¿De dónde sacaba el talento que la mantenía erguida frente a las peores desgracias?

Un día le contó su secreto a una mujer joven cuya pena parecía no tener remedio.

—Hay muchas maneras de dividir a los seres humanos —le dijo—. Yo los divido entre los que se arrugan para arriba y los que se arrugan para abajo, y quiero pertenecer a los primeros. Quiero que mi cara de vieja no sea triste, quiero tener las arrugas de la risa y llevármelas conmigo al otro mundo. Quién sabe lo que habrá que enfrentar allá.

Ángeles Mastretta (1990). *Mujeres de ojos grandes*, México, Cal y Arena.`;

const ctxNeander = `Lee con atención el texto y contesta las preguntas 5 a 7.

Un ancho y verde valle de la industrial cuenca del Ruhr, en la República Federal Alemana, ostenta a la entrada sobre la carretera la señal siguiente: "Neanderthal". La mente del automovilista se imagina fácilmente unos seres cavernícolas de pobladas cejas que acosan mamuts con palos y piedras y arrastran resignadas mujeres por el cabello.

El valle del Neander es el lugar donde, en 1856, se hallaron los huesos del "Hombre de Neanderthal", el tan traído y llevado eslabón perdido entre el hombre y el mono.

Unos trabajadores que extraían piedra caliza de una cantera desenterraron los huesos. Pensaron que pertenecían a un oso y los regalaron a un maestro de la localidad, Johann Fuhlrott. Éste se dispuso a reconstruir el esqueleto y comprobó que correspondía a una criatura que en condiciones normales podía mantenerse en pie. Sin embargo, parecía un ser mucho más avanzado que el gorila gigante de África, recién descubierto por aquel entonces.

El maestro opinó que los huesos representaban una etapa intermedia entre el mono y el hombre y que pertenecían a una criatura que vivió de 85,000 a 65,000 años, pero a mediados del siglo XIX resultaba inaudito que los antecesores del hombre se balancearan en los árboles. La Biblia decía que Adán y los animales habían sido creados por separado y las palabras del Génesis solían interpretarse entonces de manera literal.

Fuhlrott mostró sus hallazgos al célebre antropólogo alemán profesor Hermann Schaafhausen, de Bonn. Éste quedó asombrado y llevó el esqueleto a una reunión de científicos celebrada en Kassel en 1857.

Fuhlrott presentó un trabajo en la reunión, pero sólo suscitó la indignación y el desprecio de los asistentes. Su principal oponente fue Rudolph Virchow, médico y antropólogo, que denunció a Fuhlrott y declaró que los huesos de Neanderthal, aunque denotaban una fortaleza poco común, habían pertenecido a algún ser deformado por el raquitismo.

En 1859 estalló la bomba que sacudió la mentalidad del mundo. Fue Charles Darwin con su obra *El origen de las especies*, donde se lanzaba el argumento de que el hombre procedía del mono por evolución. Ello confirmaba de algún modo las ideas de Fuhlrott sobre el eslabón perdido.

Virchow y sus seguidores se encontraban entre los muchos hombres de ciencia cuyas ideas se sometían a revisión. Pronto se descubrieron restos óseos, parecidos a los del Hombre de Neanderthal de Fuhlrott, en Gibraltar, Francia, Bohemia y Moravia.

Se demostró que todos estos hallazgos correspondían al último periodo interglaciar, que concluyó hace 65,000 años.

Las aportaciones de Fuhlrott fueron revaloradas, pero para entonces él ya había muerto. El sabio maestro yace cerca del valle de Neanderthal, que nos ha ofrecido alguna luz en el profundo misterio del origen del hombre.

*El gran libro de lo asombroso e inaudito*. Reader's Digest`;

const ctxCartografia = `Lee el siguiente texto y responde.

La cartografía o ciencia que se dedica a elaborar toda clase de mapas es un recurso indispensable para el desarrollo de cualquier nación. Constituye una manera de ver lo que la superficie terrestre presenta en forma de fenómenos y hechos geográficos. La cartografía simplifica la realidad, la cual presenta de manera clara y accesible para casi cualquier persona, dependiendo del tipo de mapas que se trate.

La dificultad de hacer mapas en la antigüedad era enorme, pues no se contaba con los recursos de la fotografía aérea, la cual cambió definitivamente la forma de hacer cartografía. Los primeros mapas se hacían recordando la ubicación relativa de las cosas y lugares. A pesar de todo, la memoria y el ingenio de la gente jugó un papel importante en la historia de los mapas de antaño. El siglo XVII marcó un periodo de transición, las innovaciones impuestas por Copérnico, Kepler y Galileo influyeron en el conocimiento del Universo y del mundo, con ello se inició el empleo de proyecciones cartográficas, introduciendo las matemáticas en la elaboración de mapas.

Armando Aguilar (2001). *Geografía general*, México, Pearson Educación.`;

// q(name, text, [A,B,C,D], extra={ctx, hasImg})
const sections = [
  { subject: 'Habilidad de razonamiento verbal', prefix: 'HV', items: [
    ['Tía Ofelia — arrugarse para arriba', 'Según la definición de la tía Ofelia en la última parte del texto, las personas que "se arrugan para arriba" son las...', ['lacrimosas que se quejan de todo','personas con las que la vida se ensaña','que tienen en la cara las arrugas de la risa','que se ponen a contar sus desgracias'], {ctx:ctxOfelia}],
    ['Tía Ofelia — tema central', 'Identifica el tema central del texto.', ['El reconocimiento del sufrimiento ajeno','El egoísmo de los que tienen mala suerte en la vida','La fortaleza frente a las vicisitudes de la vida','La vida de la tía Ofelia'], {ctx:ctxOfelia}],
    ['Tía Ofelia — sentido figurado', 'Selecciona las frases que en el texto se presentan en sentido figurado.\n\n1. A veces le dolían el aire y la tierra que pisaba, el sol del amanecer, la cuenca de los ojos\n2. Era una mujer de brazos fuertes y expresión juguetona, tenía una risa contagiosa\n3. Le dolían como un vértigo el recuerdo, y como la peor amenaza, el futuro\n4. Quiero que mi cara de vieja no sea triste\n5. Era tan extravagante su fortaleza que la gente empezó a buscarla para pedirle ayuda', ['1, 2','1, 3','2, 3','3, 5'], {ctx:ctxOfelia}],
    ['Tía Ofelia — comparación', 'Identifica la expresión que en el texto establece una comparación.', ['Tener las arrugas de la risa y llevármelas conmigo al otro mundo','Le dolían como vértigo el recuerdo, y como la peor amenaza, el futuro','Pero ella jamás abrumó a nadie con su historia de pesares','Despertaba a media noche con la certidumbre de que se partiría en dos'], {ctx:ctxOfelia}],
    ['Neanderthal — los huesos', 'Los huesos encontrados en el valle de la cuenca del Ruhr...', ['pertenecían al esqueleto de un oso según el profesor','eran desarrollados como los de un gorila gigante','fueron considerados el eslabón perdido','parecían ser de hombres y mujeres cavernícolas'], {ctx:ctxNeander}],
    ['Neanderthal — Darwin respalda', 'Con la publicación de *El origen de las especies*, Charles Darwin respalda las ideas del...', ['maestro de Neander','Génesis de la Biblia','médico y antropólogo Rudolph Virchow','antropólogo Hermann Schaaffhausen'], {ctx:ctxNeander}],
    ['Neanderthal — rehabilitación de Fuhlrott', 'La causa de la rehabilitación del prestigio de Johann Fuhlrott fue...', ['el apoyo brindado por Charles Darwin a sus ideas','el reconocimiento a su sabiduría como maestro','el descubrimiento de nuevos restos óseos','la idea de que la evolución era cierta'], {ctx:ctxNeander}],
    ['Antónimo — anteriores', 'Selecciona la opción cuyo significado es **opuesto** al de la palabra en negritas.\n\nHe vivido cuando he querido: en los siglos **anteriores** y en todos los años de este que corre.', ['posteriores','consecuentes','previos','anticipados']],
    ['Antónimo — avaro', 'Selecciona la opción cuyo significado es **opuesto** al de la palabra en negritas.\n\nÁlvaro es un hombre **avaro**.', ['autoritario','dadivoso','agradecido','tacaño']],
    ['Antónimo — taciturno', 'Selecciona la opción cuyo significado es **opuesto** al de la palabra en negritas.\n\nÚltimamente te he visto muy **taciturno** en clase de Física.', ['comunicativo','conciliador','responsable','acomplejado']],
    ['Sinónimo — conjetura', 'Selecciona la opción cuyo significado es **similar** al de la palabra en negritas.\n\nLa probabilidad de una recesión internacional ha dejado de ser una mera **conjetura** y se ha convertido en una eventualidad inminente.', ['conjura','suposición','certidumbre','seguridad']],
    ['Sinónimo — místicas', 'Selecciona la opción cuyo significado es **similar** al de la palabra en negritas.\n\nDesconocido por muchos, apenas nombrado por referencias, su figura tiene casi connotaciones **místicas**.', ['prosaicas','intolerantes','célebres','espirituales']],
    ['Expresión — aguas veloces', '¿Qué significa la expresión resaltada en la oración?\n\nMiraban con asombro las **aguas veloces** del río.', ['El agua fluye continuamente','El río tiene muy poca agua','La corriente es rapidísima','El agua es constante y fuerte']],
    ['Analogía — pulgar : primero', 'Selecciona la opción cuya relación es similar al ejemplo.\n\nPulgar es a primero como meñique es a...', ['segundo','tercero','cuarto','quinto']],
    ['Analogía — rostro : máscara', 'Selecciona la opción cuya relación es similar al ejemplo.\n\nRostro es a máscara como...', ['casco a cabeza','anteojos a ojos','mano a guante','voz a micrófono']],
    ['Analogía — capote : torero', 'Selecciona la opción cuya relación es similar al ejemplo.\n\nCapote es a torero como...', ['sombrero a charro','bailarina a zapatilla','conductor a automóvil','reata a vaquero']],
  ]},
  { subject: 'Español', prefix: 'ESP', items: [
    ['Nexo de condición', 'Completa la frase con el nexo que indica condición.\n\nEsa puerta no se debe abrir, ___________ haya una emergencia.', ['el hecho de que','de modo que','aunque','a menos que']],
    ['Estrategia publicitaria', '¿Qué estrategia sigue el anunciante para mostrar las cualidades del producto en el anuncio?\n\nTodo es facilidad y felicidad en el hogar con Licuafácil, la licuadora de la era moderna.', ['Mostrar su funcionamiento','Señalar que es novedoso','Exagerar sus ventajas','Indicar que es para el hogar']],
    ['Tema principal — cartografía', '¿Cuál es el tema principal del siguiente texto?', ['Aportaciones de Copérnico, Kepler y Galileo en el siglo XVII que ayudaron a la transición de la cartografía','Qué es la cartografía, para qué se usa y cómo se ha desarrollado a través del tiempo','Dificultad para elaborar mapas en la antigüedad, ya que no se contaba con fotografía aérea','Los primeros mapas se hacían recordando la ubicación relativa de las cosas y los lugares'], {ctx:ctxCartografia}],
    ['Presencia de narrador', '¿En cuál de las siguientes oraciones existe la presencia de un narrador?', ['México es un país que tiene muchos problemas económicos, educativos, etcétera','El niño estaba jugando cuando, de pronto, oyó que alguien le hablaba al oído','¿Cuáles son los problemas que se le pueden presentar a un adolescente en la escuela?','¡Necesito que vayas a decirle a María que no podré ir a verla!']],
    ['Secuencias temporales', 'Completa el enunciado con base en las secuencias temporales.\n\nDebemos escalar la montaña ___________ del amanecer. Recuerden que ___________ estemos abajo la cantidad de oxígeno es mayor, pero a medida que ascendamos tenderá a disminuir. Llegaremos a la cima, permaneceremos media hora y ___________ bajaremos.', ['después - aunque - ahora','antes - mientras - después','después - apenas - finalmente','antes - a pesar de que - finalmente']],
    ['Uso de la coma', 'Selecciona los casos en los cuales se utiliza la coma.\n\n1. Para separar elementos de una oración\n2. Para separar palabras o frases que se intercalan en una oración a modo de explicación\n3. Antes de una cita textual, la cual se escribe entre comillas\n4. Para suplir la ausencia de un verbo o de palabras que se sobrentienden\n5. Para dejar incompleta una frase cuando lo que sigue es obvio', ['1, 2, 4','1, 2, 5','1, 3, 5','2, 3, 4']],
    ['Recurso lingüístico — sucesión/simultaneidad', 'Relaciona el tipo de recurso lingüístico con los ejemplos que le corresponden.\n\n**Recurso lingüístico**\n1. Sucesión\n2. Simultaneidad\n\n**Ejemplo**\na) Mientras\nb) Después\nc) Debido a\nd) Más tarde\ne) Al mismo tiempo', ['1ab, 2cd','1ac, 2de','1ae, 2bc','1bd, 2ae']],
    ['Nexo de continuidad', '¿Cuál nexo funciona para introducir ideas que conserven la continuidad en un texto?', ['Además','Pero','Sin embargo','Mas']],
    ['Copretérito de indicativo', '¿Cuál oración tiene un verbo conjugado en copretérito de indicativo?', ['Nunca imaginé que podrías ayudarme tanto a conseguir mis metas','Cuando estaba cerca de la meta, recordé a todos mis seres queridos','La tolerancia es algo que nunca ha estado en la mente de los jóvenes','La posibilidad que tuviste para ganar nunca estuvo tan cerca como ahora']],
    ['Concordancia sujeto-predicado', 'Las oraciones tienen concordancia entre sujeto y predicado, excepto:', ['La Muralla China tiene 8 852 km de largo y se construyó para proteger al país de los ataques Xiongnu','En 1980, la Unesco declaró al Coliseo de Roma como Patrimonio de la Humanidad','La pirámide de Keops son los únicos sobrevivientes de las siete maravillas del mundo antiguo','En la antigüedad, la ciudadela de Machu Picchu fue utilizada como palacio y santuario religioso']],
    ['Oración subordinada explicativa', '¿Cuál enunciado tiene una oración subordinada que introduce información mediante una explicación?', ['Su objetivo es contar historias utilizando herramientas como control de voz, gestos, velocidad y volumen','Leer y compartir, cada semana, una noticia que pueda ser de interés para los alumnos es una buena estrategia','En los clubes de teatro se leen y se discuten obras teatrales y se realizan dramatizaciones de situaciones cotidianas','El objetivo de este tipo de actividades, como indica el programa de Español, es crear varios espacios para la lectura']],
    ['Pasado de indicativo', '¿Cuál oración está conjugada en pasado de indicativo?', ['Juan y Pedro vieron a qué hora llegó','Hubieras temido a lo desconocido','Lucía había leído novelas de Carlos Fuentes','¿Escribirías para Juan varias canciones?']],
  ]},
  { subject: 'Historia', prefix: 'HIST', items: [
    ['Potencia colonial del siglo XVI', '¿Qué reino se convirtió en la potencia de mayor presencia colonial en el siglo XVI?', ['Francia','España','Portugal','Inglaterra']],
    ['Causas de la Revolución Francesa', 'En 1789, la división estamental de la sociedad y un monarca absoluto sin límites de poder, que se sustenta en el alto pago de impuestos del tercer Estado para mantener los lujos de su corte, fueron causas de la...', ['Independencia de las Trece Colonias','Revolución Rusa','Revolución Francesa','Guerra Austrohúngara y Serbia']],
    ['Socialismo', 'Identifica el sistema de organización social y económica que se basa en la propiedad y administración colectiva o estatal de los medios de producción, defiende la igualdad y el bienestar para todos, mitigando la diferencia entre las clases sociales.', ['Fascista','Socialista','Capitalista','Democrático']],
    ['Culturas mesoamericanas — horizontes', 'Relaciona el momento culminante de las culturas mesoamericanas con el horizonte histórico correspondiente.\n\n**Cultura**\n1. Maya\n2. Olmeca\n3. Mexica\n\n**Horizonte**\na) Preclásico\nb) Clásico\nc) Posclásico', ['1a, 2c, 3b','1b, 2a, 3c','1b, 2c, 3a','1c, 2b, 3a']],
    ['Industria textil en Inglaterra', 'La concentración de la producción textil en Inglaterra durante el siglo XIX ocasionó el surgimiento de...', ['flotas navieras','núcleos rurales','ciudades industriales','tierras de labor']],
    ['Postulados de la Ilustración', 'Selecciona los postulados centrales de la Ilustración.\n\n1. Derecho divino de los reyes\n2. Igualdad de las personas ante la ley\n3. Razón como fuente del conocimiento\n4. Progreso como una ley de la naturaleza\n5. Reconocimiento de la autoridad absoluta del rey', ['1, 2, 4','1, 4, 5','2, 3, 4','2, 3, 5']],
    ['Plan de la no reelección', 'El principio de no reelección, aún vigente en el sistema político mexicano, fue la proclama central del Plan de...', ['Guadalupe','Ayutla','Ayala','San Luis']],
    ['Reforma política de 1990', '¿Cuál es el organismo creado por la reforma política de 1990?', ['Comisión Federal Electoral','Congreso de la Unión','Instituto Federal Electoral','Suprema Corte de Justicia']],
    ['Corrientes culturales del siglo XX', 'Relaciona las corrientes culturales con sus aportaciones en México durante el siglo XX.\n\n**Corriente**\n1. Modernismo\n2. Romanticismo\n\n**Aportación**\na) Los de abajo, Mariano Azuela\nb) A Gloria, Salvador Díaz Mirón\nc) Atardecer en el lago, José María Velasco\nd) La nueva democracia, David Alfaro Siqueiros', ['1ab, 2cd','1ac, 2bd','1ad, 2bc','1bc, 2ad']],
    ['Porfiriato e industria', 'Selecciona tres acciones realizadas por Porfirio Díaz que favorecieron el crecimiento de la industria.\n\n1. Introducción de la electricidad\n2. Cobro de alcabalas\n3. Expansión del ferrocarril\n4. Fomento del sindicalismo\n5. Licencia para importar productos', ['1, 2, 5','1, 3, 4','1, 3, 5','2, 3, 4']],
    ['Iglesia y poder económico en la Nueva España', 'Selecciona los medios que empleó la Iglesia para obtener el poder económico en la Nueva España.\n\n1. Préstamos a comunidades indígenas\n2. Recolección del diezmo\n3. Recepción de un fondo del Vaticano\n4. Productividad agrícola\n5. Donación por obras pías\n6. Desarrollo de la actividad minera', ['1, 2, 6','1, 3, 4','2, 4, 5','3, 5, 6']],
    ['Independencia de Texas', 'Completa el texto.\n\nEn 1836, Texas se declara independiente de México. ___________ intenta someterla, pero al ser derrotado firma los Tratados de ___________ con Samuel Houston, comprometiéndose a que el gobierno mexicano reconoce la independencia texana y que en el río ___________ se establece la frontera.', ['Lerdo - Paz - Colorado','Santa Anna - Velasco - Bravo','Félix Zuloaga - Tacubaya - Nueces','Juárez - Guadalupe Hidalgo - Nueces']],
  ]},
  { subject: 'Geografía', prefix: 'GEO', items: [
    ['Fuentes de energía limpia', 'Selecciona las fuentes de energía limpia.\n\n1. Aprovechamiento de la energía solar\n2. Quema de combustibles fósiles\n3. Quema de leña y carbón\n4. Aprovechamiento de la energía eólica', ['1, 2','1, 4','2, 3','3, 4']],
    ['Sismos y tsunamis', 'Los sismos y tsunamis, como el acontecido en Japón en marzo de 2011, son consecuencia...', ['de los cambios climáticos','de la formación de un nuevo continente','del desplazamiento de las placas tectónicas','de la formación de dorsales submarinas']],
    ['Escala', '¿Cuál es la relación entre la distancia real en un terreno y la representada en un mapa?', ['Escala','Meridiana','Proyección geográfica','Simbología']],
    ['Puerto vulnerable a huracanes', '¿Qué puerto del golfo de México es vulnerable en época de huracanes?', ['Acapulco','Ixtapa-Zihuatanejo','Veracruz','Lázaro Cárdenas']],
    ['Migración', 'La transformación del espacio geográfico está ligada al movimiento de los individuos de su lugar de origen hacia otro con la intención de radicar en él, lo cual tiene implicaciones económicas, sociales y políticas. ¿A qué tipo de fenómeno social se hace referencia?', ['Migración','Inmigración','Transmigración','Desplazamiento']],
    ['Consecuencias de la rotación', 'Selecciona las consecuencias del movimiento de rotación de la Tierra.\n\n1. Sucesión del día y la noche\n2. Estaciones del año\n3. Diferencias horarias\n4. Eclipses', ['1, 2','1, 3','2, 4','3, 4']],
    ['Organización Mundial del Comercio', 'Es una de las instituciones representativas de la globalización. Fue creada en 1995 para regular internacionalmente los intercambios de bienes y servicios.', ['Organización Mundial del Comercio','Unión Europea','Banco Mundial','Fondo Monetario Internacional']],
    ['Subducción', 'Es el desplazamiento de las placas tectónicas en el que una se hunde bajo la otra, ocasionando actividad volcánica y tectónica.', ['Subducción','Expansión','Separación','Falla']],
    ['Industria maquiladora', 'El gran crecimiento demográfico y espacial que se ha presentado en algunas ciudades fronterizas, como Tijuana, Mexicali o Ciudad Juárez, entre otras, se puede entender a partir de la influencia de la industria…', ['pesquera','siderúrgica','agropecuaria','maquiladora']],
    ['Acuerdos comerciales', 'Relaciona los acuerdos comerciales con su característica.\n\n**Acuerdo**\n1. Tratado de Libre Comercio de América del Norte\n2. Foro de Cooperación Económica Asia-Pacífico\n3. Mercado Común del Cono Sur\n4. Unión Europea\n\n**Característica**\na) Se establece una moneda única\nb) No es obligación de los países que conforman este bloque cumplir con los acuerdos\nc) Existe libre circulación de bienes, servicios y factores productivos\nd) Es uno de los pactos comerciales con mayor desigualdad entre sus miembros', ['1b, 2c, 3d, 4a','1c, 2d, 3a, 4b','1d, 2a, 3b, 4c','1d, 2b, 3c, 4a']],
    ['Desintegración de países', 'Completa el texto.\n\nHacia 1991, en Europa se desintegró ___________ debido a devaluaciones económicas, huelgas y guerra civil, dando origen a nuevos países: Croacia, Eslovenia, Macedonia, Bosnia y Herzegovina, Serbia y Montenegro. Otro ejemplo de desintegración es el de ___________, que se extendía en Europa y en Asia, esto se debió a las reformas económicas y políticas, y en consecuencia, se formaron 15 repúblicas independientes. En 2011, también se dio el caso de ___________, que se separó del país original, transformando las fronteras que trazaron las potencias coloniales en este país de África.', ['Checoslovaquia - Turquía - Congo','Yugoslavia - la Unión Soviética - Sudán del Sur','Alemania - Pakistán - Sudáfrica','Hungría - Armenia - Zambia']],
    ['Conflicto palestino-israelí', '¿Cuál es la causa principal del conflicto entre palestinos e israelíes?', ['Económica','Disputa territorial','Ideológica','Cuestiones religiosas']],
  ]},
  { subject: 'Formación cívica y ética', prefix: 'FCE', items: [
    ['Decisión responsable', 'Verónica tiene 14 años y está embarazada, pero no sabe qué hacer, pues no quiere tener un hijo en este momento. Si actúa de forma responsable, ¿cuál es la decisión que debe tomar?', ['Abortar a espaldas de sus padres','Platicar con sus padres de inmediato y pedir su apoyo','Seguir el consejo de sus amigos: irse de su casa y buscar un trabajo','Ocultar su embarazo el tiempo que sea posible']],
    ['Prejuicios morales', 'Un grupo de estudiantes de secundaria organiza un ciclo de conferencias sobre sexualidad y decide invitar a un homosexual que trabaja en una organización no gubernamental a favor de los derechos de los homosexuales. Sin embargo, el director se opone argumentando que tal persona no es una buena influencia para los adolescentes. El razonamiento del director se basa en...', ['información objetiva','prejuicios morales','principios políticos','conceptos legales']],
    ['Persona asertiva (excepto)', 'Son características de una persona asertiva, excepto:', ['tiene miedo, duda al tomar una decisión','habla y actúa con base en los hechos','es autoafirmativa cuidando de no agredir a los demás','es autocrítica, acepta errores y aciertos']],
    ['Violencia psicológica', 'Completa el texto.\n\nAlejandra le dice a su novio que no es físicamente atractivo, que seguramente ninguna otra chica se fijaría en él; en cambio, asegura, ella lo valora por "su interior". Alejandra ejerce violencia ___________ contra su novio.', ['física','psicológica','verbal','económica']],
    ['Participación electoral', 'La participación electoral es una obligación democrática que, como ciudadano, se debe cumplir al elegir...', ['representantes de un partido','representantes políticos','consejeros de gobierno','secretarios de gobierno']],
    ['Desarrollo sustentable (excepto)', 'Son ejemplos de desarrollo sustentable, excepto:', ['reutilizar materias primas','reciclar el papel','evitar el desperdicio de agua','encender luces innecesarias']],
    ['Características del voto democrático', 'Selecciona las características del voto democrático en un proceso electoral.\n\n1. Directo\n2. Libre\n3. Obligatorio\n4. Público\n5. Secreto', ['1, 2, 5','1, 3, 4','1, 3, 5','2, 4, 5']],
    ['Valores de los derechos humanos', 'Selecciona los valores que provienen de los derechos humanos.\n\n1. Dignidad humana\n2. Libertad de los individuos\n3. Solidaridad internacional\n4. Respeto a la diversidad cultural\n5. Generosidad con los demás', ['1, 2, 3','1, 2, 4','1, 4, 5','2, 3, 5']],
    ['Conciencia moral individual', '¿Qué es la conciencia moral individual?', ['Forma correcta de actuar ante cualquier situación que se presente','Facultad que permite reconocer si las conductas propias son correctas o no','Compromiso de reconocer y aceptar los actos propios y sus consecuencias','Cualidad de saber decidir cómo actuar ante circunstancias determinadas']],
    ['Voto universal', 'A una persona se le niega el derecho a votar, con el argumento de que es de edad avanzada. Esto constituye una violación, porque el voto es...', ['directo','universal','secreto','libre']],
    ['Violencia psicológica (amenaza)', 'Los padres de Jimena han amenazado con golpearla si reprueba alguna materia. Esta situación es un ejemplo de violencia...', ['física','verbal','económica','psicológica']],
    ['Plebiscito', 'Se convoca a un plebiscito cuando la sociedad...', ['necesita la elección de gobernantes por medio del sufragio','requiere entregar una iniciativa de ley al Poder Legislativo','es consultada por el gobierno en torno a acciones por realizar','desea externar desacuerdo respecto a alguna decisión gubernamental']],
  ]},
  { subject: 'Habilidad de razonamiento matemático', prefix: 'HM', items: [
    ['Sucesión numérica', 'Selecciona la opción que contenga el término que sigue en la sucesión presentada.\n\n−34, −33, −23, −22, −12...', ['−11','−10','−8','−2']],
    ['Sucesión numérica', 'Selecciona la opción que contenga el término que sigue en la sucesión presentada.\n\n35, 27, 19, 11...', ['1','3','4','5']],
    ['Sucesión de figuras (documentos)', '¿Cuántos documentos debe haber en la séptima figura?', ['28','56','60','70'], {img:true}],
    ['Término 13 de la serie', '¿Cuál es el término número 13 de la serie?\n\n$\\dfrac{19}{3}, \\dfrac{17}{3}, 5...$', ['$-\\dfrac{5}{3}$','$-\\dfrac{3}{3}$','$-\\dfrac{1}{3}$','$\\dfrac{1}{3}$']],
    ['Completa la serie de figuras', 'Selecciona la opción que completa la serie presentada.', null, {img:true}],
    ['Completa la serie de figuras', 'Selecciona la opción que completa la serie presentada.', null, {img:true}],
    ['Completa la serie de figuras', 'Selecciona la opción que completa la serie presentada.', null, {img:true}],
    ['Completa la serie de figuras', 'Selecciona la opción que completa la serie presentada.', null, {img:true}],
    ['Figura diferente tras rotación', '¿Cuál figura es diferente, aun después de haberla rotado?', null, {img:true}],
    ['Otra vista de la figura', '¿Cuál imagen representa otra vista de la figura?', null, {img:true}],
    ['Seis triángulos equiláteros', 'Si tenemos 6 triángulos equiláteros, tomamos un vértice de cada uno de ellos y los juntamos sin encimarlos, ¿qué figura se forma?', ['Dodecágono','Hexágono','Trapecio','Rectángulo']],
    ['Plantilla — vista superior', 'Al armar la plantilla, ¿cómo se ve la figura desde la parte superior?', null, {img:true}],
    ['Tres enteros consecutivos', 'Si la suma de 3 números enteros consecutivos es 69, ¿cuál es su producto?', ['10 626','12 144','12 167','13 800']],
    ['Ceros del 101 al 200', 'En una calle cuyas casas están numeradas de manera continua del 101 al 200 se van a colocar números de metal. ¿Cuántos ceros se necesita comprar?', ['9','11','18','20']],
    ['Mezcla de pintura', 'Un señor está pintando su casa. Para obtener el tono que deseaba mezcló 4 L de pintura blanca con 7 de pintura azul. Se le acabó la pintura cuando aún no terminaba de pintar, así que compró otro litro de pintura azul. ¿Cuántos litros de pintura blanca debe agregar para que quede del mismo tono que la mezcla anterior?', ['$1.0$','$\\dfrac{4}{7}$','$\\dfrac{1}{2}$','$4.7$']],
    ['Escala 1:64', 'Un carrito de juguete tiene impresa la escala 1:64. Si el largo del carrito mide 7 cm, ¿cuál es el largo del auto real?', ['0.448 cm','3.48 m','4.48 m','5.48 m']],
  ]},
  { subject: 'Matemáticas', prefix: 'MAT', items: [
    ['Fracción equivalente', '¿Cuál es la fracción equivalente a $\\dfrac{3}{15}$?', ['$\\dfrac{1}{3}$','$\\dfrac{1}{5}$','$\\dfrac{1}{4}$','$\\dfrac{9}{18}$']],
    ['Moda', 'Un alumno obtuvo las siguientes calificaciones: 6, 7, 7, 7, 8, 8, 9, 9, 9, 9, 10, 10. ¿Cuál es la moda?', ['7.00','8.25','8.50','9.00']],
    ['Perímetro en lenguaje algebraico', 'El perímetro de un triángulo obtuso es igual a la suma de sus tres lados, lo cual, expresado en lenguaje algebraico, es...', ['$3a$','$2a + b$','$a^3$','$a + b + c$']],
    ['Ecuación del terreno', '¿Qué ecuación describe el problema?\n\nUn terreno rectangular tiene 5 m más de largo que de ancho y un área de 500 m².', ['$x^2 + 5x + 500 = 0$','$x^2 + 5x - 500 = 0$','$5x^2 - 500 = 0$','$4x - 490 = 0$']],
    ['Ganancia o pérdida', 'Una compañía registra las entradas y salidas de recursos durante 3 días. El lunes tiene ventas por 4,500 pesos y gastos por 1,200 pesos. El martes vende 700 pesos y gasta 1,000 pesos y el miércoles presenta ventas por 2,400 pesos y gastos por 1,300 pesos. ¿Cuál es la ganancia o pérdida de los días descritos?', ['−4,100 pesos','−1,700 pesos','1,700 pesos','4,100 pesos']],
    ['Precio original con sobreprecio', 'Para obtener ganancias, una empresa vende sus productos 30% más caros de su costo. Si un cliente compra un paquete en 39 pesos, ¿cuál es su precio original?', ['27 pesos','30 pesos','130 pesos','333 pesos']],
    ['Porcentaje de descuento', 'María compró un pantalón que tenía descuento y pagó 285 pesos. Si el pantalón tenía un precio original de 380 pesos, ¿de cuánto fue el descuento?', ['0.25%','0.75%','25.00%','33.00%']],
    ['Gusano en el mástil', '¿Cuántos días tarda un gusano en llegar a la cima de un mástil que mide 20 m, si diario sube 4 y resbala 1?', ['4','5','6','7']],
    ['Tangente del ángulo', 'En un triángulo rectángulo el cateto opuesto al ángulo A mide 3 unidades, el cateto adyacente 4 y la hipotenusa 5. ¿Cuál es el valor de la tangente del ángulo A?', ['$\\dfrac{3}{4}$','$\\dfrac{3}{5}$','$\\dfrac{4}{5}$','$\\dfrac{5}{4}$']],
    ['Resultado de la operación', '¿Cuál es el resultado de la operación?\n\n$-\\left[\\dfrac{4}{5} - \\dfrac{2}{3}\\left(\\dfrac{4}{5} + \\dfrac{1}{2}\\right)\\right] \\div \\dfrac{1}{5}$', ['$-\\dfrac{25}{3}$','$-\\dfrac{1}{3}$','$\\dfrac{1}{3}$','$\\dfrac{25}{3}$']],
    ['Encuesta de colores de camisa', 'Se aplicó una encuesta de opinión a 150 hombres para conocer cuál color de camisa prefieren y se obtuvo la información que aparece en la tabla. Con base en ésta se interpreta que...\n\n| Color de camisa | Frecuencia |\n|---|---|\n| Blanco | 62 |\n| Azul | 43 |\n| Café | 14 |\n| Negro | 10 |\n| Rojo | 9 |\n| Rosa | 8 |\n| Amarillo | 4 |', ['los hombres entrevistados podían elegir más de un color de camisa','los hombres entrevistados sólo eligieron un color de camisa','los colores café y negro son preferidos por 24% de la población','10% de la población entrevistada prefiere el color negro']],
    ['Prioridad de operaciones', 'Resuelve la expresión respetando la prioridad de operaciones.\n\n$\\dfrac{\\dfrac{3}{4} + \\dfrac{7}{8}}{\\dfrac{2}{5} - \\dfrac{8}{9}}$', ['$-\\dfrac{585}{176}$','$-\\dfrac{450}{192}$','$\\dfrac{585}{464}$','$\\dfrac{450}{320}$']],
  ]},
  { subject: 'Física', prefix: 'FIS', items: [
    ['Fuerza sobre la pelota', 'Al patear una pelota de futbol que se encuentra en reposo, ésta se mueve como consecuencia de la ___________ que actúa sobre ella.', ['potencia','aceleración','fuerza','fricción']],
    ['Calor y temperatura', 'Completa el texto.\n\nSe tienen dos vasos de agua a temperatura ambiente; uno con 10 y el otro con 100 mL. Se colocan simultáneamente en hornillas iguales y después de algunos minutos se observa que tienen temperaturas ___________, a pesar de que a ambos se les han suministrado ___________ cantidades de calor.', ['iguales – iguales','iguales – diferentes','diferentes – iguales','diferentes – diferentes']],
    ['Gráfica posición-tiempo', '¿Qué gráfica posición-tiempo corresponde con los datos de la tabla?\n\n| Posición (m) | Tiempo (s) |\n|---|---|\n| 2 | 1 |\n| 6 | 3 |\n| 8 | 5 |\n| 12 | 7 |\n| 13 | 9 |', null, {img:true}],
    ['Frecuencia del movimiento ondulatorio', 'Completa el enunciado.\n\nUna de las características que describe al movimiento ondulatorio es ___________, que consiste en el número de vibraciones por unidad de tiempo.', ['el periodo','la velocidad','la frecuencia','la longitud de onda']],
    ['Descomposición de la luz (excepto)', 'Estos colores resultan de la descomposición de un rayo de luz al incidir sobre un prisma, excepto:', ['amarillo','azul','verde','café']],
    ['Aceleración y gráfica velocidad-tiempo', 'Relaciona el tipo de aceleración de un cuerpo con la gráfica de velocidad-tiempo.\n\n**Tipo de aceleración**\n1. Cero\n2. Negativa\n3. Positiva', ['1a, 2b, 3c','1a, 2c, 3b','1b, 2a, 3c','1b, 2c, 3a'], {img:true}],
    ['Modelo cinético de partículas', 'Es un postulado del modelo cinético de partículas.', ['Toda la materia está constituida por partículas','Las partículas están siempre en reposo','Los choques entre las partículas y de éstas contra las paredes del recipiente son con pérdida de energía','La distancia entre partículas es demasiado pequeña comparada con el tamaño de cada una']],
    ['Radiación electromagnética y su uso', 'Relaciona cada tipo de radiación electromagnética con su uso.\n\n**Radiación**\n1. Infrarroja\n2. Rayos gamma\n3. Luz ultravioleta\n\n**Uso**\na) Desinfecta equipos y materiales quirúrgicos\nb) Manda la señal para encender la televisión y lee discos compactos\nc) Se ocupa en procedimientos para la detección de cáncer en los huesos', ['1a, 2b, 3c','1b, 2a, 3c','1b, 2c, 3a','1c, 2a, 3b']],
    ['Interacción entre imanes', 'Un estudiante acerca dos imanes por sus polos norte y observa una interacción entre ellos, manifestándose como una fuerza de...', ['contracción','repulsión','fricción','atracción']],
    ['Presión en los gases', 'De acuerdo con el modelo cinético de partículas, ¿cuál enunciado define la presión en los gases?', ['La fuerza ejercida sobre las paredes del recipiente por el choque de las partículas','El producto de la densidad molar por la altura y la aceleración de la gravedad','La suma de las presiones manométricas totales de las partículas en el contenedor','La fuerza ejercida por las partículas dividida entre el volumen que ocupa el gas']],
    ['Fuerza de atracción gravitacional', '¿Cuál ecuación relaciona el peso de un cuerpo ($mg$) con la fuerza de atracción gravitacional que éste experimenta a una distancia ($R$) del centro de la Tierra que tiene una masa ($M$)? Considera $G$ como la constante de gravitación universal.', ['$\\dfrac{GMm}{R^2}$','$\\dfrac{GM}{R^2}$','$\\dfrac{Gm}{MR^2}$','$GMmR^2$']],
    ['Transferencia de energía (agua y leche)', 'A una taza con agua a 40 °C se le agrega leche a temperatura ambiente de 15 °C. El efecto que se observa es que...', ['la leche le pasa temperatura al agua','la leche absorbe la temperatura del agua','el agua recibe energía del aire','el agua transfiere energía a la leche']],
  ]},
  { subject: 'Química', prefix: 'QUI', items: [
    ['Cloruro de sodio (compuesto)', 'El cloruro de sodio se forma por la combinación de sodio y cloro. Se puede afirmar que el cloruro de sodio es...', ['una mezcla homogénea','un elemento','un compuesto','una mezcla heterogénea']],
    ['Enlace iónico y covalente', 'Completa el texto.\n\nEn un enlace ___________ existe transferencia de electrones, mientras que en un enlace ___________ los electrones se comparten.', ['iónico - covalente','covalente - iónico','metálico - iónico','iónico - metálico']],
    ['Reacción reversible', 'Cuando en una reacción química aparecen dos flechas paralelas en sentido contrario, es...', ['reversible','de fusión','de fisión','irreversible']],
    ['Expresión química y ejemplo', 'Relaciona cada expresión química con su ejemplo.\n\n**Expresión**\n1. Ion\n2. Átomo\n3. Molécula\n\n**Ejemplo**\na) Cl₂\nb) Ca²⁺\nc) He', ['1a, 2c, 3b','1b, 2a, 3c','1b, 2c, 3a','1c, 2b, 3a']],
    ['Partículas que unen átomos', '¿Cuáles son las partículas subatómicas responsables de mantener unidos a los átomos de un compuesto?', ['Neutrones','Electrones','Protones','Neutrinos']],
    ['Reacción de neutralización', 'Es un ejemplo de una reacción de neutralización.', ['NaOH + HCl → NaCl + H₂O','CaI₂ + Cl₂ → CaCl₂ + I₂','NaCl + H₂SO₄ → NaHSO₄ + HCl','Mg + 2HCl → MgCl₂ + H₂']],
    ['Propiedad — cantidad de azúcar', 'Cuando se habla de la cantidad de azúcar en un recipiente, ¿a qué propiedad se hace referencia?', ['Densidad','Dureza','Masa','Peso']],
    ['Conservación de la masa (cambio físico)', '¿En cuál ejemplo se puede comprobar que la masa se conserva en un cambio físico?', ['Martha agrega 10 g de cloruro de sodio a 50 g de agua para formar 60 g de una solución salina','Sergio quema totalmente 3 g de cinta de magnesio en un crisol y obtiene 5 g de óxido de magnesio','Claudia une 10 g de oxígeno y 10 g de hidrógeno mediante una descarga eléctrica y obtiene 20 g de agua','Marcos calienta 2 g de azufre con 2 g de hierro y obtiene 4 g de sulfuro de hierro II']],
    ['Cambios químicos (excepto)', 'Los siguientes ejemplos representan cambios químicos, excepto:', ['quemar una hoja de papel','oxidación de una manzana','solidificación del agua','respiración aeróbica']],
    ['Orden de la tabla periódica', 'Los elementos en la tabla periódica actual se disponen de acuerdo con el orden creciente...', ['de la masa atómica','del número atómico','del radio atómico','de la electronegatividad']],
    ['Reacción de oxidación-reducción', '¿Cuál ejemplo corresponde a una reacción de oxidación-reducción?', ['Tostar pan','Hervir agua','Estirar un resorte','Congelar jugo de naranja']],
    ['Cambios de fase en la destilación', 'La destilación del agua, para su purificación, se puede realizar en el laboratorio. Se calienta y sus vapores se hacen pasar por un sistema refrigerante.\n\n¿Qué cambios de fase sufre el agua durante la destilación?', ['Evaporación y licuefacción','Evaporación y condensación','Fusión y cristalización','Sublimación y condensación']],
  ]},
  { subject: 'Biología', prefix: 'BIO', items: [
    ['Alimentos con más fibra', 'Son los alimentos que más fibra contienen.', ['Carnes','Frutas','Verduras','Cereales']],
    ['Selección natural — científico', 'Científico que explica la evolución de las especies a través de la selección natural.', ['Gregor Mendel','Robert Hooke','Louis Pasteur','Charles Darwin']],
    ['Plato del Bien Comer — menú', 'Selecciona el menú del día con base en el Plato del Bien Comer.', ['Pechuga empanizada con puré de papa y arroz con leche','Enchiladas de mole con pollo, agua de jamaica y fruta de temporada','Hamburguesa con papas a la francesa, refresco y helado de chocolate','Sopa de verdura, carne asada con frijoles, tortillas de maíz, agua de melón y manzana']],
    ['Autótrofos', 'A los organismos capaces de fabricar su alimento se les llama...', ['parásitos','autótrofos','holozoicos','heterótrofos']],
    ['Pérdida de diversidad (excepto)', 'Son factores que provocan la pérdida de diversidad biológica, excepto:', ['los cambios de clima','las erupciones volcánicas','la creación de reservas naturales','los incendios forestales']],
    ['Proceso de la reacción', '¿Qué proceso representa la siguiente reacción?\n\nDióxido de carbono + Agua + Luz → Glucosa + Oxígeno', ['Respiración','Fotosíntesis','Fermentación','Combustión']],
    ['Aletas en ballenas (adaptación)', 'El surgimiento de las aletas en las ballenas es un ejemplo del proceso evolutivo llamado...', ['adaptación','especiación','selección natural','diversificación']],
    ['Manipulación genética', 'Selecciona las características que distinguen a la manipulación genética en la investigación científica.\n\n1. Análisis de la selección natural y la evolución de especies\n2. Estudio de la estructura del ADN de las especies\n3. Identificación de la información contenida en los cromosomas\n4. Estimación de la deriva génica en las poblaciones\n5. Experimentación de recombinación de ADN entre especies', ['1, 2, 4','1, 3, 4','2, 3, 5','3, 4, 5']],
    ['Dieta balanceada — mayor proporción', '¿Cuál grupo de alimentos se debe incluir en mayor proporción en una dieta balanceada?', ['Frutas','Carnes','Cereales','Vegetales']],
    ['Compuesto faltante (respiración)', '¿Cuál es el compuesto faltante en la reacción de respiración?\n\nGlucosa + Oxígeno → Dióxido de carbono + Agua + ___________', ['ADP','ADN','ATP','ARN']],
    ['Anticonceptivos naturales — ventajas', '¿Cuáles son las ventajas del uso de métodos anticonceptivos naturales?', ['Están disponibles sin prescripción médica y pueden suministrarse por distintas vías','Son de fácil colocación y efectivos durante varios años','Son gratuitos y no generan reacciones secundarias porque carecen de hormonas','Protegen contra ETS, pero sus efectos pueden ser irreversibles']],
    ['Calentamiento global — emisión', 'Completa el texto.\n\nLa emisión de ___________ a la atmósfera es una de las causas del calentamiento global.', ['plomo','metano','óxido de nitrógeno','clorofluorocarbono']],
  ]},
];

// Ensamble
let id = 0;
const outSections = sections.map(sec => {
  const questions = sec.items.map((it, i) => {
    id++;
    const [name, text, opts, extra={}] = it;
    const q = { id, topic: `${sec.prefix}.${i+1}`, topic_name: name, text };
    // opciones
    if (LETTER_IMG.has(id)) {
      q.options = {...LET};
    } else if (opts) {
      q.options = {A:opts[0], B:opts[1], C:opts[2], D:opts[3]};
    } else {
      throw new Error(`q${id} sin opciones y no es LETTER_IMG`);
    }
    q.answer = KEY[id];
    if (extra.ctx) q.context = extra.ctx;
    if (extra.img || LETTER_IMG.has(id) || FIG_IMG.has(id)) q.image = img(id);
    return q;
  });
  return { subject: sec.subject, questions };
});

const exam = {
  exam: {
    title: 'ECOEMS 9',
    group: 'Ingreso a nivel medio superior',
    date: '2026-06-20',
    total_questions: id,
    students: ["Ari","Alexander","Axel","Citlaly","Conchita","Julio","Kevin","Leah","Marley","Miguel Ángel","Rafaela","Regina","Roxanna","Sofía","Ximena","Yuli"],
    sections: outSections,
  }
};

fs.writeFileSync('ecoems-9.json', JSON.stringify(exam, null, 2) + '\n');

// Validaciones
const counts = outSections.map(s => `${s.subject}: ${s.questions.length}`);
console.log('Total preguntas:', id);
counts.forEach(c => console.log('  -', c));
const allQ = outSections.flatMap(s=>s.questions);
const missingAns = allQ.filter(q=>!q.answer);
console.log('Sin respuesta:', missingAns.length ? missingAns.map(q=>q.id).join(',') : 'ninguna');
const badAns = allQ.filter(q=>!['A','B','C','D'].includes(q.answer));
console.log('Respuesta inválida:', badAns.length ? badAns.map(q=>q.id).join(',') : 'ninguna');
const withImg = allQ.filter(q=>q.image).map(q=>q.id);
console.log('Con imagen ('+withImg.length+'):', withImg.join(','));
