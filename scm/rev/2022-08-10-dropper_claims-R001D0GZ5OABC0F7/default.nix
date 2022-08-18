stdargs @ { scm, ... }:

scm.revision {
    guid = "R001D0GZ5OABC0F7";
    name = "2022-08-10-dropper_claims";
    upgrade_sql = ./upgrade.sql;
    dependencies = [
        <2022-08-10-dropper_contracts-R001D0GSBN4S9BXO>
    ];
}
