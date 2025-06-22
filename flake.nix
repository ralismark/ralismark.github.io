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

        deps = [
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
        ];
      in
      rec {
        packages.heron = pkgs.writeShellApplication {
          name = "heron";
          runtimeInputs = deps;

          text = ''
            export PYTHONPATH=''${HERONPATH-.}''${PYTHONPATH:+:}''${PYTHONPATH-}
            exec python -m heron "$@"
          '';
        };

        apps.default = {
          type = "app";
          program = pkgs.lib.getExe packages.heron;
        };

        devShells.default = pkgs.mkShell {
          buildInputs = deps;

          shellHook = ''
            export PYTHONPATH=$PWD
            PATH=$PWD/node_modules/.bin:$PATH
          '';
        };

      });
}
