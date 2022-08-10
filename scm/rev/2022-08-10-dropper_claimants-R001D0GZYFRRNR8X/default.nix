stdargs @ { scm, ... }:

scm.revision {
    guid = "R001D0GZYFRRNR8X";
    name = "2022-08-10-dropper_claimants";
    upgrade_sql = ./upgrade.sql;
    dependencies = [
        <2022-08-10-dropper_claims-R001D0GZ5OABC0F7>
    ];
}
