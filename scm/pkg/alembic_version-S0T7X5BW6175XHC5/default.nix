stdargs @ { scm, ... }:

scm.schema {
    guid = "S0T7X5BW6175XHC5";
    name = "alembic_version";
    upgrade_sql = ./upgrade.sql;
    dependencies = [
        <2022-08-11-alembic_version-R001D1KR4WR2RMUS>
    ];
}
