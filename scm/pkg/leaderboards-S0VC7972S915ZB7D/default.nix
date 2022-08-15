stdargs @ { scm, ... }:

scm.schema {
    guid = "S0VC7972S915ZB7D";
    name = "leaderboards";
    upgrade_sql = ./upgrade.sql;
    dependencies = [
        <2022-08-10-leaderboards-R001D0GTJ5SV7Q84>
    ];
}
