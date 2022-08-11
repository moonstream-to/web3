stdargs @ { scm, ... }:

scm.revision {
    guid = "R001D1KR4WR2RMUS";
    name = "2022-08-11-alembic_version";
    upgrade_sql = ./upgrade.sql;
    dependencies = [
        
    ];
}
