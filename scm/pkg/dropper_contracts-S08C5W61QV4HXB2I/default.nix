stdargs @ { scm, ... }:

scm.schema {
    guid = "S08C5W61QV4HXB2I";
    name = "dropper_contracts";
    upgrade_sql = ./upgrade.sql;
    dependencies = [
        <2022-08-10-dropper_contracts-R001D0GSBN4S9BXO>
    ];
}
