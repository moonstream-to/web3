stdargs @ { scm, ... }:

scm.schema {
    guid = "S0IXH3C5Q83VYMJY";
    name = "leaderboard_scores";
    upgrade_sql = ./upgrade.sql;
    dependencies = [
        <leaderboards-S0VC7972S915ZB7D>
        <2022-08-10-leaderboard_scores-R001D0GUCF7IER1O>
    ];
}
