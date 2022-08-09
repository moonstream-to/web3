with builtins;
let
    scm_repos = [
        (getEnv "SCM_GIT")
        (fetchGit {
            url = "git@gitlab.com:deltaex/schematic.git";
            rev = "ba5d7b40255e5da9a74e666dd88e309dae40fbd2";
        })
    ];
    scm_repo = head (filter (x: x != "") scm_repos);
    scm = (import scm_repo {
        verbose = true;
        repos = [
            "."
            (getEnv "MDP_GIT")
            (fetchGit {
                url = "git@github.com:bugout-dev/engine.git";
                rev = "6dc9adcdf7119f2a09a44896c73602201bf60d34";
            })
        ] ++ scm_repos;
    });
in rec {
    schematic = scm.shell.overrideAttrs ( oldAttrs : {
        shellHook = oldAttrs.shellHook + ''
            [ -n "$ENV" -a "$ENV" != "dev" ] && export BUGSNAG=2b987ca13cd93a4931bb746aace204fb
        '';
    });
}
