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
          derivationArgs = {
            preferLocalBuild = true;
          };
        };
        # create node_modules such that it can work with regular npm-install
        node_modules = pkgs.runCommandLocal "node_modules" {} ''
          mkdir $out

          for f in ${npmDeps}/node_modules/*; do
            echo "$f"
            basename=$(basename "$f")
            case "$basename" in
              @*) # scoped package of the form @scope/pkg
                mkdir "$out/$basename"
                for scoped_pkg in "$f"/*; do
                  ln -s "$scoped_pkg" -t "$out/$basename"
                done
                ;;

              *) # unscoped package
                ln -s "$f" -t $out
                ;;
            esac
          done

          # miscellaneous bits
          cp -r ${npmDeps}/node_modules/.* -t $out
        '';

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
            ''
              rm -rf node_modules
              cp -r --no-preserve=all ${node_modules} node_modules
              chmod +w -R node_modules

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
