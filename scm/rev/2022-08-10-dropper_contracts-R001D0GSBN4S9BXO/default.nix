stdargs @ { scm, ... }:

scm.revision {
    guid = "R001D0GSBN4S9BXO";
    name = "2022-08-10-dropper_contracts";
    upgrade_sql = ./upgrade.sql;
    dependencies = [
        
    ];
}
