{
  description = "ralismark.xyz";

  inputs = {
    nixpkgs.url = "nixpkgs";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = import nixpkgs { inherit system; };

        npmDeps = pkgs.importNpmLock.buildNodeModules {
          nodejs = pkgs.nodejs;
          package = builtins.fromJSON (builtins.readFile ./package.json);
          packageLock = builtins.fromJSON (builtins.readFile ./package-lock.json);
        };

        devshell = { ci }: pkgs.mkShellNoCC {
          packages = [
            pkgs.nodejs
            pkgs.graphviz
            (pkgs.python3.withPackages (p: with p; [
              frozendict
              jinja2
              libsass
              mistune
              pygments
              pyyaml
              requests
              watchdog
            ]))

            (pkgs.writeScriptBin "heron" ''
              #!/bin/sh
              exec python3 -m heron "$@"
            '')

            pkgs.importNpmLock.hooks.linkNodeModulesHook
          ];

          shellHook = builtins.concatStringsSep "\n" [
            # python setup
            ''
              export PYTHONPATH=$PWD
            ''

            # npm setup
            (if ci
              then ''
                rm -rf node_modules
                mkdir node_modules
                ln -s ${npmDeps}/node_modules/* ${npmDeps}/node_modules/.* -t node_modules/
              ''
              else ''
                [ -e node_modules ] || npm ci
              '')
            ''
              PATH=$PWD/node_modules/.bin:$PATH
            ''

            # misc
            ''
              PATH=$PWD/tools:$PATH
            ''
          ];
        };
      in
      {
        devShells.default = devshell { ci = false; };
        devShells.ci = devshell { ci = true; };
      });
}
