stdargs @ { scm, ... }:

scm.revision {
    guid = "R001D0FMHJ180QR1";
    name = "2022-08-10-alembic_version";
    upgrade_sql = ./upgrade.sql;
    dependencies = [
        
    ];
}
