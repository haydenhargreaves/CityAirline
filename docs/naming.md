# Naming Convention

This document outlines the naming convention for this project.

### Tables

**Plural Nouns**

The statement "select lots of planes from plane" feels wrong. We will use plural nouns
since the database will store many of each entity.

>
> Airlines, Planes, Seats, etc
>

### Columns

**snake_case**

Due to the casing differences in Windows and Linux environments, to maintain safety and reduce 
confusion, we will use snake_case.

>
> airline_id, name, sold_at, etc
>

### Primary Keys

**id**

Saves space and keystrokes, and it does not reduce readability. When you select an ID from a table,
it is that table's ID. Furthermore, when many IDs are used in the same query, that implies joins,
which usually means aliasing, so the ID is preceded by the alias.

>
> id
>

### Foreign Keys

**reference_id**

This is a case where it makes sense to provide the referenced entities name before the ID. In cases
where there are more than one reference to the same table, the FK should be named to reflect the purpose
of the column. Snake case should be used, like in all columns.

>
> airline_id, seat_id, source_airport_id, etc
>



