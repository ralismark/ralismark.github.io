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

        node_modules =
          let
            packageJsons = pkgs.importNpmLock {
              package = builtins.fromJSON (builtins.readFile ./package.json);
              packageLock = builtins.fromJSON (builtins.readFile ./package-lock.json);
            };
          in
            pkgs.runCommand "node_modules" {
              nativeBuildInputs = [ pkgs.nodejs ];
            } ''
              # npm expects ~ to be writeable
              export HOME=$PWD/.home

              cp ${packageJsons}/* .
              npm ci
              cp -r node_modules $out
            '';

        devshell = { ci }: pkgs.mkShellNoCC {
          packages = [
            pkgs.nodejs
            pkgs.graphviz
            pkgs.nodePackages.katex
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
          ];

          shellHook = builtins.concatStringsSep "\n" [
            # python setup
            ''
              export PYTHONPATH=$PWD
            ''

            # npm setup
            (if ci
              then ''
                ln -s ${node_modules} node_modules
              ''
              else ''
                [ -e node_modules ] || npm ci
              '')
            ''
              PATH=$PWD/node_modules/.bin:$PATH
            ''

            # misc
            ''
              PATH=$PWD/bin:$PATH
            ''
          ];
        };
      in
      {
        devShells.default = devshell { ci = false; };
        devShells.ci = devshell { ci = true; };
      });
}
