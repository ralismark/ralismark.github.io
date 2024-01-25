{
  description = "ralismark.xyz";

  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs/nixpkgs-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = import nixpkgs { inherit system; };
      in
      rec {
        packages.default = pkgs.stdenv.mkDerivation {
          pname = "heron";
          version = "0.1.0";
          src = ./.;
          site = ./site;

          buildInputs = [
            pkgs.graphviz
            pkgs.nodePackages.katex
            (pkgs.python3.withPackages (p: with p; [
              frozendict
              graphviz
              jinja2
              libsass
              mistune
              pygments
              pyyaml
              requests
              watchdog
            ]))
          ];

          buildPhase = ''
            PYTHONPATH=.
            python -m heron build -o $out $site/main.py
          '';

          shellHook = ''
            export PYTHONPATH=.:
          '';
        };

        apps.default = {
          type = "app";
          program = builtins.toString (pkgs.writeScript "heron" ''
            #!/bin/sh
            export PATH=${pkgs.lib.makeBinPath packages.default.buildInputs}:$PATH
            export PYTHONPATH=.
            exec python -m heron "$@"
          '');
        };

      });
}
