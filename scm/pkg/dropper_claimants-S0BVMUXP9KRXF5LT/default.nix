stdargs @ { scm, ... }:

scm.schema {
    guid = "S0BVMUXP9KRXF5LT";
    name = "dropper_claimants";
    upgrade_sql = ./upgrade.sql;
    dependencies = [
        <dropper_claims-S05BV02LO7UDRPR2>
        <2022-08-10-dropper_claimants-R001D0GZYFRRNR8X>
    ];
}
