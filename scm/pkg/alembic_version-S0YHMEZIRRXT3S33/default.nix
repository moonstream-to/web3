stdargs @ { scm, ... }:

scm.schema {
    guid = "S0YHMEZIRRXT3S33";
    name = "alembic_version";
    upgrade_sql = ./upgrade.sql;
    dependencies = [
        <2022-08-10-alembic_version-R001D0FMHJ180QR1>
    ];
}
