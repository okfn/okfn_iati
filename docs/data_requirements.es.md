# Requisitos de Datos IATI para el Banco de Desarrollo

## Introducción

Este documento describe los datos necesarios de su organización para generar archivos XML conformes con IATI (Iniciativa Internacional para la Transparencia de la Ayuda). IATI es un estándar global para publicar datos transparentes sobre actividades de desarrollo y ayuda humanitaria.

Los datos que proporcione se transformarán en formato XML IATI y se publicarán en el Registro IATI, haciendo que sus actividades de desarrollo sean transparentes y accesibles para la comunidad internacional.

## ¿Qué datos podemos publicar?

IATI está diseñado para rastrear el flujo de recursos de desarrollo y ayuda humanitaria. Como banco de desarrollo, puede publicar información sobre una amplia gama de instrumentos financieros y actividades, incluyendo:

- **Operaciones de préstamos**: Tanto préstamos concesionales como no concesionales a gobiernos, empresas estatales y entidades del sector privado
- **Programas de donaciones**: Donaciones de asistencia técnica, subvenciones para investigación y otros financiamientos no reembolsables
- **Inversiones de capital**: Inversiones directas en empresas y fondos que apoyan objetivos de desarrollo
- **Esquemas de garantías**: Garantías financieras que ayudan a movilizar recursos adicionales
- **Acuerdos de cofinanciamiento**: Proyectos financiados conjuntamente con otras instituciones de desarrollo
- **Cooperación técnica**: Servicios de asesoría y programas de desarrollo de capacidades
- **Fondos fiduciarios**: Gestión de recursos en nombre de donantes para propósitos específicos
- **Financiamiento basado en políticas**: Apoyo para reformas políticas e institucionales
- **Financiamiento de respuesta a emergencias**: Financiamiento rápido para recuperación de desastres y resiliencia
- **Iniciativas de integración regional**: Proyectos transfronterizos que promueven el desarrollo regional

IATI permite rastrear todas las etapas de estas operaciones, desde la aprobación inicial hasta la implementación y resultados, proporcionando una visión integral de su cartera de desarrollo y sus impactos. Esta transparencia ayuda a demostrar el valor del trabajo de su institución al tiempo que facilita la coordinación con otros socios de desarrollo.

## Formato de Datos

Por favor, proporcione sus datos en formato **CSV** o **Excel**, con una fila por actividad. Las secciones a continuación explican qué información necesitamos para cada actividad.

## Información Esencial de Actividades

Para cada actividad de desarrollo (proyecto, programa o intervención), necesitamos:

### 1. Identificación Básica

