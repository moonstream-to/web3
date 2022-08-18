stdargs @ { scm, ... }:

scm.revision {
    guid = "R001D0GUCF7IER1O";
    name = "2022-08-10-leaderboard_scores";
    upgrade_sql = ./upgrade.sql;
    dependencies = [
        <2022-08-10-leaderboards-R001D0GTJ5SV7Q84>
    ];
}
