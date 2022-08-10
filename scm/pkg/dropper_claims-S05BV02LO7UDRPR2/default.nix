stdargs @ { scm, ... }:

scm.schema {
    guid = "S05BV02LO7UDRPR2";
    name = "dropper_claims";
    upgrade_sql = ./upgrade.sql;
    dependencies = [
        <dropper_contracts-S08C5W61QV4HXB2I>
        <2022-08-10-dropper_claims-R001D0GZ5OABC0F7>
    ];
}