| Campo | Descripción | Formato | Requerido | Ejemplo |
|-------|-------------|---------|-----------|---------|
| Identificador de Actividad | Código único para esta actividad | Texto (debe comenzar con el ID de su organización) | Sí | `XM-DAC-12345-PROJECT001` |
| Título de la Actividad | Nombre de la actividad | Texto | Sí | "Programa de Apoyo a Pequeñas Empresas" |
| Descripción de la Actividad | Descripción detallada de lo que implica la actividad | Texto | Sí | "Este programa apoya a pequeñas empresas en áreas rurales mediante microfinanzas y capacitación" |
| Estado de la Actividad | Estado actual de la actividad | [Código ActivityStatus de IATI](https://iatistandard.org/en/iati-standard/203/codelists/activitystatus/) (1=Planificación, 2=Implementación, etc.) | Sí | 2 (Implementación) |

### 2. Fechas

| Campo | Descripción | Formato | Requerido | Ejemplo |
|-------|-------------|---------|-----------|---------|
| Fecha de Inicio Planificada | Cuándo está programado el inicio de la actividad | AAAA-MM-DD | Sí | 2023-01-15 |
| Fecha de Inicio Real | Cuándo comenzó realmente la actividad | AAAA-MM-DD | Si ha comenzado | 2023-01-20 |
| Fecha de Finalización Planificada | Cuándo está programado el fin de la actividad | AAAA-MM-DD | Sí | 2024-01-15 |
| Fecha de Finalización Real | Cuándo finalizó realmente la actividad | AAAA-MM-DD | Si está completada | - |

### 3. Organizaciones Involucradas

#### 3.1. Su Organización (Organización Informante)

| Campo | Descripción | Formato | Requerido | Ejemplo |
|-------|-------------|---------|-----------|---------|
| ID de la Organización | Identificador IATI de su organización | Texto | Sí | `XM-DAC-12345` |
| Nombre de la Organización | Nombre de su organización | Texto | Sí | "Banco Centroamericano de Integración Económica" |
| Tipo de Organización | Tipo de organización | [Código OrganisationType de IATI](https://iatistandard.org/en/iati-standard/203/codelists/organisationtype/) (10=Gobierno, 40=Multilateral, etc.) | Sí | 40 (Multilateral) |

#### 3.2. Organizaciones Participantes

Para cada organización que participa en la actividad, proporcione:

| Campo | Descripción | Formato | Requerido | Ejemplo |
|-------|-------------|---------|-----------|---------|
| Nombre de la Organización | Nombre de la organización participante | Texto | Sí | "Ministerio de Finanzas, Honduras" |
| ID de la Organización | Identificador IATI de la organización (si se conoce) | Texto | Si está disponible | `XM-DAC-HN-MOF` |
| Rol de la Organización | Rol en la actividad | [Código OrganisationRole de IATI](https://iatistandard.org/en/iati-standard/203/codelists/organisationrole/) (1=Financiador, 4=Implementador, etc.) | Sí | 4 (Implementador) |
| Tipo de Organización | Tipo de organización | [Código OrganisationType de IATI](https://iatistandard.org/en/iati-standard/203/codelists/organisationtype/) | Sí | 10 (Gobierno) |

### 4. Ubicación Geográfica

#### 4.1. País/Región Receptor

| Campo | Descripción | Formato | Requerido | Ejemplo |
|-------|-------------|---------|-----------|---------|
| País Receptor | País donde se realiza la actividad | [Código ISO 3166-1 alfa-2](https://iatistandard.org/en/iati-standard/203/codelists/country/) | Sí (si no hay región) | HN (para Honduras) |
| Porcentaje | Porcentaje de la actividad en este país | Número (0-100) | Si hay múltiples países | 100 |

O

| Campo | Descripción | Formato | Requerido | Ejemplo |
|-------|-------------|---------|-----------|---------|
| Región Receptora | Región donde se realiza la actividad | [Código de región IATI](https://iatistandard.org/en/iati-standard/203/codelists/region/) | Sí (si no hay país) | 298 (para Centroamérica) |
| Porcentaje | Porcentaje de la actividad en esta región | Número (0-100) | Si hay múltiples regiones | 100 |

#### 4.2. Ubicaciones Específicas (si aplica)

Para cada ubicación específica dentro del país:

| Campo | Descripción | Formato | Requerido | Ejemplo |
|-------|-------------|---------|-----------|---------|
| Nombre de la Ubicación | Nombre de la ubicación específica | Texto | Sí | "Tegucigalpa" |
| Descripción de la Ubicación | Breve descripción de esta ubicación | Texto | No | "Área de la ciudad capital" |
| Coordenadas | Coordenadas geográficas | Latitud,Longitud | Si está disponible | "14.0723,-87.1921" |
| Tipo de Ubicación | Tipo de ubicación | [Código LocationType de IATI](https://iatistandard.org/en/iati-standard/203/codelists/locationtype/) | Si está disponible | 2 (Lugar Poblado) |

### 5. Sectores

Para cada sector que aborda la actividad:

| Campo | Descripción | Formato | Requerido | Ejemplo |
|-------|-------------|---------|-----------|---------|
| Código del Sector | Código que representa el sector | [Código de propósito OCDE DAC de 5 dígitos](https://iatistandard.org/en/iati-standard/203/codelists/sector/) | Sí | 11110 (Política Educativa) |
| Nombre del Sector | Nombre del sector | Texto | Sí | "Política Educativa y Gestión Administrativa" |
| Porcentaje | Porcentaje de la actividad enfocada en este sector | Número (0-100) | Si hay múltiples sectores | 60 |

### 6. Información Financiera

#### 6.1. Presupuestos

Para cada período presupuestario:

| Campo | Descripción | Formato | Requerido | Ejemplo |
|-------|-------------|---------|-----------|---------|
| Tipo de Presupuesto | Tipo de presupuesto | [Código BudgetType de IATI](https://iatistandard.org/en/iati-standard/203/codelists/budgettype/) (1=Original, 2=Revisado) | Sí | 1 (Original) |
| Estado | Estado del presupuesto | [Código BudgetStatus de IATI](https://iatistandard.org/en/iati-standard/203/codelists/budgetstatus/) (1=Indicativo, 2=Comprometido) | Sí | 2 (Comprometido) |
| Inicio del Período | Inicio del período presupuestario | AAAA-MM-DD | Sí | 2023-01-01 |
| Fin del Período | Fin del período presupuestario | AAAA-MM-DD | Sí | 2023-12-31 |
| Monto | Valor del presupuesto | Número | Sí | 1500000 |
| Moneda | Moneda del presupuesto | [Código ISO 4217 de 3 letras](https://iatistandard.org/en/iati-standard/203/codelists/currency/) | Sí | USD |
| Fecha de Valor | Fecha de tipo de cambio | AAAA-MM-DD | Sí | 2023-01-01 |

#### 6.2. Transacciones

Para cada transacción financiera:

| Campo | Descripción | Formato | Requerido | Ejemplo |
|-------|-------------|---------|-----------|---------|
| Tipo de Transacción | Tipo de transacción | [Código TransactionType de IATI](https://iatistandard.org/en/iati-standard/203/codelists/transactiontype/) | Sí | 3 (Desembolso) |
| Fecha de Transacción | Fecha de la transacción | AAAA-MM-DD | Sí | 2023-03-15 |
| Monto | Monto de la transacción | Número | Sí | 500000 |
| Moneda | Moneda de la transacción | [Código ISO 4217 de 3 letras](https://iatistandard.org/en/iati-standard/203/codelists/currency/) | Sí | USD |
| Fecha de Valor | Fecha de tipo de cambio | AAAA-MM-DD | Sí | 2023-03-15 |
| Organización Proveedora | Organización que proporciona los fondos | Texto | Para fondos entrantes | "Banco Mundial" |
| Organización Receptora | Organización que recibe los fondos | Texto | Para fondos salientes | "Ministerio de Educación, Honduras" |
| Tipo de Financiación | Tipo de financiación | [Código FinanceType de IATI](https://iatistandard.org/en/iati-standard/203/codelists/financetype/) | Si está disponible | 110 (Subvención Estándar) |
| Tipo de Flujo | Tipo de flujo | [Código FlowType de IATI](https://iatistandard.org/en/iati-standard/203/codelists/flowtype/) | Si está disponible | 10 (ODA) |

### 7. Resultados (si están disponibles)

Para cada resultado que se está rastreando:

| Campo | Descripción | Formato | Requerido | Ejemplo |
|-------|-------------|---------|-----------|---------|
| Tipo de Resultado | Tipo de resultado | [Código ResultType de IATI](https://iatistandard.org/en/iati-standard/203/codelists/resulttype/) (1=Producto, 2=Efecto, etc.) | Sí | 2 (Efecto) |
| Título del Resultado | Título del resultado | Texto | Sí | "Mayor acceso a la educación" |
| Descripción del Resultado | Descripción del resultado | Texto | Sí | "Medida del aumento de la matrícula escolar en áreas objetivo" |
| Título del Indicador | Título del indicador | Texto | Sí | "Tasa de matriculación escolar" |
| Descripción del Indicador | Descripción del indicador | Texto | Sí | "Porcentaje de niños en edad escolar matriculados" |
| Medida del Indicador | Tipo de medición | [Código IndicatorMeasure de IATI](https://iatistandard.org/en/iati-standard/203/codelists/indicatormeasure/) | Sí | 2 (Porcentaje) |
| Año de Referencia | Año de los datos de referencia | AAAA | Si está disponible | 2022 |
| Valor de Referencia | Valor de referencia | Número o Texto | Si está disponible | "45%" |
| Año Objetivo | Año del objetivo | AAAA | Si está disponible | 2024 |
| Valor Objetivo | Valor objetivo | Número o Texto | Si está disponible | "60%" |
| Año Real | Año del resultado real | AAAA | Si está disponible | 2023 |
| Valor Real | Valor real alcanzado | Número o Texto | Si está disponible | "52%" |

### 8. Documentos

Para cada documento relacionado con la actividad:

| Campo | Descripción | Formato | Requerido | Ejemplo |
|-------|-------------|---------|-----------|---------|
| Título del Documento | Título del documento | Texto | Sí | "Propuesta de Proyecto" |
| URL del Documento | Dirección web del documento | URL | Sí | "https://ejemplo.org/docs/propuesta.pdf" |
| Formato del Documento | Formato del documento | Tipo MIME | Sí | "application/pdf" |
| Categoría del Documento | Tipo de documento | [Código DocumentCategory de IATI](https://iatistandard.org/en/iati-standard/203/codelists/documentcategory/) | Sí | A02 (Objetivos) |

## Marcadores de Política (si aplican)

Para cada marcador de política que aplique a la actividad:

| Campo | Descripción | Formato | Requerido | Ejemplo |
|-------|-------------|---------|-----------|---------|
| Marcador de Política | Tipo de política | [Código PolicyMarker de IATI](https://iatistandard.org/en/iati-standard/203/codelists/policymarker/) | Sí | 1 (Igualdad de Género) |
| Significancia | Grado de enfoque | [Código PolicySignificance de IATI](https://iatistandard.org/en/iati-standard/203/codelists/policysignificance/) | Sí | 1 (Objetivo Significativo) |

## Notas de Validación de Datos

1. **Identificadores de Actividad**: Deben comenzar con el identificador de su organización seguido de un guión y un código único.
2. **Fechas**: Todas las fechas deben estar en formato AAAA-MM-DD.
3. **Porcentajes**: Cuando se enumeran múltiples países, regiones o sectores, los porcentajes deben sumar 100%.
4. **Moneda**: Use códigos estándar ISO de 3 letras para las monedas (USD, EUR, GBP, etc.).
5. **Códigos de País**: Use códigos ISO estándar de 2 letras (HN, SV, GT, NI, CR, PA, etc.).
6. **Códigos de Sector**: Use los códigos de propósito OCDE DAC de 5 dígitos.
7. **Valores de Listas de Códigos**: Todos los campos con listas de códigos específicas deben usar los valores exactos de código de las listas enlazadas del estándar IATI.

## Información Adicional Necesaria

Si dispone de cualquiera de la siguiente información, por favor inclúyala:

1. **Moneda Predeterminada**: La moneda principal utilizada para la actividad (use [código ISO 4217](https://iatistandard.org/en/iati-standard/203/codelists/currency/))
2. **Indicador Humanitario**: Si la actividad es de naturaleza humanitaria (Sí/No)
3. **Actividades Relacionadas**: Si esta actividad está relacionada con otras actividades que informa (especifique [código RelatedActivityType](https://iatistandard.org/en/iati-standard/203/codelists/relatedactivitytype/))
4. **Tipo de Colaboración**: Tipo de colaboración (use [código CollaborationType](https://iatistandard.org/en/iati-standard/203/codelists/collaborationtype/))
5. **Tipo de Ayuda**: Tipo de ayuda (use [código AidType](https://iatistandard.org/en/iati-standard/203/codelists/aidtype/))

## ¿Preguntas?

Si tiene dudas sobre cualquier campo de datos o necesita aclaración sobre los requisitos de formato, contacte a nuestro equipo en [su-correo@ejemplo.com].

## Próximos Pasos

1. Compile sus datos en un archivo CSV o Excel siguiendo la estructura anterior
2. Incluya una fila por actividad con columnas que coincidan con los campos descritos
3. Envíenos su archivo completado antes de [fecha límite]
4. Nuestro equipo validará los datos y los convertirá al formato XML IATI
5. Compartiremos el archivo IATI generado con usted para su revisión antes de la publicación
