stdargs @ { scm, ... }:

scm.revision {
    guid = "R001CXUIG6BPK5T6";
    name = "2022-08-09-config";
    basefiles = ./basefiles;
    upgrade_sql = ./upgrade.sql;
    dependencies = [
        
    ];
}
