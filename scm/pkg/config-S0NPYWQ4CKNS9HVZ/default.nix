stdargs @ { scm, ... }:

scm.schema {
    guid = "S0NPYWQ4CKNS9HVZ";
    name = "config";
    upgrade_sql = ./upgrade.sql;
    basefiles = ./basefiles;
    dependencies = [
        <2022-08-09-config-R001CXUIG6BPK5T6>
    ];
}

