# PostgreSQL + PostGIS

**What it is.** PostgreSQL is the open-source relational database. PostGIS is its spatial
extension: geometry/geography types, spatial indexes and hundreds of `ST_*` functions
(distance, intersection, buffering, coordinate transforms).

**Why here.** The app needs "which district is this point in?", "how far is the nearest
substation / mandi / CBG buyer?" and district polygons for the map. PostGIS does these in SQL,
next to the rest of the data, and every managed Postgres offers it.

## Concepts that matter

1. **Extension.** `create extension postgis;` per database. The image does it for
   `$POSTGRES_DB`; `db/init/20_project.sql` makes it explicit.
2. **`geometry` vs `geography`.** Geometry is planar maths in the units of its coordinate
   system; geography is on the spheroid, with distances in metres. For UP-scale distances, use
   geography, or geometry in a metric projection (UTM 44N, EPSG:32644).
3. **SRID** = coordinate reference system ID. GPS lon/lat is **EPSG:4326**. Mixing SRIDs
   errors or gives nonsense. `ST_SetSRID` labels; `ST_Transform` converts.
4. **Axis order: longitude first.** `ST_MakePoint(lon, lat)`. Swapping them is the #1 bug;
   the smoke test's Lucknow–Kanpur distance (≈75 km) would come out very differently.
5. **Spatial index (GiST).** `create index on t using gist (geom);` makes `ST_DWithin` /
   `ST_Intersects` fast. Prefer `ST_DWithin(a, b, d)` to `ST_Distance(a, b) < d`, because
   only the former uses the index.
6. **Schemas** (`raw`, `staging`, `marts`) are namespaces within one database, created by
   loaders and dbt later. Phase 0 creates none.
7. **Portability.** Spatial SQL lives only in `dbt/models/intermediate/spatial/` and
   `dbt/macros/spatial/` (see portability.md).

## Commands you'll run

```bash
make db-up            # start + smoke test
make db-psql          # then, inside psql:
```
```sql
\dx                                   -- installed extensions
\dn                                   -- schemas
select postgis_full_version();
select st_astext(st_setsrid(st_makepoint(80.9462, 26.8467), 4326));   -- Lucknow
```

## Common mistakes

- `ST_MakePoint(lat, lon)`.
- Measuring distance in degrees (geometry in 4326) and reading it as km.
- Forgetting the spatial index, then wondering why a join takes minutes.
- `x::geography` casts in models. Write `cast(x as geography)` (portability rule 2).

## Interview questions

- *Geometry vs geography: which would you use for "plants within 50 km of a sugar mill" in UP, and why?*
- *How does a GiST index speed up a spatial join?* (It indexes bounding boxes in an R-tree-like
  structure; the box test prunes candidates before the exact geometry test.)
